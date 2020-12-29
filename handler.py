import json
import os

# if we're working locally, prepend /dev/ to the URL
root = "/dev/" if os.environ['IS_OFFLINE'] else "/"


def hello(event, context):
    global root
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        # "input": event.queryStringParameters,
        "event": event
        # "context": context
    }

    if event['resource'] == root + "users/create":
        body = {
            "message": "Hello World"
        }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
