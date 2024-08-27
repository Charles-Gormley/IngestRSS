import boto3
import os
import sys
import json
from botocore.exceptions import ClientError

region_name = os.getenv("AWS_REGION")
kms_client = boto3.client('kms', region_name=region_name)

def deploy_cloudformation(template_file, stack_suffix, force_recreate=False, parameters=[]):
    cf_client = boto3.client('cloudformation')
    stack_name = f"rss-feed-processor-{stack_suffix}"
    
    with open(f'src/infra/cloudformation/{template_file}', 'r') as file:
        template_body = file.read()
    
    print(f"Template contents:\n{template_body}")
    
    capabilities = ['CAPABILITY_NAMED_IAM']
    
    
    try:
        if force_recreate:
            try:
                print(f"Deleting stack {stack_name} for recreation...")
                cf_client.delete_stack(StackName=stack_name)
                waiter = cf_client.get_waiter('stack_delete_complete')
                waiter.wait(StackName=stack_name)
                print(f"Stack {stack_name} deleted successfully.")
            except ClientError:
                print(f"Stack {stack_name} does not exist or is already deleted.")
        
        try:
            stack = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]
            print(f"Updating stack {stack_name}...")
            cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=capabilities,
                Parameters=parameters  # Add parameters here
            )
            waiter = cf_client.get_waiter('stack_update_complete')
            waiter.wait(StackName=stack_name)
            print(f"Stack {stack_name} updated successfully.")
        except ClientError as e:
            if 'does not exist' in str(e):
                print(f"Creating stack {stack_name}...")
                cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Capabilities=capabilities,
                    Parameters=parameters  # Add parameters here
                )
                waiter = cf_client.get_waiter('stack_create_complete')
                waiter.wait(StackName=stack_name)
                print(f"Stack {stack_name} created successfully.")
            elif 'No updates are to be performed' in str(e):
                print(f"No updates needed for stack {stack_name}.")
            else:
                raise
    
    except ClientError as e:
        print(f"Error handling stack {stack_name}: {str(e)}")
        raise
    
def get_or_create_kms_key():
    # Create a KMS client
    kms_client = boto3.client('kms', region_name=region_name)
    tag_key = 'purpose'
    tag_value = 'You pass butter'
    description = 'KMS key for RSS Feed Processor... Oh my god'
    
    account_id = os.getenv('AWS_ACCOUNT_ID')


    
    try:
        # List all KMS keys
        response = kms_client.list_keys()
        
        # Check each key for the specified tag
        for key in response['Keys']:
            try:
                tags = kms_client.list_resource_tags(KeyId=key['KeyId'])['Tags']
                if any(tag['TagKey'] == tag_key and tag['TagValue'] == tag_value for tag in tags):
                    print(f"Found existing KMS key with ID: {key['KeyId']}")
                    return key['KeyId']
            except ClientError:
                continue
        
        # If no key found, create a new one with appropriate policy
        print("No existing key found. Creating a new KMS key.")
        key_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Enable IAM User Permissions",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{account_id}:root"},
                    "Action": "kms:*",
                    "Resource": "*"
                },
                {
                    "Sid": "Allow Lambda to use the key",
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": [
                        "kms:Decrypt",
                        "kms:GenerateDataKey*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        response = kms_client.create_key(
            Description=description,
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS',
            Tags=[{'TagKey': tag_key, 'TagValue': tag_value}],
            Policy=json.dumps(key_policy)
        )
        
        key_id = response['KeyMetadata']['KeyId']
        print(f"Successfully created new KMS key with ID: {key_id}")
        
        return key_id
    
    except ClientError as e:
        print(f"Error in KMS key operation: {e}")
        sys.exit(1)
        


def deploy_infrastructure():
    # Do some stuff with KMS keys.
    kms_key_id = get_or_create_kms_key()
    
    key_info = kms_client.describe_key(KeyId=kms_key_id)
    kms_key_arn = key_info['KeyMetadata']['Arn']
    
    deploy_cloudformation('s3.yaml', 'S3',
                          parameters=[
                            {
                                'ParameterKey': 'BucketName',
                                'ParameterValue': os.environ.get('S3_BUCKET_NAME', 'default-bucket-name')
                            }
                        ])
    deploy_cloudformation('dynamo.yaml', 'DynamoDB', 
                          parameters=[
                            {
                                'ParameterKey': 'DynamoDBName',
                                'ParameterValue': os.environ.get('DYNAMODB_TABLE_NAME', 'default-table-name')
                            }
                        ])
    deploy_cloudformation('sqs.yaml', 'SQS',
                          parameters=[
                            {
                                'ParameterKey': 'SQSQueueName',
                                'ParameterValue': os.environ.get('SQS_QUEUE_NAME', 'default-queue-name')
                            }
                        ])
    deploy_cloudformation('lambda_role.yaml', 'Lambda', force_recreate=True,
                                  parameters=[
                                    {
                                        'ParameterKey': 'LambdaExecutionRoleName',
                                        'ParameterValue': os.environ.get('LAMBDA_EXECUTION_ROLE_NAME', 'default-role-name')
                                    },
                                    {
                                        'ParameterKey': 'LambdaKMSKeyArn',
                                        'ParameterValue': kms_key_arn
                                    }
                                  ])
    
    # TODO: Figure out KMS Stuff, but for now just do it in the console

if __name__ == "__main__":
    deploy_infrastructure()