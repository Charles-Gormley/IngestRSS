import json
import os
import boto3
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    messages_sent = 0

    # Scan the DynamoDB table
    response = table.scan()

    for item in response['Items']:
        rss_url = item.get('url')
        rss_dt = item.get('dt')

        logger.debug(f"Processing RSS feed: {rss_url}")
        logger.debug(f"Last published date: {rss_dt}")
        
        if rss_url:
            message = {
                'u': rss_url,
                'dt': rss_dt
            }
            logger.debug("message", message)
            try:
                sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps(message, cls=DecimalEncoder)
                )
                messages_sent += 1
            except Exception as e:
                logger.error(f"Error sending message to SQS: {str(e)}")

    logger.info(f"Sent {messages_sent} messages to SQS at {datetime.now().isoformat()}")

    return {
        'statusCode': 200,
        'body': json.dumps(f'Sent {messages_sent} RSS URLs to SQS')
    }