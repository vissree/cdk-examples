from aws_cdk import core
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_codebuild as codebuild


class CodepipelineAndCodebuildStack(core.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Github oauth token
        github_token = core.SecretValue.secrets_manager(
            self.node.try_get_context("github_access_token_path"),
            json_field="token",
        )

        # Github source credentials
        github_creds = codebuild.GitHubSourceCredentials(
            self, "GithubCredentials", access_token=github_token
        )

        # codebuild project to run tests
        run_tests_project = codebuild.Project(
            self,
            "RunTests",
            badge=True,
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename="pipeline/buildspec.yml"
            ),
            source=codebuild.Source.git_hub(
                owner="vissree", repo="testbed", clone_depth=1, webhook=False,
            ),
            description="Run the tests",
            timeout=core.Duration.minutes(10),
        )
