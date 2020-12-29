import json
import os

# if we're working locally, prepend /dev/ to the URL
root = "/dev/" if os.environ['IS_OFFLINE'] else "/"

#function to build the body object (it's a body builder, like Schwarzenegger!)
def the_govnuh(msg = "default message",dict = {}):      
    return {
        "message": msg,
        **dict,
    }

def hello(event, context):
    global root

    #default response when no other routes are matched
    body = the_govnuh("Go Serverless v1.0! Your function executed successfully!",{"event":event})

    qSP = event['queryStringParameters']

    if event['resource'] == root + "users/create":
        if qSP:
            body = the_govnuh("My bust size is " + qSP["bust"],{"input": qSP})
        else: 
            body = the_govnuh("Missing qSP")

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
