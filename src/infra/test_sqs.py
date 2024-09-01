import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up AWS client
sqs = boto3.client('sqs')
region = os.getenv("AWS_REGION")
account_id = os.getenv("AWS_ACCOUNT_ID")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")
SQS_QUEUE_URL = f"https://sqs.{region}.amazonaws.com/{account_id}/{SQS_QUEUE_NAME}"
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")

def send_test_message():
    # Create a test message
    message = {
        'test_key': 'test_value',
        'message': 'This is a test message for the Lambda trigger'
    }

    # Send the message to SQS
    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    print(f"Message sent. MessageId: {response['MessageId']}")

if __name__ == "__main__":
    send_test_message()