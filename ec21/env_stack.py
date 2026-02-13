from aws_cdk import App, Environment
from my_stacks.postgres_rds_stack import PostgresRdsStack

app = App()

# Use context to select environment
env_name = app.node.try_get_context("env")

if env_name == "dev":
    target_env = Environment(account="111111111111", region="us-east-1")
elif env_name == "prod":
    target_env = Environment(account="222222222222", region="us-east-1")
else:
    raise ValueError("Invalid env context")

PostgresRdsStack(
    app,
    f"Postgres-{env_name}",
    env=target_env
)

app.synth()

"""
cdk deploy Postgres-dev -c env=dev --profile dev
cdk deploy Postgres-prod -c env=prod --profile prod
"""
