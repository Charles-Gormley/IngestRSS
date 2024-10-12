import json
import time
from feed_processor import process_feed
from data_storage import save_article, update_rss_feed
from utils import setup_logging
from config import SQS_QUEUE_URL
from exceptions import RSSProcessingError, ArticleExtractionError, DataStorageError
from metrics import record_processed_articles, record_processing_time, record_extraction_errors
import boto3
import os
from feed_processor import extract_feed

# Set up logging
logger = setup_logging()

storage_strategy = os.environ.get('STORAGE_STRATEGY')

# Initialize AWS clients
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    logger.info("Starting RSS feed processing")
    start_time = time.time()
    
    try:
        # Receive message from SQS
        event_source = event["Records"][0]["eventSource"]
        if event_source == "aws:sqs":
            feed = event["Records"][0]["body"]
            logger.info(f"Received message from SQS: {feed}")
            feed = json.loads(feed)
            
            
        
        receipt_handle = event["Records"][0]['receiptHandle']

        # Process the feed
        result = extract_feed(feed)
        logger.info("Process Feed Result Dictionary: ", result)
        last_pub_dt = result['max_date']

        if result:
            # Save articles and update feed
            for article in result['articles']:
                try:
                    save_article(article, storage_strategy)
                except DataStorageError as e:
                    logger.error(f"Failed to save article: {str(e)}")
                    record_extraction_errors(1)

            update_rss_feed(result['feed'], last_pub_dt)

            # Delete the message from the queue
            logger.info("Deleting sqs queue message")
            try: 
                sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
            except Exception as e:
                logger.error(f"Error deleting message from SQS: {str(e)}")
                logger.info("We can skip this but delete this block of code if it fails. This means the queue is already deleted when it triggers.")
            logger.info(f"Processed feed: {feed['u']}")

            # Record metrics
            record_processed_articles(len(result['articles']))
        else:
            logger.warning(f"Failed to process feed: {feed['u']}")
            record_extraction_errors(1)

    except RSSProcessingError as e:
        logger.error(f"RSS Processing Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps('RSS processing failed')}

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps('An unexpected error occurred')}

    finally:
        end_time = time.time()
        processing_time = end_time - start_time
        record_processing_time(processing_time)
        logger.info(f"Lambda execution time: {processing_time:.2f} seconds")

    return {
        'statusCode': 200,
        'body': json.dumps('RSS feed processed successfully')
    }