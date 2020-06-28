#!/usr/bin/env python3

from aws_cdk import core
from vpc_baseline.vpc_baseline_stack import VpcBaselineStack

import yaml

CONFIG_FILE = "config.yaml"


# Parse the configuration file
# TODO: Validate the parameters
with open(CONFIG_FILE, "r") as cfg_file:
    cfg = yaml.safe_load(cfg_file)

env = core.Environment(region=cfg["vpc"]["region"])
app = core.App()
VpcBaselineStack(app, "vpc-baseline", env=env, config=cfg)

app.synth()
