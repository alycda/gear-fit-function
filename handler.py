import json
import os

# if we're working locally, prepend /dev/ to the URL
root = "/dev/" if os.environ['IS_OFFLINE'] else "/"

def the_govnuh(msg = "desfult message"):         #function to build the body object (it's a body builder, like Schwarzenegger!)
    return {
        "message": msg
    }

def hello(event, context):
    global root

    body = the_govnuh("Go Serverless v1.0! Your function executed successfully!")

    # body = {          #default response when no other routes are matched
    #     "message": "Go Serverless v1.0! Your function executed successfully!",
    #     # "input": event['queryStringParameters'],
    #     "event": event
    #     # "context": context
    # }

    if event['resource'] == root + "users/create":
        if event['queryStringParameters']:
            body = {
                "message": "Hello World",
                "input": event['queryStringParameters'],
                "bob": "My bust size is " + event['queryStringParameters']["bust"],
            }
        else: 
            body = {
                "message": "Missing qSP",
            }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
