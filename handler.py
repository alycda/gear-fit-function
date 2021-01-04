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
        nt_cursor = conn.cursor(named_tuple=True)

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
                id_min = qSP["min"]
                id_max = qSP["max"]
                sql = "SELECT * FROM fc_users WHERE user_id BETWEEN %s AND %s;"%(id_min,id_max)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchall() #res should be a list of named tuples, with each column name as the index
                for row in res:
                    if row.user_id: #checks if user id exists, to protect against user id's being out of range
                        user_id = row.user_id
                        user_bust = row.user_bust
                        user_waist = row.user_waist
                        body[user_id] = the_govnuh("The user id is " + str(user_id) + ", the user bust is " + str(user_bust) + ", and the user waist is " + str(user_waist) + ". ")
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/get-one": #returns all data for a given user id
            if qSP:
                user = qSP["id"]
                sql = "SELECT * FROM fc_users WHERE user_id = %s;"%(user)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchone() #res is a list of named tuples, with each column name as the index
                user_id = res.user_id
                user_bust = res.user_bust
                user_waist = res.user_waist
                body = the_govnuh("The user id is " + str(user_id) + ", the user bust is " + str(user_bust) + ", and the user waist is " + str(user_waist) + "./n")
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/update": #updates any given values for a (mandatory) given user id
            if qSP:
                user_id = qSP["id"]
                if (qSP.get("bust") is not None and qSP.get("waist") is not None):
                    user_bust = qSP["bust"]
                    user_waist = qSP["waist"]
                    sql = "UPDATE fc_users SET user_bust = %s, user_waist = %s WHERE user_id = %s;"%(user_bust,user_waist,user_id) 
                    body = the_govnuh("The user id is " + str(user_id) + ", the new user bust is " + str(user_bust) + ", and the new user waist is " + str(user_waist) + ". ")
                    cursor.execute(sql)
                    conn.commit()
                elif (qSP.get("bust") is not None):
                    user_bust = qSP["bust"]
                    sql = "UPDATE fc_users SET user_bust = %s WHERE user_id = %s;"%(user_bust,user_id) 
                    body = the_govnuh("The user id is " + str(user_id) + " and the new user bust is " + str(user_bust) + ". ")
                    cursor.execute(sql)
                    conn.commit()
                elif (qSP.get("waist") is not None):
                    user_waist = qSP["waist"]
                    sql = "UPDATE fc_users SET user_waist = %s WHERE user_id = %s;"%(user_waist,user_id) 
                    body = the_govnuh("The user id is " + str(user_id) + " and the new user waist is " + str(user_waist) + ". ")
                    cursor.execute(sql)
                    conn.commit()
                else:
                    body = the_govnuh("Please specify a measurement to update for user " + str(user_id) + ". ")
                # body = the_govnuh("The user id is " + str(user_id) + ", the new user bust is " + str(user_bust) + ", and the new user waist is " + str(user_waist) + ". ")

                # probably need to parse the query contents in order to make the below work. EG, if query contains bust, user_bust = qSP["bust"]
                # user_id = qSP["id"]
                # def user_updater(user_id, **update):
                #     #normal sql update: "UPDATE table SET col1 = val 1, col2 = val2... WHERE col9 = val9;"
                #     query = "UPDATE fc_users SET "
                #     for key, value in update.items():
                #         if value > 0:
                #             query += " %s = %s,"%(key,value)
                #     query -= "," #strip last comma from query
                #     query += " WHERE user_id = %s;"%(user_id)        
                #     return query
                # fields = {"user_bust":qSP["bust"],"user_waist":qSP["waist"],"user_derived_bust":qSP["der-bust"],"user_derived_waist":qSP["der-waist"]}
                # updates = {}
                # for key,value in fields.items():
                #     if value is not None:
                #         updates[key] = value
                # sql = user_updater(user_id, updates)
                # cursor.execute(sql)
                # conn.commit()
                # body = the_govnuh("The following values were updated for User %s: %s"%(user_id,updates))
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/delete": #deletes a single user identified by a given user id
            if qSP:
                user_id = qSP["id"]
                sql = "DELETE FROM fc_users WHERE user_id = %s LIMIT 1;"%(user_id) #LIMIT 1 just to limit the damage if SQL accepts a wildcard for user id
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("User " + str(user_id) + " has been deleted from the database.")
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
