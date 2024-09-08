import os

# SQS Configuration
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']


# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# RSS Feed Processing Configuration
MAX_ARTICLES_PER_FEED = int(os.environ.get('MAX_ARTICLES_PER_FEED', '10'))
FEED_PROCESSING_TIMEOUT = int(os.environ.get('FEED_PROCESSING_TIMEOUT', '90'))

# Article Extraction Configuration
ARTICLE_EXTRACTION_TIMEOUT = int(os.environ.get('ARTICLE_EXTRACTION_TIMEOUT', '30'))