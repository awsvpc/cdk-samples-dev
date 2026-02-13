from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    Tags,
    Environment
)
from constructs import Construct
import os

class LambdaCronStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str, lambda_layer_version=None, **kwargs):
        super().__init__(scope, id, **kwargs)

        # --- Tags ---
        Tags.of(self).add("Application", "MyApp")
        Tags.of(self).add("Description", "Daily Lambda Cron Workflow")
        Tags.of(self).add("Env", env_name)
        Tags.of(self).add("Email", "team@example.com")

        # --- Lambda Layer ---
        if lambda_layer_version is None:
            layer = _lambda.LayerVersion(
                self,
                "SharedLayer",
                code=_lambda.Code.from_asset("lambda/layers/shared_lib"),
                compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
                description="Shared Lambda Layer for utils"
            )
        else:
            layer = lambda_layer_version

        # --- Lambda2 ---
        lambda2 = _lambda.Function(
            self,
            "Lambda2",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda/lambda2"),
            layers=[layer],
            environment={
                "MY_ENV": env_name,
            },
            memory_size=256,
            timeout=Duration.seconds(30),
        )

        # --- Lambda1 ---
        lambda1 = _lambda.Function(
            self,
            "Lambda1",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda/lambda1"),
            layers=[layer],
            environment={
                "MY_ENV": env_name,
                "LAMBDA2_NAME": lambda2.function_name
            },
            memory_size=256,
            timeout=Duration.seconds(30),
        )

        # --- Permissions: Lambda1 can invoke Lambda2 ---
        lambda2.grant_invoke(lambda1)

        # --- EventBridge Rule: Daily 4AM UTC ---
        rule = events.Rule(
            self,
            "Daily4AMRule",
            schedule=events.Schedule.cron(minute="0", hour="4")
        )
        rule.add_target(targets.LambdaFunction(lambda1))

        # --- Allow EventBridge to invoke Lambda1 ---
        lambda1.add_permission(
            "AllowEventBridgeInvoke",
            principal=iam.ServicePrincipal("events.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=rule.rule_arn
        )

        # --- Outputs ---
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.layer = layer
        self.event_rule = rule
