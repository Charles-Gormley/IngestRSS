import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up AWS clients
sqs = boto3.client('sqs')
lambda_client = boto3.client('lambda')

# Get environment variables
region = os.getenv("AWS_REGION")
account_id = os.getenv("AWS_ACCOUNT_ID")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")

def get_or_create_sqs_queue():
    try:
        # Try to get the queue URL first
        response = sqs.get_queue_url(QueueName=SQS_QUEUE_NAME)
        queue_url = response['QueueUrl']
        print(f"SQS queue already exists. URL: {queue_url}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            # Queue doesn't exist, so create it
            try:
                response = sqs.create_queue(QueueName=SQS_QUEUE_NAME)
                queue_url = response['QueueUrl']
                print(f"SQS queue created. URL: {queue_url}")
            except ClientError as create_error:
                print(f"Error creating SQS queue: {create_error}")
                return None
        else:
            print(f"Error getting SQS queue: {e}")
            return None
    return queue_url

def configure_lambda_trigger(function_name, queue_url):
    try:
        # Get the SQS queue ARN
        queue_attributes = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['QueueArn']
        )
        queue_arn = queue_attributes['Attributes']['QueueArn']

        # Check if Lambda function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Lambda function '{function_name}' does not exist. Please create it first.")
                return
            else:
                raise

        # Add the SQS queue as an event source for the Lambda function
        response = lambda_client.create_event_source_mapping(
            EventSourceArn=queue_arn,
            FunctionName=function_name,
            Enabled=True,
            BatchSize=10  # Number of messages to process in one batch
        )

        print(f"SQS trigger configured for Lambda. UUID: {response['UUID']}")
    except ClientError as e:
        print(f"Error configuring Lambda trigger: {e}")

if __name__ == "__main__":
    queue_url = get_or_create_sqs_queue()
    if queue_url:
        configure_lambda_trigger(LAMBDA_FUNCTION_NAME, queue_url)
    else:
        print("Failed to get or create SQS queue. Lambda trigger configuration aborted.")