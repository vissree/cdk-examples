from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import aws_apigateway as apigw


class GithubPrAutoBuildAndNotificationStack(core.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda function to comment on PR
        notify_build_start = _lambda.Function(
            self,
            "NotifyBuildStart",
            handler="notify_build_start.main",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("source"),
            environment={
                "GITHUB_ACCESS_TOKEN_PATH": self.node.try_get_context(
                    "github_access_token_path"
                )
            },
        )

        # Add SSM and KMR access to execution role
        # to read the Github token from parameter
        # store
        notify_build_start.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "kms:Decrypt"],
                effect=iam.Effect.ALLOW,
                resources=["*"],
            )
        )

        # Create an API gateway endpoint to use as the
        # Github webhook
        apigw.LambdaRestApi(
            self,
            "GithubWebhookApi",
            handler=notify_build_start,
            endpoint_types=[apigw.EndpointType.REGIONAL],
        )
