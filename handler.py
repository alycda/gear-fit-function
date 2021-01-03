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
        nt_cursor = conn.cursor(named_Tuple = True)

        qSP = event['queryStringParameters']

        if event['resource'] == root + "users/create": #if query isn't null, write new record to fc_users in the db
            if qSP:
                #body = the_govnuh("My bust size is " + qSP["bust"],{"input": qSP}) #original test message, replaced with db message below
                user_bust = qSP["bust"]
                user_waist = qSP["waist"]
                sql = "INSERT INTO fc_users(user_bust,user_waist) values(%s,%s);"%(user_bust,user_waist)
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("My bust is " + user_bust + " inches, and my waist is " + user_waist + " inches. Writing to users.")
                #Call fr/create here if qSP has fr_info                
            else: 
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/get-many": #returns all data for user id's in a given range
            if qSP:
                id_mn = qSP["min"]
                id_max = qSP["max"]
                sql = "SELECT * FROM fc_users WHERE user_id BETWEEN %s AND %s;"%(id_min,id_max)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchmany() #res should be a list of named tuples, with each column name as the index
                for row in res:
                    user_id = row.user_id
                    user_bust = row.user_bust
                    user_waist = row.user_waist
                body = the_govnuh("The user id is " + user_id + ", the user bust is " + user_bust + ", and the user waist is " + user_waist + "./n")
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/get-one": #returns all data for a given user id
            if qSP:
                user = qSP["id"]
                sql = "SELECT * FROM fc_users WHERE user_id = %s;"%(user)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchone() #res should be a list of named tuples, with each column name as the index
                for row in res:
                    user_id = row.user_id
                    user_bust = row.user_bust
                    user_waist = row.user_waist
                body = the_govnuh("The user id is " + user_id + ", the user bust is " + user_bust + ", and the user waist is " + user_waist + "./n")
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/update": #updates any given values for a (mandatory) given user id
            if qSP:
                ### if the below doesn't work, try this instead
                # user_id = qSP["id"]
                # if qSP["bust"] and qSP["waist"]:
                #     user_bust = qSP["bust"]
                #     user_waist = qSP["waist"]
                #     sql = "UPDATE fc_users SET user_bust = %s AND user_waist = %s WHERE user_id = %s;"%(user_bust,user_waist,user_id) 
                # elif qSP["bust"]:
                #     user_bust = qSP["bust"]
                #     sql = "UPDATE fc_users SET user_bust = %s WHERE user_id = %s;"%(user_bust,user_id) 
                # elif qSP["waist"]:
                #     user_waist = qSP["waist"]
                #     sql = "UPDATE fc_users SET user_waist = %s WHERE user_id = %s;"%(user_waist,user_id) 
                # cursor.execute(sql)
                # conn.commit()
                # body = the_govnuh("The user id is " + user_id + ", the new user bust is " + user_bust + ", and the new user waist is " + user_waist + "./n")

                user_id = qSP["id"]
                def user_updater(user_id, **update):
                    #normal sql update: "UPDATE table SET col1 = val 1, col2 = val2... WHERE col9 = val9;"
                    query = "UPDATE fc_users SET "
                    for kw, arg in update.items():
                        if arg != 0 and arg is not None:
                            query += " %s = %s,"%(kw,arg)
                    query -= "," #strip last comma from query
                    query += " WHERE user_id = %s;"%(user_id)        
                    return query
                updates = {"user_bust":qSP["bust"],"user_waist":qSP["waist"],"user_derived_bust":qSP["der-bust"],"user_derived_waist":qSP["der-waist"]}
                sql = user_updater(user_id, updates)
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("The following values were updated for User %s: %s"%(user_id,updates))
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/delete": #deletes a single user identified by a given user id
            if qSP:
                user_id = qSP["id"]
                sql = "DELETE FROM fc_users WHERE user_id = %s LIMIT ONE;"%(user) #LIMIT ONE just to limit the damage if SQL accepts a wildcard for user id
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("User " + user_id + " has been deleted from the database./n")
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
