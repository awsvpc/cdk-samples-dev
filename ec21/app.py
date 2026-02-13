#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.base_stack import BaseStack
from stacks.windows_ec2_stack import WindowsEc2Stack
from stacks.linux_ec2_stack import LinuxEc2Stack
from stacks.lambda_step_stack import LambdaStepStack

app = App()

env_name = app.node.try_get_context("env")  # dev, prod

if env_name == "dev":
    env_target = Environment(account="111111111111", region="us-east-1")
elif env_name == "prod":
    env_target = Environment(account="222222222222", region="us-east-1")
else:
    raise ValueError("env context must be dev or prod")

# Base stack (IAM role, SSM param, SG)
base = BaseStack(app, f"BaseStack-{env_name}", env=env_target, env_name=env_name)

# Windows EC2 stack
windows = WindowsEc2Stack(
    app, f"WindowsEC2Stack-{env_name}",
    env=env_target,
    base_stack=base,
    env_name=env_name,
    os_version="win2022"
)

# Linux EC2 stack
linux = LinuxEc2Stack(
    app, f"LinuxEC2Stack-{env_name}",
    env=env_target,
    base_stack=base,
    env_name=env_name,
    os_version="al2023"
)

# Lambda + Step Function
lambda_stack = LambdaStepStack(
    app, f"LambdaStepStack-{env_name}",
    env=env_target,
    env_name=env_name
)

app.synth()
