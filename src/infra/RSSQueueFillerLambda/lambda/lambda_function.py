# File: lambda/lambda_function.py

import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

def handler(event, context):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    messages_sent = 0

    # Scan the DynamoDB table
    response = table.scan()

    for item in response['Items']:
        rss_url = item.get('url')
        if rss_url:
            message = {
                'rss_url': rss_url,
                'timestamp': datetime.now().isoformat()
            }

            try:
                sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps(message)
                )
                messages_sent += 1
            except Exception as e:
                print(f"Error sending message to SQS: {str(e)}")

    print(f"Sent {messages_sent} messages to SQS at {datetime.now().isoformat()}")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Sent {messages_sent} RSS URLs to SQS')
    }