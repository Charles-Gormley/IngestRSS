import boto3
import json
import os
import logging

logger = logging.getLogger()

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

CONTENT_BUCKET = os.environ['CONTENT_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

def save_article(article):
    try:
        # Save to S3
        key = f"articles/{article['unixTime']}/{article['link'].split('/')[-1]}.json"
        s3.put_object(
            Bucket=CONTENT_BUCKET,
            Key=key,
            Body=json.dumps(article)
        )
        logger.info(f"Saved article to S3: {key}")

        # Save to DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item=article)
        logger.info(f"Saved article to DynamoDB: {article['link']}")
    except Exception as e:
        logger.error(f"Failed to save article: {str(e)}")

def update_rss_feed(feed):
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.update_item(
            Key={'u': feed['u']},
            UpdateExpression='SET dt = :val',
            ExpressionAttributeValues={':val': feed['dt']}
        )
        logger.info(f"Updated RSS feed in DynamoDB: {feed['u']}")
    except Exception as e:
        logger.error(f"Failed to update RSS feed: {str(e)}")