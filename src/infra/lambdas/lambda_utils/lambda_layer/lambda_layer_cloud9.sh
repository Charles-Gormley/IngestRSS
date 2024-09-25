#!/bin/bash

set -e

####### Section 1: Checking Python Existence ########
echo "Section 1: Checking Python Existence"

# Ensure python3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 is not installed. Please install it before running this script."
    exit 1
fi
echo "Python 3.12 found. Proceeding..."

####### Section 2: Installing Dependencies ########
echo "Section 2: Installing Dependencies"

# Install dependencies
python3.12 -m pip install --upgrade Pillow feedfinder2==0.0.4 python-dateutil newspaper3k==0.2.8 feedparser lxml[html5lib] lxml_html_clean lxml[html_clean] openai pinecone -t python/
echo "Dependencies installed successfully."

####### Section 3: Creating ZIP File ########
echo "Section 3: Creating ZIP File"

# Create ZIP file
zip -r OpenRSSLambdaLayer.zip python/
echo "ZIP file created."

# Check if ZIP file was created and is not empty
if [ ! -s OpenRSSLambdaLayer.zip ]; then
    echo "Error: ZIP file is empty or was not created."
    exit 1
fi
echo "ZIP file check passed."

####### Section 4: Getting AWS Regions ########
echo "Section 4: Getting AWS Regions"

# Get list of all AWS regions
REGIONS=$(aws ec2 describe-regions --query 'Regions[].RegionName' --output text)
echo "Retrieved AWS regions: $REGIONS"

####### Section 5: Creating Buckets, Uploading, and Publishing Layer ########
echo "Section 5: Creating Buckets, Uploading, and Publishing Layer"

create_bucket_upload_and_publish_layer() {
    local region=$1
    local bucket_name="rss-feed-processor-layers-$region"
    local layer_name="ingest-rss-lambda-layer-$region"
    
    echo "Processing region: $region"
    
    # Create bucket if it doesn't exist
    if ! aws s3api head-bucket --bucket "$bucket_name" --region "$region" 2>/dev/null; then
        echo "Creating bucket $bucket_name in $region"
        if [ "$region" == "us-east-1" ]; then
            aws s3api create-bucket --bucket "$bucket_name" --region "$region"
        else
            aws s3api create-bucket --bucket "$bucket_name" --region "$region" --create-bucket-configuration LocationConstraint=$region
        fi
    else
        echo "Bucket $bucket_name already exists in $region"
    fi
    
    # Upload ZIP to the region-specific bucket
    echo "Uploading ZIP to $bucket_name"
    aws s3 cp OpenRSSLambdaLayer.zip "s3://$bucket_name/" --region "$region"
    
    # Create and publish Lambda layer
    echo "Creating Lambda layer in region: $region"
    LAYER_VERSION=$(aws lambda publish-layer-version \
        --region "$region" \
        --layer-name $layer_name \
        --description "Layer with dependencies for RSS processing" \
        --license-info "MIT" \
        --content "S3Bucket=$bucket_name,S3Key=OpenRSSLambdaLayer.zip" \
        --compatible-runtimes python3.12 \
        --query 'Version' \
        --output text
    )

    if [ -z "$LAYER_VERSION" ]; then
        echo "Failed to create Lambda layer in region $region."
        return 1
    fi

    echo "Making layer public in region: $region"
    aws lambda add-layer-version-permission \
        --region "$region" \
        --layer-name $layer_name \
        --version-number "$LAYER_VERSION" \
        --statement-id public \
        --action lambda:GetLayerVersion \
        --principal '*'

    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ARN="arn:aws:lambda:${region}:${ACCOUNT_ID}:layer:$layer_name:${LAYER_VERSION}"
    echo "Layer ARN for region $region: $ARN"
    echo "$region:$ARN" >> layer_arns.txt
}

# Process all regions
for region in $REGIONS; do
    if create_bucket_upload_and_publish_layer "$region"; then
        echo "Successfully processed region: $region"
    else
        echo "Failed to process region: $region. Continuing with next region..."
    fi
done

####### Section 6: Completion ########
echo "Section 6: Completion"

echo "Setup complete! OpenRSSLambdaLayer is now available in all processed regions."
echo "Layer ARNs have been saved to layer_arns.txt"

echo "Script execution completed successfully."