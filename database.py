"""SQlite wrapper for flask app"""
import sqlite3
from flask import g
def get_db():
    """finds database"""
    return sqlite3.connect("database.db")

def get_connection():
    """Connects to db"""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    """Executes a funtion into db"""
    if params is None:
        params=[]
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Finds most recent insertion"""
    return g.last_insert_id

def query(sql, params=None):
    """Preforms requested query in db"""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def query_one(sql, params=None):
    """Does a fetchone query in db"""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params). fetchone()
    con.close()
    return result
