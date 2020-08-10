from helpers.helper_version_control import GithubWrapper
from helpers.aws.helper_ssm import SSMServiceClass
import json
import os


ssm = SSMServiceClass()
GITHUB_ACCESS_TOKEN = ssm.get_secret(os.getenv("GITHUB_ACCESS_TOKEN_PATH"))


def main(event, context):
    if not GITHUB_ACCESS_TOKEN:
        print("Empty Github access token, exiting")
        raise RuntimeError("Empty Github access token")

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
        repo_name = payload["repository"]["full_name"]
    except KeyError as e:
        print(json.dumps(payload))
        raise e

    # Validate if this is a pull_request event and the PR state is open
    if event_type != "pull_request":
        raise RuntimeWarning("Received event is not related to pull requests")
    elif state != "open":
        raise RuntimeWarning("PR state is not open, ignore")
    else:
        github = GithubWrapper(repo_name, GITHUB_ACCESS_TOKEN)
        github.add_pr_comment(
            number,
            "Comment added by lambda invocation {}".format(context.aws_request_id),
        )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": "Received",
    }
