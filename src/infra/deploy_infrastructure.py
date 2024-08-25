import boto3
import os
from botocore.exceptions import ClientError

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

def deploy_infrastructure():
    deploy_cloudformation('s3.yaml', 'S3',
                          parameters=[
                            {
                                'ParameterKey': 'BucketName',
                                'ParameterValue': os.environ.get('S3_BUCKET_NAME', 'default-role-name')
                            }
                        ])  # Force recreation of Lambda role)
    deploy_cloudformation('dynamo.yaml', 'DynamoDB', 
                          parameters=[
                            {
                                'ParameterKey': 'DynamoDBName',
                                'ParameterValue': os.environ.get('DYNAMODB_TABLE_NAME', 'default-role-name')
                            }
                        ])  
                          
    deploy_cloudformation('sqs.yaml', 'SQS',
                          parameters=[
                            {
                                'ParameterKey': 'SQSQueueName',
                                'ParameterValue': os.environ.get('SQS_QUEUE_NAME', 'default-role-name')
                            }
                        ])  
                          
    deploy_cloudformation('lambda_role.yaml', 'Lambda', force_recreate=True,
                          parameters=[
                            {
                                'ParameterKey': 'LambdaExecutionRoleName',
                                'ParameterValue': os.environ.get('LAMBDA_EXECUTION_ROLE_NAME', 'default-role-name')
                            }
                        ])  
    
if __name__ == "__main__":
    deploy_infrastructure()
    