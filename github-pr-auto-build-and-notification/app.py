#!/usr/bin/env python3

from aws_cdk import core

from github_pr_auto_build_and_notification.github_pr_auto_build_and_notification_stack import GithubPrAutoBuildAndNotificationStack


app = core.App()
GithubPrAutoBuildAndNotificationStack(app, "github-pr-auto-build-and-notification")

app.synth()
