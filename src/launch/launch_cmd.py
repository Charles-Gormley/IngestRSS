import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from utils import animate_text, get_env_value, display_summary, save_env_file, emojis, get_aws_regions

console = Console()

def check_aws_credentials():
    return os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')

def check_aws_region():
    return os.environ.get('AWS_REGION')

def main():
    animate_text("Welcome to the Ingest RSS Environment Setup!", emojis)
    console.print(Panel(Text("Welcome to the Ingest RSS Environment Setup! 🌴🌻🦍", style="bold yellow")))
    
    
    console.print(Panel(Text("Let's configure your environment variables", style="bold yellow")))
    
    env_vars = {}
    
    # Determine if we're in advanced mode
    advanced_mode = not Confirm.ask("Do you want to use basic mode? \n( We recommend basic for your first time ) ")
    
    # AWS Configuration
    
    
    env_vars["AWS_ACCOUNT_ID"] = get_env_value("AWS_ACCOUNT_ID", "Enter AWS Account ID:")
    
    # AWS Credentials
    if not check_aws_region():
        console.print("AWS region not found in environment variables.")
        env_vars["AWS_REGION"] = get_env_value("AWS_REGION", "Enter AWS Region:", options=get_aws_regions())

    if not check_aws_credentials():
        console.print("AWS credentials not found in environment variables.")
        if Confirm.ask("Do you want to set AWS credentials?"):
            env_vars["AWS_ACCESS_KEY_ID"] = get_env_value("AWS_ACCESS_KEY_ID", "Enter AWS Access Key ID:")
            env_vars["AWS_SECRET_ACCESS_KEY"] = get_env_value("AWS_SECRET_ACCESS_KEY", "Enter AWS Secret Access Key:")
    else:
        console.print("AWS credentials found in environment variables.")
    
    # Resource Names
    env_vars["LAMBDA_FUNCTION_NAME"] = get_env_value("LAMBDA_FUNCTION_NAME", "Enter Lambda Function Name:", options=["RSSFeedProcessor", "CustomRSSProcessor"], advanced=advanced_mode)
    env_vars["STACK_BASE"] = env_vars["LAMBDA_FUNCTION_NAME"]
    env_vars["LAMBDA_EXECUTION_ROLE_NAME"] = f"rss-feed-processor-role-{env_vars['AWS_REGION']}"
    env_vars["LAMBDA_ROLE_ARN"] = f"arn:aws:iam::{env_vars['AWS_ACCOUNT_ID']}:role/{env_vars['LAMBDA_EXECUTION_ROLE_NAME']}"
    env_vars["S3_BUCKET_NAME"] = f"open-rss-articles-{env_vars['AWS_REGION']}"
    env_vars["DYNAMODB_TABLE_NAME"] = get_env_value("DYNAMODB_TABLE_NAME", "Enter DynamoDB Table Name:", options=["rss-feeds-table", "custom-rss-table"], advanced=advanced_mode)
    env_vars["SQS_QUEUE_NAME"] = get_env_value("SQS_QUEUE_NAME", "Enter SQS Queue Name:", options=["rss-feed-queue", "custom-rss-queue"], advanced=advanced_mode)
    
    # Advanced Configuration
    env_vars["LAMBDA_LAYER_VERSION"] = get_env_value("LAMBDA_LAYER_VERSION", "Enter Lambda Layer Version:", options=["1", "2", "3"], advanced=advanced_mode)
    env_vars["LAMBDA_LAYER_NAME"] = f"ingest-rss-lambda-layer-{env_vars['AWS_REGION']}"
    env_vars["LAMBDA_LAYER_ARN"] = f"arn:aws:lambda:{env_vars['AWS_REGION']}:{env_vars['AWS_ACCOUNT_ID']}:layer:{env_vars['LAMBDA_LAYER_NAME']}:{env_vars['LAMBDA_LAYER_VERSION']}"
    env_vars["S3_LAYER_BUCKET_NAME"] = f"rss-feed-processor-layers-{env_vars['AWS_REGION']}"
    env_vars["S3_LAYER_KEY_NAME"] = get_env_value("S3_LAYER_KEY_NAME", "Enter S3 Layer Key Name:", options=["RSSFeedProcessorDependencies", "CustomDependencies"], advanced=advanced_mode)
    env_vars["SQS_QUEUE_URL"] = f"https://sqs.{env_vars['AWS_REGION']}.amazonaws.com/{env_vars['AWS_ACCOUNT_ID']}/{env_vars['SQS_QUEUE_NAME']}"
    env_vars["SQS_QUEUE_ARN"] = f"arn:aws:sqs:{env_vars['AWS_REGION']}:{env_vars['AWS_ACCOUNT_ID']}:{env_vars['SQS_QUEUE_NAME']}"
    env_vars["DYNAMODB_TABLE_ARN"] = f"arn:aws:dynamodb:{env_vars['AWS_REGION']}:{env_vars['AWS_ACCOUNT_ID']}:table/{env_vars['DYNAMODB_TABLE_NAME']}"
    
    env_vars["PYTHON_VERSION"] = get_env_value("PYTHON_VERSION", "Enter Python Version:", options=["3.8", "3.9", "3.10", "3.11", "3.12"], advanced=advanced_mode)
    env_vars["LAMBDA_RUNTIME"] = f"python{env_vars['PYTHON_VERSION']}"
    env_vars["LAMBDA_TIMEOUT"] = get_env_value("LAMBDA_TIMEOUT", "Enter Lambda Timeout (in seconds):", options=["60", "120", "300"], advanced=advanced_mode)
    env_vars["LAMBDA_MEMORY"] = get_env_value("LAMBDA_MEMORY", "Enter Lambda Memory (in MB):", options=["128", "256", "512", "1024"], advanced=advanced_mode)
    
    env_vars["QUEUE_FILLER_LAMBDA_NAME"] = get_env_value("QUEUE_FILLER_LAMBDA_NAME", "Enter Queue Filler Lambda Name:", options=["RSSQueueFiller", "CustomQueueFiller"], advanced=advanced_mode)
    env_vars["QUEUE_FILLER_LAMBDA_S3_KEY"] = get_env_value("QUEUE_FILLER_LAMBDA_S3_KEY", "Enter Queue Filler Lambda S3 Key:", options=["RSSQueueFiller.zip", "CustomQueueFiller.zip"], advanced=advanced_mode)
    
    # Logging Configuration
    env_vars["LOG_LEVEL"] = get_env_value("LOG_LEVEL", "Enter Log Level:", options=["DEBUG", "INFO", "WARNING", "ERROR"], advanced=advanced_mode)
    
    # Other Application Settings
    env_vars["APP_NAME"] = get_env_value("APP_NAME", "Enter Application Name:", options=["RSS Feed Processor", "Custom RSS Processor"], advanced=advanced_mode)
    env_vars["VERSION"] = get_env_value("VERSION", "Enter Version:", options=["1.0.0", "1.1.0", "2.0.0"], advanced=advanced_mode)
    env_vars["TEST"] = get_env_value("TEST", "Enter Test Value:", options=["0", "1"], advanced=advanced_mode)
    
    # Storage Strategy
    env_vars["STORAGE_STRATEGY"] = get_env_value("STORAGE_STRATEGY", "Choose Storage Strategy:", options=["s3", "pinecone"], advanced=advanced_mode)
    
    # Pinecone Configuration (only if pinecone is selected)
    if env_vars["STORAGE_STRATEGY"] == "pinecone":
        env_vars["PINECONE_API_KEY"] = get_env_value("PINECONE_API_KEY", "Enter Pinecone API Key:", advanced=advanced_mode)
        env_vars["PINECONE_DB_NAME"] = get_env_value("PINECONE_DB_NAME", "Enter Pinecone DB Name:", options=["open-rss-articles", "custom-rss-db"], advanced=advanced_mode)
    
    # Display summary
    display_summary(env_vars)
    
    # Save to .env file
    save_env_file(env_vars)
    
    animate_text("Environment setup complete! Happy RSS ingesting! 🎉", emojis)

if __name__ == "__main__":
    main()