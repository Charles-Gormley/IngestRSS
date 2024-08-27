import boto3
import os
import zipfile
import io
import requests
import json
from botocore.exceptions import ClientError
from src.utils.retry_logic import retry_with_backoff
import time
import sys
from src.infra.deploy_infrastructure import get_or_create_kms_key

# Set variables
LAMBDA_NAME = "RSSFeedProcessor"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
ACCOUNT_NUM = os.getenv('AWS_ACCOUNT_ID')
LAMBDA_ROLE_NAME = os.getenv('LAMBDA_EXECUTION_ROLE_NAME')
LAMBDA_ROLE_ARN = f"arn:aws:iam::{ACCOUNT_NUM}:role/{LAMBDA_ROLE_NAME}"
LAMBDA_TIMEOUT = 300
LAMBDA_MEMORY = 256
LAMBDA_RUNTIME = "python3.11"
LAMBDA_STACK_NAME = "rss-feed-processor-Lambda"
LAMBDA_LAYER_NAME = "RSSFeedProcessorLayer"
S3_LAYER_BUCKET_NAME = os.getenv('S3_LAYER_BUCKET_NAME')
S3_LAYER_KEY = os.getenv('S3_LAYER_KEY_NAME')+'.zip'

def zip_directory(path):
    print(f"Creating deployment package from {path}...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zip_file.write(file_path, arcname)
    return zip_buffer.getvalue()

@retry_with_backoff()
def update_function_code(lambda_client, function_name, zip_file):
    return lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_file
    )

@retry_with_backoff()
def get_or_create_lambda_layer():
    layer_arn = 'arn:aws:lambda:us-east-1:966265353179:layer:OpenRSSLambdaLayer:3'
    
    return layer_arn
    

def wait_for_function_update_to_complete(lambda_client, function_name, max_attempts=30, delay=10):
    for attempt in range(max_attempts):
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            state = response['Configuration']['State']
            if state == 'Active':
                return True
            elif state == 'Failed':
                print(f"Function update failed: {response['Configuration'].get('StateReason')}")
                return False
            print(f"Function {function_name} is in {state} state. Waiting...")
        except ClientError as e:
            print(f"Error checking function state: {e}")
            return False
        time.sleep(delay)
    print(f"Timeout waiting for function {function_name} to become active.")
    return False

@retry_with_backoff()
def update_function_configuration(lambda_client, function_name, handler, role, timeout, memory, layers, kms_key_id):
    # First, wait for any ongoing updates to complete
    if not wait_for_function_update_to_complete(lambda_client, function_name):
        raise Exception(f"Function {function_name} is not in a state to be updated.")

    config = {
        'FunctionName': function_name,
        'Handler': handler,
        'Role': role,
        'Timeout': timeout,
        'MemorySize': memory,
        'Layers': layers
    }
    
    if kms_key_id:
        config['KMSKeyArn'] = f"arn:aws:kms:{os.environ['AWS_REGION']}:{ACCOUNT_NUM}:key/{kms_key_id}"
    
    print(f"Updating function configuration for {function_name}... with {config}")
    
    max_retries = 5 # TODO: Get rid of this dumb retry logic and just use the wrapper I created.
    for attempt in range(max_retries):
        try:
            response = lambda_client.update_function_configuration(**config)
            print(f"Update request sent successfully for {function_name}.")
            
            # Wait for the update to complete
            if wait_for_function_update_to_complete(lambda_client, function_name):
                print(f"Function {function_name} updated successfully.")
                return response
            else:
                print(f"Function {function_name} update may not have completed successfully.")
                if attempt < max_retries - 1:
                    print(f"Retrying in 30 seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(30)
                else:
                    raise Exception(f"Failed to update function {function_name} after {max_retries} attempts.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                if attempt < max_retries - 1:
                    print(f"Another operation is in progress for {function_name}. Retrying in 30 seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(30)
                else:
                    raise Exception(f"Failed to update function {function_name} after {max_retries} attempts due to ongoing operations.")
            elif 'The role defined for the function cannot be assumed by Lambda' in str(e):
                if attempt < max_retries - 1:
                    print(f"IAM role not ready. Retrying in 30 seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(30)
                else:
                    raise Exception(f"Failed to update function {function_name} after {max_retries} attempts. IAM role could not be assumed by Lambda.")
            else:
                print(f"Error updating function configuration: {e}")
                raise
    
    raise Exception(f"Failed to update function {function_name} after {max_retries} attempts.")

@retry_with_backoff()
def create_function(lambda_client, function_name, runtime, role, handler, zip_file, timeout, memory, layers, kms_key_id):
    config = {
        'FunctionName': function_name,
        'Runtime': runtime,
        'Role': role,
        'Handler': handler,
        'Code': {'ZipFile': zip_file},
        'Timeout': timeout,
        'MemorySize': memory,
        'Layers': layers
    }
    
    if kms_key_id:
        config['KMSKeyArn'] = f"arn:aws:kms:{os.environ['AWS_DEFAULT_REGION']}:{ACCOUNT_NUM}:key/{kms_key_id}"
    
    return lambda_client.create_function(**config)

def get_pillow_layer_arn():
    url = "https://api.klayers.cloud/api/v2/p3.11/layers/latest/us-east-1/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        layers_data = response.json()
        
        pillow_layer = next((layer for layer in layers_data if layer['package'] == 'Pillow'), None)
        
        if pillow_layer:
            return pillow_layer['arn']
        else:
            print("Pillow layer not found in the API response.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching Pillow layer ARN: {e}")
        return None

def deploy_lambda():
    lambda_client = boto3.client('lambda')

    print(f"Starting deployment of Lambda function: {LAMBDA_NAME}")
    deployment_package = zip_directory('src/lambda_function/src')

    layer_arn = get_or_create_lambda_layer()
    if layer_arn:
        print(f"Using Lambda Layer ARN: {layer_arn}")
    else:
        print("Warning: Lambda Layer not found or created. Proceeding without Layer.")

    pillow_layer_arn = get_pillow_layer_arn()
    if pillow_layer_arn:
        print(f"Using Pillow Layer ARN: {pillow_layer_arn}")
    else:
        print("Warning: Pillow Layer not found. Proceeding without Pillow Layer.")

    kms_key_id = get_or_create_kms_key()
    if kms_key_id:
        print(f"Using KMS Key ID: {kms_key_id}")
    else:
        print("Warning: KMS Key not found or created. Proceeding without KMS Key.")
        sys.exit(1)

    try:
        # Check if the function exists
        try:
            lambda_client.get_function(FunctionName=LAMBDA_NAME)
            function_exists = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                function_exists = False
            else:
                raise e

        # Combine the layers
        layers = [layer_arn] if layer_arn else []
        if pillow_layer_arn:
            layers.append(pillow_layer_arn)

        if function_exists:
            print("Updating existing Lambda function...")
            update_function_configuration(lambda_client, LAMBDA_NAME, LAMBDA_HANDLER, LAMBDA_ROLE_ARN, LAMBDA_TIMEOUT, LAMBDA_MEMORY, layers, kms_key_id)
            update_function_code(lambda_client, LAMBDA_NAME, deployment_package)
        else:
            print(f"Lambda function '{LAMBDA_NAME}' not found. Creating new function...")
            create_function(lambda_client, LAMBDA_NAME, LAMBDA_RUNTIME, LAMBDA_ROLE_ARN, LAMBDA_HANDLER, deployment_package, LAMBDA_TIMEOUT, LAMBDA_MEMORY, layers, kms_key_id)

        print("Lambda deployment completed successfully!")

    except Exception as e:
        print(f"Error during Lambda deployment: {str(e)}")
        raise

if __name__ == "__main__":
    deploy_lambda()