#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.base_stack import BaseStack
from stacks.windows_ec2_stack import WindowsEc2Stack
from stacks.linux_ec2_stack import LinuxEc2Stack
from stacks.lambda_step_stack import LambdaStepStack

app = App()

env_name = app.node.try_get_context("env")  # dev or prod

# Multi-account mapping
if env_name == "dev":
    env_target = Environment(account="111111111111", region="us-east-1")
elif env_name == "prod":
    env_target = Environment(account="222222222222", region="us-east-1")
else:
    raise ValueError("env context must be dev or prod")

# --- Base Stack ---
base_stack = BaseStack(app, f"BaseStack-{env_name}", env_name=env_name, env=env_target)

# --- Windows EC2 ---
windows_stack = WindowsEc2Stack(
    app,
    f"WindowsEC2Stack-{env_name}",
    base_stack=base_stack,
    env_name=env_name,
    os_version="win2022",
    env=env_target
)

# --- Linux EC2 ---
linux_stack = LinuxEc2Stack(
    app,
    f"LinuxEC2Stack-{env_name}",
    base_stack=base_stack,
    env_name=env_name,
    os_version="al2023",
    env=env_target
)

# --- Lambda + Step Function ---
lambda_stack = LambdaStepStack(
    app,
    f"LambdaStepStack-{env_name}",
    env_name=env_name,
    env=env_target
)

app.synth()
