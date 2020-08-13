from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam
from aws_cdk import core


class GithubPrAutoBuildAndNotificationStack(core.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        repo_owner = self.node.try_get_context("github_repo_owner")
        repo_name = self.node.try_get_context("github_repo_name")

        # Github oauth token
        github_token = core.SecretValue.secrets_manager(
            self.node.try_get_context("github_access_token_path"),
            json_field="token",
        )

        # Github source credentials
        github_creds = codebuild.GitHubSourceCredentials(
            self, "GithubCredentials", access_token=github_token
        )

        # Codebuild project to run tests
        run_tests_project = codebuild.Project(
            self,
            "RunTests",
            badge=True,
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename="pipeline/buildspec.yml"
            ),
            source=codebuild.Source.git_hub(
                owner=repo_owner, repo=repo_name, clone_depth=1, webhook=False,
            ),
            description="Run the tests",
            timeout=core.Duration.minutes(10),
        )

        # Lambda function to trigger the build on PR creation 
        notify_build_start = _lambda.Function(
            self,
            "NotifyBuildStart",
            handler="start_build.main",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("lambda"),
            environment={
                "CODEBUILD_PROJECT_NAME": run_tests_project.project_name
            },
        )

        # Permission to trigger Codebuild project
        notify_build_start.add_to_role_policy(
            iam.PolicyStatement(
                actions=["codebuild:StartBuild"],
                effect=iam.Effect.ALLOW,
                resources=[run_tests_project.project_arn],
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
