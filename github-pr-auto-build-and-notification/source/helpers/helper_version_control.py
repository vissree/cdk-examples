from github import Github
from github.GithubException import GithubException, BadCredentialsException


class GithubWrapper():
    """
    Wrapper class for Github api
    """

    def __init__(self, repo_name, access_token):
        try:
            self.github = Github(access_token)
            self.repo = self.github.get_repo(repo_name)
        except BadCredentialsException as e:
            print("Invalid Access Token")
            raise e
        except GithubException as e:
            print("Error getting repository details, check log for details")
            raise e

    def add_pr_comment(self, number, body):
        """
        Add an issue comment to the given pull request
        """
        try:
            pr = self.repo.get_pull(number)
        except GithubException as e:
            if e.status == 404:
                print("Invalid pull request number {}".format(number))
            else:
                print("Cannot retrieve pull request, check log for details")

            raise e

        # add comment
        try:
            pr.create_issue_comment(body)
        except GithubException as e:
            if e.status == 403:
                print("Insufficient permissions to add comment")
            else:
                print(
                    "Error adding issue comment to pull request {}".format(
                        number
                    )
                )

            raise e
