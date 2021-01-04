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
            else: 
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "gear/create": 
            if qSP:
                gear_type = qSP["type"]
                gear_brand = qSP["brand"]
                gear_name = qSP["name"]
                gear_size = qSP["size"]
                gear_bust = qSP["bust"]
                gear_waist = qSP["waist"]
                sql = "INSERT INTO fc_gear(gear_type,gear_brand,gear_name,gear_size,gear_derived_bust,gear_derived_waist) values(%s,%s,%s,%s,%s,%s);"%(gear_type,gear_brand,gear_name,gear_size,gear_bust,gear_waist)
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("New gear created! Gear type is %s, brand is %s, name is %s, size is %s, bust is %s, and waist is %s"%(gear_type,gear_brand,gear_name,gear_size,gear_bust,gear_waist))
            else: 
                body = the_govnuh("Missing qSP")
        
        if event['resource'] == root + "fr/create": 
            if qSP:
                fr_gear_id = qSP["gear"]
                fr_user_id = qSP["user"]
                fr_backpro = qSP["backpro"]
                fr_bust_adjust = qSP["bust"]
                fr_waist_adjust = qSP["waist"]
                sql = "INSERT INTO fc_fit_reports(fr_gear_id,fr_user_id,fr_backpro,fr_bust_adjust,fr_waist_adjust) values(%s,%s,%s,%s,%s);"%(fr_gear_id,fr_user_id,fr_backpro,fr_bust_adjust,fr_waist_adjust)
                cursor.execute(sql)
                conn.commit()
                body = the_govnuh("New fit report created! Gear ID is %s, user ID is %s, bust adjust is %s, and waist adjust is %s;"%(fr_gear_id,fr_user_id,fr_bust_adjust,fr_waist_adjust))
            else: 
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "users/get-many": #returns all data for all user id's in a given range
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
                        if row.user_derived_bust:
                            user_derived_bust = row.user_derived_bust
                        if row.user_derived_waist:
                            user_derived_waist = row.user_derived_waist
                        # body[user_id] = the_govnuh("The user id is " + str(user_id) + ", the user bust is " + str(user_bust) + ", and the user waist is " + str(user_waist) + ". ")
                        body[user_id] = the_govnuh("For user id %s, the bust is %s, the waist is %s, the derived bust is %s, and the derived waist is %s"%(user_id,user_bust,user_waist,user_derived_bust,user_derived_waist))
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "gear/get-many": #returns all data for all gear with a single given parameter (eg brand or name) #later can add size ranges
            if qSP:
                if qSP.get("gear") is not None:
                    gear_id = qSP["gear"]
                    sql = "SELECT * FROM fc_gear WHERE gear_id = %s;"%(gear_id) #this should only return 1 record
                if qSP.get("type") is not None:
                    gear_type = qSP["type"]
                    sql = "SELECT * FROM fc_gear WHERE gear_type = %s LIMIT 100;"%(gear_type)
                elif qSP.get("brand") is not None:
                    gear_brand = qSP["brand"]
                    sql = "SELECT * FROM fc_gear WHERE gear_brand = %s LIMIT 100;"%(gear_brand)
                elif qSP.get("name") is not None:
                    gear_name = qSP["name"]
                    sql = "SELECT * FROM fc_gear WHERE gear_name = %s LIMIT 100;"%(gear_name)                
                nt_cursor.execute(sql)
                res = nt_cursor.fetchall() #res should be a list of named tuples, with each column name as the index
                for row in res:
                    if row.gear_id: #checks if gear id exists, to protect against id's being out of range
                        gear_id = row.gear_id
                        gear_type = row.gear_type
                        gear_brand = row.gear_brand
                        gear_name = row.gear_name
                        gear_size = row.gear_size
                        gear_bust = row.gear_bust
                        gear_waist = row.gear_waist                        
                        body[user_id] = the_govnuh("For gear id %s, the gear type is %s, brand is %s, name is %s, size is %s, derived bust is %s, and derived waist is %s."%(gear_id,gear_type,gear_brand,gear_name,gear_size,gear_bust,gear_waist))
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "fr/get-many": #returns all fit reports for a given user id OR a given gear id
            if qSP:
                if qSP.get("gear") is not None:
                    fr_gear_id = qSP["gear"]
                    sql = "SELECT * FROM fc_fit_reports WHERE fr_gear_id = %s;"%(fr_gear_id)
                    nt_cursor.execute(sql)
                    res = nt_cursor.fetchall() #res should be a list of named tuples, with each column name as the index
                    for row in res:
                        if row.fr_id: #checks if record exists, to protect against id's being out of range
                            fr_id = row.fr_id
                            fr_user_id = row.fr_user_id
                            fr_backpro = row.fr_backpro
                            fr_bust_adjust = row.fr_bust_adjust
                            fr_waist_adjust = row.fr_waist_adjust
                            if row.gear_bust_est:
                                gear_bust_est = row.gear_bust_est
                            if row.gear_waist_est: 
                                gear_waist_est = row.gear_waist_est
                            if row.user_bust_est:
                                user_bust_est = row.user_bust_est
                            if row.user_waist_est:
                                user_waist_est = row.user_waist_est
                            body[fr_id] = the_govnuh("For fit report %s, the user is %s, back protector is %s, bust adjust is %s, and waist adjust is %s. The estimated bust of the item is %s, and the estimated waist of the item is %s. The estimated bust of the user is %s, and the estimated waist of the user is %s"%(fr_id,fr_user_id,fr_backpro,fr_bust_adjust,fr_waist_adjust,gear_bust_est,gear_waist_est,user_bust_est,user_waist_est))
                elif qSP.get("user") is not None:
                    fr_user_id = qSP["user"]
                    sql = "SELECT * FROM fc_fit_reports WHERE fr_user_id = %s;"%(fr_user_id)
                    nt_cursor.execute(sql)
                    res = nt_cursor.fetchall() #res should be a list of named tuples, with each column name as the index
                    for row in res:
                        if row.fr_id: #checks if record exists, to protect against id's being out of range
                            fr_id = row.fr_id
                            fr_gear_id = row.fr_gear_id
                            fr_backpro = row.fr_backpro
                            fr_bust_adjust = row.fr_bust_adjust
                            fr_waist_adjust = row.fr_waist_adjust
                            if row.gear_bust_est:
                                gear_bust_est = row.gear_bust_est
                            if row.gear_waist_est: 
                                gear_waist_est = row.gear_waist_est
                            if row.user_bust_est:
                                user_bust_est = row.user_bust_est
                            if row.user_waist_est:
                                user_waist_est = row.user_waist_est
                            body[fr_id] = the_govnuh("For fit report %s, the gear id is %s, back protector is %s, bust adjust is %s, and waist adjust is %s. The estimated bust of the item is %s, and the estimated waist of the item is %s. The estimated bust of the user is %s, and the estimated waist of the user is %s"%(fr_id,fr_gear_id,fr_backpro,fr_bust_adjust,fr_waist_adjust,gear_bust_est,gear_waist_est,user_bust_est,user_waist_est))
                else:
                    body = the_govnuh("Please specify whether you're looking by user or gear id. ")
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

        if event['resource'] == root + "gear/get-one": #returns all data for a given gear id
            if qSP:
                gear_id = qSP["id"]
                sql = "SELECT * FROM fc_gear WHERE gear_id = %s;"%(gear_id)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchone() #res is a list of named tuples, with each column name as the index
                gear_type = res.gear_type
                gear_brand = res.gear_brand
                gear_name = res.gear_name
                gear_size = res.gear_size
                gear_derived_bust = res.gear_derived_bust
                gear_derived_waist = res.gear_derived_waist
                body = the_govnuh("For gear id %s, the type is %s, the brand is %s, the name is %s, the size is %s, the derived bust is %s, and the derived waist is %s"%(gear_id,gear_type,gear_brand,gear_name,gear_size,gear_derived_bust,gear_derived_waist))
            else:
                body = the_govnuh("Missing qSP")

        if event['resource'] == root + "fr/get-one": #returns all data for a given fit report id
            if qSP:
                fr_id = qSP["id"]
                sql = "SELECT * FROM fc_fit_reports WHERE fr_id = %s;"%(fr_id)
                nt_cursor.execute(sql)
                res = nt_cursor.fetchone() #res is a list of named tuples, with each column name as the index
                if res.fr_id:
                    fr_gear_id = res.fr_gear_id
                    fr_user_id = res.fr_user_id
                    fr_backpro = res.fr_backpro
                    fr_bust_adjust = res.fr_bust_adjust
                    fr_waist_adjust = res.fr_waist_adjust
                    if row.gear_bust_est:
                        gear_bust_est = row.gear_bust_est
                    if row.gear_waist_est: 
                        gear_waist_est = row.gear_waist_est
                    if row.user_bust_est:
                        user_bust_est = row.user_bust_est
                    if row.user_waist_est:
                        user_waist_est = row.user_waist_est
                    body = the_govnuh("For fit report %s, the gear id is %s, back protector is %s, bust adjust is %s, and waist adjust is %s. The estimated bust of the item is %s, and the estimated waist of the item is %s. The estimated bust of the user is %s, and the estimated waist of the user is %s"%(fr_id,fr_gear_id,fr_backpro,fr_bust_adjust,fr_waist_adjust,gear_bust_est,gear_waist_est,user_bust_est,user_waist_est))
                else:
                    body = the_govnuh("Fit report ID %s does not exist. "%(fr_id))
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
