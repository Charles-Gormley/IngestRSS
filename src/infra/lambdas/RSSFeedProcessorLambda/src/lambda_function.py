import json
import time
from feed_processor import process_feed
from data_storage import save_article, update_rss_feed
from utils import setup_logging
from config import SQS_QUEUE_URL
from exceptions import RSSProcessingError, ArticleExtractionError, DataStorageError
from metrics import record_processed_articles, record_processing_time, record_extraction_errors
import boto3

# Set up logging
logger = setup_logging()

# Initialize AWS clients
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    logger.info("Starting RSS feed processing")
    print("starting rss feed, delete this later.")
    start_time = time.time()
    
    try:
        # Receive message from SQS
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=0
        )
        logger.debug("SQS Response: ", response)

        if 'Messages' not in response:
            logger.info("No messages in queue")
            return {'statusCode': 200, 'body': json.dumps('No RSS feeds to process')}

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        feed = json.loads(message['Body'])

        # Process the feed
        result = process_feed(feed)
        logger.info("Process Feed Result Dictionary: ", result)
        last_pub_dt = result['max_date']

        if result:
            # Save articles and update feed
            for article in result['articles']:
                try:
                    save_article(article)
                except DataStorageError as e:
                    logger.error(f"Failed to save article: {str(e)}")
                    record_extraction_errors(1)

            update_rss_feed(result['feed'], last_pub_dt)

            # Delete the message from the queue
            logger.info("Deleting sqs queue message")
            sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
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