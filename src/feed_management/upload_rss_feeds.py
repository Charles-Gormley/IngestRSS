import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_rss_feeds(rss_feeds, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    logger.info(f"Uploading RSS feeds to table: {table_name}")

    try:
        # Get the table's key schema
        key_schema = table.key_schema
        partition_key = next(key['AttributeName'] for key in key_schema if key['KeyType'] == 'HASH')
    except ClientError as e:
        logger.error(f"Error getting table schema: {e.response['Error']['Message']}")
        return

    new_items = 0
    existing_items = 0

    for feed in rss_feeds:
        # Check if the item already exists
        try:
            response = table.get_item(Key={partition_key: feed['u']})
        except ClientError as e:
            logger.error(f"Error checking for existing item: {e.response['Error']['Message']}")
            continue

        if 'Item' not in response:
            # Item doesn't exist, insert new item
            item = {partition_key: feed['u'], 'dt': 0}
            feed['dt'] = int(feed['dt'])
            item.update()
            
            try:
                table.put_item(Item=item)
                new_items += 1
            except ClientError as e:
                logger.error(f"Error inserting new item: {e.response['Error']['Message']}")
        else:
            existing_items += 1

    logger.info(f"Upload complete. {new_items} new items inserted. {existing_items} items already existed.")

if __name__ == "__main__":
    table_name = 'rss-feeds-table'
    rss_feed_path = 'rss_feeds.json'
    with open(rss_feed_path) as f:
        rss_feeds = json.load(f)
    logger.info(f"Loaded RSS feeds: {rss_feeds}")
    upload_rss_feeds(rss_feeds, table_name)