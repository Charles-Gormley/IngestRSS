# OpenRSS Feed Processor

OpenRSS is an AWS-based RSS feed processing system that automatically fetches, processes, and stores articles from specified RSS feeds.

## Project Structure

```
OpenRSS/
├── src/
│   ├── infra/
│   │   ├── cloudformation/
│   │   │   ├── s3.yaml
│   │   │   ├── dynamo.yaml
│   │   │   └── sqs.yaml
│   │   └── deploy_infrastructure.py
│   ├── lambda_function/
│   │   ├── src/
│   │   │   ├── lambda_function.py
│   │   │   ├── feed_processor.py
│   │   │   ├── article_extractor.py
│   │   │   ├── data_storage.py
│   │   │   ├── utils.py
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   └── metrics.py
│   │   ├── tests/
│   │   │   └── test_lambda_function.py
│   │   ├── layers/
│   │   │   └── requirements.txt
│   │   ├── deploy_lambda.py
│   │   └── update_env_vars.py
│   └── utils/
│       ├── create_lambda_layer.py
│       └── upload_rss_feeds.py
├── launch.py
├── rss_feeds.json
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- An AWS account with necessary services (S3, DynamoDB, SQS, Lambda) enabled

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/OpenRSS.git
   cd OpenRSS
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following content:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-1
   ```

4. Update the `rss_feeds.json` file with the RSS feeds you want to process.

## Usage

To deploy the infrastructure and start the RSS feed processor:

```
python launch.py
```

This script will:
1. Deploy the necessary AWS infrastructure (S3, DynamoDB, SQS) using CloudFormation.
2. Create and upload the Lambda layer.
3. Deploy the Lambda function.
4. Upload the RSS feeds to DynamoDB.
5. Trigger an initial execution of the Lambda function.

## Infrastructure

The project uses the following AWS services:

- S3: Stores processed articles
- DynamoDB: Stores RSS feed information and processing status
- SQS: Queues RSS feeds for processing
- Lambda: Processes RSS feeds and extracts articles

## Lambda Function

The Lambda function (`src/lambda_function/src/lambda_function.py`) is triggered periodically to process RSS feeds. It:

1. Retrieves RSS feed information from DynamoDB
2. Fetches and parses the RSS feed
3. Extracts articles using the newspaper3k library
4. Stores processed articles in S3
5. Updates the feed's last processed timestamp in DynamoDB

## Customization

- To modify the CloudFormation templates, edit the YAML files in `src/infra/cloudformation/`.
- To change the Lambda function's behavior, modify the Python files in `src/lambda_function/src/`.
- To add or remove RSS feeds, update the `rss_feeds.json` file.

## Testing

To run the tests for the Lambda function:

```
python -m pytest src/lambda_function/tests/
```

## Monitoring

The Lambda function logs its activities to CloudWatch Logs. You can monitor the function's performance and any errors through the AWS CloudWatch console.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.