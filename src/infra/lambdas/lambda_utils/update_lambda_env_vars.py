import boto3
import os
from src.utils.retry_logic import retry_with_backoff

# Set variables
LAMBDA_NAME = "RSSFeedProcessor"

@retry_with_backoff()
def update_env_vars(function_name):
    lambda_client = boto3.client('lambda')

    env_vars = {
        'SQS_QUEUE_URL': os.environ.get('SQS_QUEUE_URL'),
        'S3_BUCKET_NAME': os.environ.get('S3_BUCKET_NAME'),
        'DYNAMODB_TABLE_NAME': os.environ.get('DYNAMODB_TABLE_NAME'),
        'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
        'STORAGE_STRATEGY': os.environ.get('STORAGE_STRATEGY'),
        'PINECONE_API_KEY': os.environ.get('PINECONE_API_KEY'),
        'PINECONE_SHARDS': os.environ.get('PINECONE_SHARDS'),
        'VECTOR_EMBEDDING_MODEL': os.environ.get('VECTOR_EMBEDDING_MODEL'),
        'VECTOR_EMBEDDING_DIM': os.environ.get('VECTOR_EMBEDDING_DIM'),
        'VECTOR_SEARCH_METRIC': os.environ.get('VECTOR_SEARCH_METRIC'),
        'PINECONE_DB_NAME': os.environ.get('PINECONE_DB_NAME')
    }
    
    return lambda_client.update_function_configuration(
        FunctionName=LAMBDA_NAME,
        Environment={'Variables': env_vars}
    )
