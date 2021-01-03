import json
import os
import mysql
import mysql.connector
from mysql.connector import Error

#should define a "connector" constructor here so we can call it instead of writing it out each time. Need to call cursor() and conn() from other functions.
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

