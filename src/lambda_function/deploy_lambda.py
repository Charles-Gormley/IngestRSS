import boto3
import os
import zipfile
import io
from botocore.exceptions import ClientError
from src.utils.retry_logic import retry_with_backoff

# Set variables
LAMBDA_NAME = "RSSFeedProcessor"
LAMBDA_HANDLER = "lambda_function.lambda_handler"
ACCOUNT_NUM = os.getenv('AWS_ACCOUNT_ID')
LAMBDA_ROLE_NAME = os.getenv('LAMBDA_EXECUTION_ROLE_NAME')
LAMBDA_ROLE_ARN = f"arn:aws:iam::{ACCOUNT_NUM}:role/{LAMBDA_ROLE_NAME}"
LAMBDA_TIMEOUT = 300
LAMBDA_MEMORY = 256
LAMBDA_RUNTIME = "python3.10"

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
def update_function_configuration(lambda_client, function_name, handler, role, timeout, memory):
    return lambda_client.update_function_configuration(
        FunctionName=function_name,
        Handler=handler,
        Role=role,
        Timeout=timeout,
        MemorySize=memory
    )

@retry_with_backoff()
def create_function(lambda_client, function_name, runtime, role, handler, zip_file, timeout, memory):
    return lambda_client.create_function(
        FunctionName=function_name,
        Runtime=runtime,
        Role=role,
        Handler=handler,
        Code={'ZipFile': zip_file},
        Timeout=timeout,
        MemorySize=memory
    )

def deploy_lambda():
    lambda_client = boto3.client('lambda')

    print(f"Starting deployment of Lambda function: {LAMBDA_NAME}")
    deployment_package = zip_directory('src/lambda_function/src')

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

        if function_exists:
            print("Updating existing Lambda function...")
            update_function_code(lambda_client, LAMBDA_NAME, deployment_package)
            update_function_configuration(lambda_client, LAMBDA_NAME, LAMBDA_HANDLER, LAMBDA_ROLE_ARN, LAMBDA_TIMEOUT, LAMBDA_MEMORY)
        else:
            print(f"Lambda function '{LAMBDA_NAME}' not found. Creating new function...")
            create_function(lambda_client, LAMBDA_NAME, LAMBDA_RUNTIME, LAMBDA_ROLE_ARN, LAMBDA_HANDLER, deployment_package, LAMBDA_TIMEOUT, LAMBDA_MEMORY)

        print("Lambda deployment completed successfully!")

    except Exception as e:
        print(f"Error during Lambda deployment: {str(e)}")
        raise

if __name__ == "__main__":
    deploy_lambda()