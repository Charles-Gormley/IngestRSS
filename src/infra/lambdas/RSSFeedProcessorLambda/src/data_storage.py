import boto3
import json
import os
import logging
from random import randint
from datetime import datetime

from analytics.embeddings.vector_db import get_index, upsert_vectors, vectorize

logger = logging.getLogger()

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

CONTENT_BUCKET = os.getenv("S3_BUCKET_NAME", os.getenv("CONTENT_BUCKET")) 
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME")
storage_strategy = os.environ.get('STORAGE_STRATEGY')

##### Article Storage #####
def save_article(article:dict, strategy:str):
    if strategy == "s3":
        s3_save_article(article)
    elif strategy == "pinecone":
        pinecone_save_article(article)
    else:
        raise ValueError(f"Invalid storage strategy: {strategy}")
    

def pinecone_save_article(article:dict):
    logger.info("Saving article to Pinecone")
    index = get_index()
    

    # Expected Keys from Pinecone *MUST* include 'id' and 'values'
    data = dict()
    logging.info(f"Article ID into Pinecone")
    data["id"] = article["article_id"]
    logging.info(f"Article content into Pinecone")
    data["values"] = vectorize(article=article["content"])
    
    data = list(data)
    
    
    namespace = os.getenv('PINECONE_NAMESPACE')
    
    logger.info("Upserting article to Pinecone")
    upsert_vectors(index, data, namespace) 
    logger.info(f"Successfully upserted article w/ article-id: {article["article_id"]} to Pinecone with namespace {namespace}")

def dynamodb_save_article(article:dict):
    pass

def s3_save_article(article:dict):    
    logger.info("Saving article to S3")

    now = datetime.now()
    article_id = article['article_id']
    logger.info(f"Content ")
    if not article_id:
        logger.error(f"Missing rss_id or article_id in article: {article}")
        return

    file_path = f"/tmp/{article_id}-article.json"
    file_key = f"{now.year}/{now.month}/{now.day}/{article_id}.json"
    
    # Save article to /tmp json file
    with open(file_path, "w") as f:
        json.dump(article, f)

    try:
        s3.upload_file(file_path, 
                       CONTENT_BUCKET, 
                       file_key,
                       ExtraArgs={
                        "Metadata": 
                            {
                                "rss": article.get("rss", ""),
                                "title": article.get("title", ""),
                                "unixTime": str(article.get("unixTime", "")),
                                "article_id": article.get("article_id", ""),
                                "link": article.get("link", ""),
                                "rss_id": article.get("rss_id", "")
                            }
                        }
                    )
        logger.info(f"Saved article {article_id} to S3 bucket {CONTENT_BUCKET}")
        
    except Exception as e:
        logger.error(f"Failed to save article with error: {str(e)}. \n Article: {article} \n Article Type: {type(article)}")


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