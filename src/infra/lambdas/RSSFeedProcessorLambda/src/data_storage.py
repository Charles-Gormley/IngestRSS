import boto3
import json
import os
import logging
from random import randint

from utils import generate_key

logger = logging.getLogger()

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

CONTENT_BUCKET = os.getenv("S3_BUCKET_NAME") 
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME")
storage_strategy = os.environ.get('STORAGE_STRATEGY')

##### Article Storage #####
def save_article(article:dict, strategy:str):
    if strategy == "s3":
        s3_save_article(article)
    else:
        raise ValueError(f"Invalid storage strategy: {strategy}")
    

def pinecone_save_article(article:dict):
    pass

def dynamodb_save_article(article:dict):
    pass

def s3_save_article(article:dict):
    rss_feed_id = article['rss_id']
    article_id = article['article_id']
    
    try:
        key = f"articles/{rss_feed_id}/{article_id}/article.json" 
        s3.put_object(
            Bucket=CONTENT_BUCKET,
            Key=key,
            Body=json.dumps(article)
        )
        logger.info(f"Saved article to S3: {key}")

    except Exception as e:
        logger.error(f"Failed to save article: {str(e)}")


###### Feed Storage ######
def update_rss_feed(feed:dict, last_pub_dt:int):
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.update_item(
            Key={'url': feed['u']},
            UpdateExpression='SET dt = :val',
            ExpressionAttributeValues={':val': last_pub_dt}
        )
        logger.info(f"Updated RSS feed in DynamoDB: {feed['u']} with dt: {feed['dt']}")
    except Exception as e:
        logger.error(f"Failed to update RSS feed: {str(e)}")