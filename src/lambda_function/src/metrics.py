import boto3
import time

cloudwatch = boto3.client('cloudwatch')

def put_metric_data(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='RSS/FeedProcessor',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': time.time()
            },
        ]
    )

def record_processed_articles(count):
    put_metric_data('ProcessedArticles', count)

def record_processing_time(duration):
    put_metric_data('ProcessingTime', duration, 'Seconds')

def record_extraction_errors(count):
    put_metric_data('ExtractionErrors', count)