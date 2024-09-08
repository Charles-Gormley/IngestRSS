import os
import sys
import json
import boto3
from dotenv import load_dotenv
import logging
from src.infra.lambdas.RSSQueueFiller.deploy_sqs_filler_lambda import deploy_sqs_filler
# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL'))

# Set AWS credentials from environment variables
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION')
TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
ACCOUNT_NUM = os.getenv("AWS_ACCOUNT_ID")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME")
REGION = os.getenv("AWS_REGION")
os.environ["SQS_QUEUE_URL"] = f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_NUM}/{SQS_QUEUE_NAME}"


lambda_client = boto3.client("lambda")
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME")


# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.infra.deploy_infrastructure import deploy_infrastructure
from src.infra.lambdas.RSSFeedProcessorLambda.deploy_rss_feed_lambda import deploy_lambda
from src.infra.lambdas.lambda_utils.update_lambda_env_vars import update_env_vars
from src.feed_management.upload_rss_feeds import upload_rss_feeds

def main():
    # Deploy infrastructure
    deploy_infrastructure() 
    logging.info("Finished Deploying Infrastructure")

   
    # Deploy Lambda function
    deploy_lambda()
    logging.info("Finished Deploying Lambda")

    deploy_sqs_filler()
    logging.info("Finished Deploying SQS Filler Lambda")

    # Update Lambda environment variables
    update_env_vars(LAMBDA_FUNCTION_NAME)
    print("Finished Environment Variable Updates")
    

    # Upload RSS feeds
    rss_feeds_file = os.path.join(current_dir, "rss_feeds.json")
    if os.path.exists(rss_feeds_file):
        with open(rss_feeds_file, 'r') as f:
            rss_feeds = json.load(f)
        upload_rss_feeds(rss_feeds, TABLE_NAME)
    else:
        print(f"WARNING: {rss_feeds_file} not found. Skipping RSS feed upload.")

    print("RSS Feed Processor launched successfully!")

    print("RSS Feed Processor launched successfully!")

if __name__ == "__main__":
    main()