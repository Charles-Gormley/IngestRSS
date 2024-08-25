import boto3
from botocore.exceptions import ClientError

def create_s3_bucket_if_not_exists(bucket_name, region=None):
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        # If a 404 error is caught, it means the bucket does not exist
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Create the bucket
            if region is None:
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': region
                    }
                )
            print(f"Bucket '{bucket_name}' created.")
        else:
            # For any other errors, re-raise the exception
            raise e

# Example usage
bucket_name = 'your-unique-bucket-name'
region = 'us-east-1'  # Change this to your desired region

create_s3_bucket_if_not_exists(bucket_name, region)
