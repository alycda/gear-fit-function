import json


def hello(event, context):
    if event.resource == "/":
        body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            # "input": event.queryStringParameters,
            "event": event,
            # "context": context
        }

    elif event.resource == "/users/create":
        body = "Hello World"


    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
