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

    #open db connection
    try: 
        conn = mysql.connector.connect(
        host = os.environ.get('GEAR_CALC_HOST'),
        user = os.environ.get('GEAR_CALC_USER'),
        password = os.environ.get('GEAR_CALC_PASSWORD'),
        auth_plugin = 'mysql_native_password', #when testing in vscode, the mysql extension only supported this older authentication scheme. Might be able to upgrade now
        database = os.environ.get('GEAR_CALC_DATABASE'),
        )
        print("MySQL connection open")
        cursor = conn.cursor() 

        qSP = event['queryStringParameters']

        if event['resource'] == root + "users/create":
            #if query isn't null, write it to fc_users in the db
            if qSP:
                #body = the_govnuh("My bust size is " + qSP["bust"],{"input": qSP}) #original test message, replaced with db message below
                user_bust = qSP["bust"]
                user_waist = qSP["waist"]
                sql = "INSERT INTO fc_users(user_bust,user_waist) values(%s,%s);"%(user_bust,user_waist)
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("My bust is " + user_bust + " inches, and my waist is " + user_waist + " inches. Writing to users.")
                #need to add fit report values to fit_reports table.
                #after all user-supplied values are added, close db connection. Will reopen it to return results but this will get it to update autoincremented id's.
                #cursor.close()
                #conn.close()

                #need to add a function to return best fit results here


            else: 
                body = the_govnuh("Missing qSP")

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

    finally:
        if (conn.is_connected()):
            cursor.close()
            conn.close()
            print("MySQL connection is closed")    

    return response
