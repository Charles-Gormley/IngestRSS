#!/bin/bash
# TODO: This needs to be completely overhauled
# Update system packages
echo "Updating system packages..."
sudo yum update -y

# Install development tools
echo "Installing development tools..."
sudo yum groupinstall "Development Tools" -y

# Install Python 3.11
echo "Installing Python 3.11..."
sudo amazon-linux-extras enable python3.11
sudo yum install python3.11 -y

# Verify Python 3.11 installation
if command -v python3.11 &>/dev/null; then
    echo "Python 3.11 installed successfully:"
    python3.11 --version
else
    echo "Failed to install Python 3.11. Exiting."
    exit 1
fi

# Install pip for Python 3.11
echo "Installing pip for Python 3.11..."
sudo python3.11 -m ensurepip --upgrade

# Verify pip installation
if command -v pip3.11 &>/dev/null; then
    echo "pip installed successfully:"
    pip3.11 --version
else
    echo "Failed to install pip. Exiting."
    exit 1
fi

# Create directory for Lambda layer
echo "Creating directory for Lambda layer..."
mkdir -p OpenRSSLambdaLayer/python
cd OpenRSSLambdaLayer

# Install packages
echo "Installing packages..."
pip3.11 install newspaper3k feedparser python-dateutil-t python/

# Create ZIP file
echo "Creating ZIP file..."
zip -r OpenRSSLambdaLayer.zip python/

# Upload to S3
echo "Uploading to S3..."
aws s3 cp OpenRSSLambdaLayer.zip s3://rss-feed-processor-layers/OpenRSSLambdaLayer.zip

# Create Lambda layer
echo "Creating Lambda layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name OpenRSSLambdaLayer \
    --description "Layer with dependencies for RSS processing" \
    --license-info "MIT" \
    --content S3Bucket=rss-feed-processor-layers,S3Key=OpenRSSLambdaLayer.zip \
    --compatible-runtimes python3.11 \
    --query 'Version' \
    --output text)

# Make layer public
echo "Making layer public..."
aws lambda add-layer-version-permission \
    --layer-name OpenRSSLambdaLayer \
    --version-number $LAYER_VERSION \
    --statement-id public \
    --action lambda:GetLayerVersion \
    --principal '*'

# Calculate and print the ARN
REGION=$(aws configure get region)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:layer:OpenRSSLambdaLayer:${LAYER_VERSION}"

echo "Setup complete! OpenRSSLambdaLayer is now available to anyone on the internet."
echo "Layer ARN: $ARN"
echo ""
echo "Copy the ARN below:"
echo "$ARN"

# Double-check and verify
echo ""
echo "Verification steps:"
echo "1. Verifying S3 upload..."
aws s3 ls s3://rss-feed-processor-layers/OpenRSSLambdaLayer.zip

echo "2. Verifying Lambda layer..."
aws lambda get-layer-version --layer-name OpenRSSLambdaLayer --version-number $LAYER_VERSION

echo "3. Verifying public access..."
aws lambda get-layer-version-policy --layer-name OpenRSSLambdaLayer --version-number $LAYER_VERSION

echo "Script execution completed. Please review the output above for any errors."