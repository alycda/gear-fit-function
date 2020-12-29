import json


def hello(event, context):
    # if event.get("resource") == "/":
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        # "input": event.queryStringParameters,
        "event": event
        # "context": context
    }

    # elif event.get("resource") == "/users/create":
    #     body = {
    #         "message": "Hello World"
    #     }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
