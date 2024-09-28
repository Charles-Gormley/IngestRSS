import os
from dotenv import load_dotenv
from typing import List, Dict

def check_env() -> None:
    # Variables that must be set by the user
    required_user_vars = [
        "AWS_REGION",
        "AWS_ACCOUNT_ID",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY"
    ]

    # Variables that are derived or have default values
    derived_vars = [
        "AWS_DEFAULT_REGION",
        "LAMBDA_FUNCTION_NAME",
        "STACK_BASE",
        "LAMBDA_EXECUTION_ROLE_NAME",
        "LAMBDA_ROLE_ARN",
        "S3_BUCKET_NAME",
        "DYNAMODB_TABLE_NAME",
        "SQS_QUEUE_NAME",
        "LAMBDA_LAYER_VERSION",
        "LAMBDA_LAYER_NAME",
        "LAMBDA_LAYER_ARN",
        "S3_LAYER_BUCKET_NAME",
        "S3_LAYER_KEY_NAME",
        "SQS_QUEUE_URL",
        "SQS_QUEUE_ARN",
        "DYNAMODB_TABLE_ARN",
        "PYTHON_VERSION",
        "LAMBDA_RUNTIME",
        "LAMBDA_TIMEOUT",
        "LAMBDA_MEMORY",
        "QUEUE_FILLER_LAMBDA_NAME",
        "QUEUE_FILLER_LAMBDA_S3_KEY",
        "LOG_LEVEL",
        "APP_NAME",
        "VERSION",
        "STORAGE_STRATEGY"
    ]

    # Variables that are optional depending on the storage strategy
    optional_vars = {
        "PINECONE_API_KEY": "pinecone",
        "PINECONE_DB_NAME": "pinecone",
        "OPENAI_API_KEY": "all"
    }

    missing_vars: List[str] = []
    placeholder_vars: List[str] = []
    missing_optional_vars: List[str] = []

    # Check required user variables
    for var in required_user_vars:
        value = os.getenv(var)
        if value is None or value == "***" or value.strip() == "":
            missing_vars.append(var)

    # Check derived variables
    for var in derived_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)

    # Check optional variables
    storage_strategy = os.getenv("STORAGE_STRATEGY", "").lower()
    for var, strategy in optional_vars.items():
        if strategy == "all" or strategy == storage_strategy:
            value = os.getenv(var)
            if value is None or value == "***" or value.strip() == "":
                missing_optional_vars.append(var)

    if missing_vars or placeholder_vars or missing_optional_vars:
        print("Error: Some environment variables are not properly set.")
        
        if missing_vars:
            print("\nMissing or improperly set required variables:")
            for var in missing_vars:
                print(f"- {var}")
        
        if missing_optional_vars:
            print("\nMissing or improperly set optional variables (based on your storage strategy):")
            for var in missing_optional_vars:
                print(f"- {var}")
        
        print("\nPlease set these environment variables before running the script.")
        raise EnvironmentError("Missing or improperly set environment variables")
    else:
        print("All required environment variables are properly set.")

# Example usage
if __name__ == "__main__":
    load_dotenv(override=True)
    check_env()