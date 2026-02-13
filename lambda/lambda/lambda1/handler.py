import os
import boto3

lambda_client = boto3.client("lambda")

def handler(event, context):
    print("Lambda1 triggered")
    print("ENV VAR:", os.environ.get("MY_ENV"))

    # Invoke Lambda2
    response = lambda_client.invoke(
        FunctionName=os.environ.get("LAMBDA2_NAME"),
        InvocationType="Event"
    )
    print("Invoked Lambda2:", response)
    return {"status": "Lambda1 completed"}
