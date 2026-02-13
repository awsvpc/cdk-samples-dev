import os

def handler(event, context):
    print("Lambda2 triggered")
    print("ENV VAR:", os.environ.get("MY_ENV"))
    return {"status": "Lambda2 completed"}
