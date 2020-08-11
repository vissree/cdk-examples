from botocore.exceptions import ClientError
from botocore.config import Config
import boto3
import json
import os

CODEBUILD_PROJECT_NAME = os.getenv("CODEBUILD_PROJECT_NAME")

try:
    codebuild = boto3.client("codebuild", config=Config(retries={"max_attempts": 3}))
except ClientError as e:
    print("Client error during initialization: {}".format(e))
    raise e

def main(event, context):
    try:
        payload = json.loads(event["body"])
    except json.decoder.JSONDecodeError as e:
        print("Error decoding string: {}".format(event["body"]))
        raise e
    except TypeError as e:
        print("Received empty body")
        raise e

    try:
        # TODO: need to check if there are chances of multiple events in one hook
        event_type = event["multiValueHeaders"]["X-GitHub-Event"][0]

        action = payload["action"]
        state = payload["pull_request"]["state"]
        number = payload["number"]
    except KeyError as e:
        print(json.dumps(payload))
        raise e

    # Validate if this is a pull_request event and the PR state is open
    if event_type != "pull_request":
        raise RuntimeWarning("Received event is not related to pull requests")

    if state != "open":
        raise RuntimeWarning("PR state is not open, ignore")

    # start the build
    try:
        response = codebuild.start_build(
            projectName=CODEBUILD_PROJECT_NAME,
            sourceVersion="pr/{}".format(number),
            reportBuildStatusOverride=True,
            buildStatusConfigOverride={
                "context": "Codebuild",
            }
        )
    except ClientError as e:
        print("Client error triggering build: {}".format(e))
        raise e

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": "Received",
    }
