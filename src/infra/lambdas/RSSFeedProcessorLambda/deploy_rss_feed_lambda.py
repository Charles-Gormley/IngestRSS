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

import logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))

# Set variables

LAMBDA_NAME = os.getenv('LAMBDA_FUNCTION_NAME')

ACCOUNT_NUM = os.getenv('AWS_ACCOUNT_ID')
LAMBDA_ROLE_ARN = os.getenv("LAMBDA_ROLE_ARN")
LAMBDA_TIMEOUT = int(os.getenv('LAMBDA_TIMEOUT'))
LAMBDA_MEMORY = int(os.getenv('LAMBDA_MEMORY'))
LAMBDA_RUNTIME = os.getenv('LAMBDA_RUNTIME')
S3_LAYER_BUCKET_NAME = os.getenv('S3_LAYER_BUCKET_NAME')
LAMBDA_STACK_NAME = os.getenv("STACK_BASE") + f"-{LAMBDA_NAME}"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
LAMBDA_LAYER_NAME = LAMBDA_NAME + "Layer"
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

def get_or_create_lambda_layer():
    layer_arn = os.getenv('LAMBDA_LAYER_ARN')
    
    return layer_arn

@retry_with_backoff(max_retries=50, initial_backoff=5, backoff_multiplier=2) # Note: This function usually takes a long time to be successful. 
def update_function_configuration(lambda_client, function_name, handler, role, timeout, memory, layers, kms_key_id):

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
    

        try:
            response = lambda_client.update_function_configuration(**config)
            print(f"Update request sent successfully for {function_name}.")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                logging.info(f"Function {function_name} is currently being updated. Retrying...")
                raise e


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
    deployment_package = zip_directory('src/infra/lambdas/RSSFeedProcessorLambda/src')

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