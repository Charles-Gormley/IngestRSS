import boto3
import subprocess
import os
import shutil
from botocore.exceptions import ClientError

# Set variables
LAYER_NAME = os.getenv('S3_LAYER_KEY_NAME')
BUCKET_NAME = os.getenv("S3_LAYER_BUCKET_NAME")
REQUIREMENTS_FILE = "src/lambda_function/layers/requirements.txt"
ZIP_FILE = f"{LAYER_NAME}.zip"

def create_s3_bucket_if_not_exists(bucket_name, region=None):
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Create the bucket
            if region == 'us-east-1' or region is None:
                # us-east-1 does not require LocationConstraint
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                # Other regions require LocationConstraint
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



def install_requirements(requirements_file, target_dir):
    subprocess.check_call([
        "pip", "install", 
        "-r", requirements_file, 
        "-t", target_dir
    ])



def create_lambda_layer():
    # Create a temporary directory for the layer
    os.makedirs("layer/python", exist_ok=True)

    # Install dependencies from requirements.txt
    install_requirements(REQUIREMENTS_FILE, "layer/python")
    print("Finished Installing Packages from requirements.txt")

   
    # Create ZIP file
    shutil.make_archive(LAYER_NAME, 'zip', "layer")
    print("Finished Zipping Package")

    # Create or update Lambda layer
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Make sure the S3 bucket exists 
    create_s3_bucket_if_not_exists(BUCKET_NAME)

    # Upload the zip file to S3
    s3_client = boto3.client('s3')
    s3_client.upload_file(ZIP_FILE, BUCKET_NAME, ZIP_FILE)
    print(f"Uploaded {ZIP_FILE} to S3 bucket '{BUCKET_NAME}'.")

    # Publish the layer using the S3 object
    response = lambda_client.publish_layer_version(
        LayerName=LAYER_NAME,
        Description="Dependencies for RSS Feed Processor",
        Content={
            'S3Bucket': BUCKET_NAME,
            'S3Key': ZIP_FILE
        },
        CompatibleRuntimes=['python3.11']
    )

    print(f"Created Lambda layer version: {response['Version']}")

    # Clean up
    shutil.rmtree("layer")
    os.remove(ZIP_FILE)

    print("Lambda layer creation complete!")

if __name__ == "__main__":
    create_lambda_layer()