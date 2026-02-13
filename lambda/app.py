#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.lambda_cron_stack import LambdaCronStack

app = App()

env_name = app.node.try_get_context("env")  # dev, qa, prod

env_mapping = {
    "dev": Environment(account="111111111111", region="us-east-1"),
    "qa": Environment(account="222222222222", region="us-east-1"),
    "prod": Environment(account="333333333333", region="us-east-1"),
}

if env_name not in env_mapping:
    raise ValueError("Invalid env context")

LambdaCronStack(
    app,
    f"LambdaCronStack-{env_name}",
    env_name=env_name,
    env=env_mapping[env_name]
)

app.synth()
