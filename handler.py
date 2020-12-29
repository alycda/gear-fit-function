import json
import os


def hello(event, context):
    body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            # "input": event.queryStringParameters,
            "event": event
            # "context": context
        }
    # print('Body default, not if statement')
    print(os.environ['IS_OFFLINE'])
    # print(event.get("resource"))
    # print(event["resource"])
    
    if os.environ['IS_OFFLINE']:
        if event['resource'] == "/dev/users/create":
            body = {
                "message": "Hello World"
            }
            print('Body default, not if statement, IS_OFFLINE = true')

    else:
        if event["resource"] == "/users/create":
            body = {
                "message": "Hello World"
            }
            print('Body default, not if statement, remote')

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
