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

        # an output artifact to connect source and build stages
        source_output = codepipeline.Artifact(artifact_name="github")

        # codebuild project to run tests
        run_tests_project = codebuild.PipelineProject(
            self,
            "RunTests",
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename="pipeline/buildspec.yml"
            ),
            description="Run the tests",
            timeout=core.Duration.minutes(10),
        )

        # codepipeline with source and build stages
        pipeline = codepipeline.Pipeline(
            self,
            "ShiftLeftPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.GitHubSourceAction(
                            oauth_token=github_token,
                            owner="vissree",
                            repo="testbed",
                            branch="master",
                            trigger=codepipeline_actions.GitHubTrigger.NONE,
                            action_name="PullChanges",
                            output=source_output,
                            run_order=1,
                        )
                    ],
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="RunTests",
                            input=source_output,
                            project=run_tests_project,
                            run_order=1,
                        )
                    ],
                ),
            ],
        )
