# -*- coding: utf-8 -*-

import mysql.connector as sql
import sys
import csv

# get records from csv-file as a list      
def read_csv(fname='test.csv')->list:
    res = []
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for data in reader:
            res.append(data)
            
    return res

# get database connection
def get_connection(db, psw, username):
    try:
        cnx = sql.connect(user=username, password=psw, database=db)
        return cnx
    except Exception as e:
        print(e)

# get table column names and records as lists     
def get_data_list(connection: sql.MySQLConnection, 
                   query_text:str,reset=True):
    try:
        cur_con = connection
        if reset:
            cur_con.reset_session()
        cursor = cur_con.cursor()
        query = query_text
        cursor.execute(query)
        res = cursor.fetchall() 
        cols = cursor.column_names
        cursor.close()
        cur_con.close()
        return (res, cols)
    
    except Exception as e:
        print(e)
  
# execute insert query       
def insert_data(connection: sql.MySQLConnection, insert_query:str,vals:list, reset=True):
    ''' An argument is a query or parameterized query + list of values'''
    
    try:
        cur_con = connection
        if reset:
            cur_con.reset_session()
          
        cursor = cur_con.cursor()
        cursor.executemany(insert_query, vals)
        cur_con.commit()
        print(cursor.rowcount, " rows inserted.")
        cursor.close()
        cur_con.close()
        
    except Exception as e:
        print(e)
 
# execute delete query    
def delete_data(connection: sql.MySQLConnection, del_query:str, reset=True):
    try:
        cur_con = connection
        if reset:
            cur_con.reset_session()
          
        cursor = cur_con.cursor()
        cursor.execute(del_query)
        cur_con.commit()
        print(cursor.rowcount, " record(s) deleted.")
        cursor.close()
        cur_con.close()
        
    except Exception as e:
        print(e)

# execute update query
def update_data(connection: sql.MySQLConnection, upd_query:str, reset=True):
    try:
        cur_con = connection
        if reset:
            cur_con.reset_session()
          
        cursor = cur_con.cursor()
        cursor.execute(upd_query)
        cur_con.commit()
        print(cursor.rowcount, " record(s) affected.")
        cursor.close()
        cur_con.close()
        
    except Exception as e:
        print(e)