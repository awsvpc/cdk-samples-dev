from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks
)
from constructs import Construct

class LambdaStepStack(Stack):
    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        fn = _lambda.Function(
            self,
            "HelloLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.handler",
            code=_lambda.Code.from_inline(
                "def handler(event, context):\n    print('Hello World')\n    return {'status':'ok'}"
            )
        )

        task = tasks.LambdaInvoke(
            self,
            "InvokeHelloLambda",
            lambda_function=fn,
            output_path="$.Payload"
        )

        sf = sfn.StateMachine(
            self,
            "HelloStateMachine",
            definition=task
        )

        self.state_machine = sf
        self.lambda_fn = fn
