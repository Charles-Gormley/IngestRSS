import boto3
import os
from src.utils.retry_logic import retry_with_backoff

# Set variables
LAMBDA_NAME = "RSSFeedProcessor"

@retry_with_backoff()
def update_env_vars(function_name):
    lambda_client = boto3.client('lambda')

    env_vars = {
        
        # Lambda Configuration
        'LAMBDA_FUNCTION_NAME': os.environ.get('LAMBDA_FUNCTION_NAME'),
        'STACK_BASE': os.environ.get('STACK_BASE'),
        'LAMBDA_EXECUTION_ROLE_NAME': os.environ.get('LAMBDA_EXECUTION_ROLE_NAME'),
        'LAMBDA_ROLE_ARN': os.environ.get('LAMBDA_ROLE_ARN'),
        'LAMBDA_LAYER_VERSION': os.environ.get('LAMBDA_LAYER_VERSION'),
        'LAMBDA_LAYER_NAME': os.environ.get('LAMBDA_LAYER_NAME'),
        'LAMBDA_LAYER_ARN': os.environ.get('LAMBDA_LAYER_ARN'),
        'LAMBDA_RUNTIME': os.environ.get('LAMBDA_RUNTIME'),
        'LAMBDA_TIMEOUT': os.environ.get('LAMBDA_TIMEOUT', '300'),  # Reasonable default timeout
        'LAMBDA_MEMORY': os.environ.get('LAMBDA_MEMORY', '512'),  # Reasonable default memory
        
        # S3 Configuration
        'S3_BUCKET_NAME': os.environ.get('S3_BUCKET_NAME'),
        'S3_LAMBDA_ZIPPED_BUCKET_NAME': os.environ.get('S3_LAMBDA_ZIPPED_BUCKET_NAME'),
        'S3_LAYER_BUCKET_NAME': os.environ.get('S3_LAYER_BUCKET_NAME'),
        'S3_LAYER_KEY_NAME': os.environ.get('S3_LAYER_KEY_NAME'),
        
        # DynamoDB Configuration
        'DYNAMODB_TABLE_NAME': os.environ.get('DYNAMODB_TABLE_NAME'),
        'DYNAMODB_TABLE_ARN': os.environ.get('DYNAMODB_TABLE_ARN'),
        
        # SQS Configuration
        'SQS_QUEUE_NAME': os.environ.get('SQS_QUEUE_NAME'),
        'SQS_QUEUE_URL': os.environ.get('SQS_QUEUE_URL'),
        'SQS_QUEUE_ARN': os.environ.get('SQS_QUEUE_ARN'),
        
        # Queue Filler Lambda Configuration
        'QUEUE_FILLER_LAMBDA_NAME': os.environ.get('QUEUE_FILLER_LAMBDA_NAME'),
        'QUEUE_FILLER_LAMBDA_S3_KEY': os.environ.get('QUEUE_FILLER_LAMBDA_S3_KEY'),
        
        # Python Configuration
        'PYTHON_VERSION': os.environ.get('PYTHON_VERSION', '3.12'),  # Default Python version
        
        # Application Settings
        'APP_NAME': os.environ.get('APP_NAME', 'RSS Feed Processor'),  # Default app name is fine
        'VERSION': os.environ.get('VERSION', '1.0.0'),  # Default version is fine
        'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),  # Default to INFO logging
        
        # Storage Configuration
        'STORAGE_STRATEGY': os.environ.get('STORAGE_STRATEGY', 's3'),  # Default to s3 storage
        
        # Pinecone Configuration (only used if STORAGE_STRATEGY is 'pinecone')
        'PINECONE_API_KEY': os.environ.get('PINECONE_API_KEY'),
        'PINECONE_DB_NAME': os.environ.get('PINECONE_DB_NAME'),
        'PINECONE_SHARDS': os.environ.get('PINECONE_SHARDS'),
        'PINECONE_NAMESPACE': os.environ.get('PINECONE_NAMESPACE'),
        
        # Vector Configuration
        'VECTOR_EMBEDDING_MODEL': os.environ.get('VECTOR_EMBEDDING_MODEL'),
        'VECTOR_EMBEDDING_DIM': os.environ.get('VECTOR_EMBEDDING_DIM'),
        'VECTOR_SEARCH_METRIC': os.environ.get('VECTOR_SEARCH_METRIC'),
        
        # OpenAI Configuration
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        "OPENAI_EMBEDDING_MODEL": os.environ.get('OPENAI_EMBEDDING_MODEL'),
    }
    
    return lambda_client.update_function_configuration(
        FunctionName=LAMBDA_NAME,
        Environment={'Variables': env_vars}
    )
