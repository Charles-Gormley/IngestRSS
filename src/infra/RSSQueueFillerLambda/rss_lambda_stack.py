# File: rss_lambda_stack.py
import os
from dotenv import load_dotenv
load_dotenv()

from aws_cdk import (
    App,
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration
)
from constructs import Construct

class SqsFillerLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda Function
        self.sqs_filler = _lambda.Function(
            self, "SqsFillerFunction",
            function_name=os.getenv("QUEUE_FILLER_LAMBDA_NAME"),
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset("src/infra/RSSQueueFillerLambda/lambda"),
            timeout=Duration.minutes(5),
            environment={
                "SQS_QUEUE_URL": os.getenv("SQS_QUEUE_URL"),
                "DYNAMODB_TABLE_NAME": os.getenv("DYNAMODB_TABLE_NAME")
            }
        )

        # Grant Lambda permission to scan DynamoDB
        self.sqs_filler.add_to_role_policy(iam.PolicyStatement(
            actions=["dynamodb:Scan"],
            resources=[os.getenv("DYNAMODB_TABLE_ARN")]
        ))

        # Grant Lambda permission to send messages to SQS
        self.sqs_filler.add_to_role_policy(iam.PolicyStatement(
            actions=["sqs:SendMessage"],
            resources=[os.getenv("SQS_QUEUE_ARN")]
        ))

# Main
if __name__ == "__main__":
    app = App()
    SqsFillerLambdaStack(app, "SqsFillerLambdaStack")
    app.synth()