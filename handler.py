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

#should define a "connector" constructor here so we can call it instead of writing it out each time. Need to call cursor() and conn().
def connector():
    try:
        conn = mysql.connector.connect(
        host = os.environ.get('GEAR_CALC_HOST'),
        user = os.environ.get('GEAR_CALC_USER'),
        password = os.environ.get('GEAR_CALC_PASSWORD'),
        auth_plugin = 'mysql_native_password', #when testing in vscode, the mysql extension only supported this older authentication scheme. Might be able to upgrade now
        database = os.environ.get('GEAR_CALC_DATABASE'),
        )
        cursor = conn.cursor() 
    return cursor
    #pass

#these (gear and user updaters) are actually independent of any form submissions, though they should be called after each form submission. Should they have their own file, or a functions.py?
def gear_updater(gear_id):
    #call connector() here to open conn to db
    bust_records = []
    sql = "SELECT gear_bust_est FROM fc_fit_reports WHERE fr_gear_id = %s"%(gear_id)
    cursor.execute(sql)
    res = cursor.fetchall()
    for row in res:
        bust_records.append(float(row[0]))
    bust = sum(bust_records)/len(bust_records)
    #repeat the above, but now for waist (later hip and inseam). Will need an if statement to determine what dimensions the gear has, eg pants won't have a bust.

    #save new bust, waist, etc. to gear table as derived values
    pass

def user_updater(user_id):
    #open conn to db

    pass

def hello(event, context):
    global root

    #default response when no other routes are matched
    body = the_govnuh("Go Serverless v1.0! Your function executed successfully!",{"event":event})

    #open wordpress db connection
    try: 
        conn = mysql.connector.connect(
        host = '192.185.50.220',
        #port = 2083, #not sure I need port here, take it out and see what happens #it works! I don't need port apparently
        user = 'carolann_dbtest',
        password = '123456',
        auth_plugin = 'mysql_native_password', #when testing in vscode, the mysql extension only supported this older authentication scheme. Might be able to upgrade now
        database = "carolann_moto_gear_fit_calculator",
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
                cursor.close()
                conn.close()

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
