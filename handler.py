import json
import os
import mysql
import mysql.connector
from mysql.connector import Error

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

    #open wordpress db connection
    try: 
        mydb = mysql.connector.connect(
        host = '192.185.50.220',
        #port = 2083, #not sure I need port here, take it out and see what happens
        user = 'carolann_dbtest',
        password = '123456',
        auth_plugin = 'mysql_native_password',
        database = "carolann_moto_gear_fit_calculator",
        )
        print("MySQL connection open")
        cursor = mydb.cursor() 

        qSP = event['queryStringParameters']

        if event['resource'] == root + "users/create":
            #if query isn't null, write it to fc_users in the db
            if qSP:
                #body = the_govnuh("My bust size is " + qSP["bust"],{"input": qSP}) #original test message, replaced with db message below
                user_bust = qSP["bust"]
                sql = "INSERT INTO fc_users(user_bust) values(%s);"%(user_bust)
                cursor.execute(sql)
                mydb.commit()
                body = the_govnuh("My bust size is " + user_bust + ", writing to users.")

            else: 
                body = the_govnuh("Missing qSP")

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

    finally:
        if (mydb.is_connected()):
            cursor.close()
            mydb.close()
            print("MySQL connection is closed")    

    return response
