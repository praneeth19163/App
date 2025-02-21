import sqlite3
from functools import wraps
from flask import g

def connect_db():
    sql = sqlite3.connect(r'C:\Users\PRANEETH\Desktop\demo\member.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def execute_query(db, query, args=()):
    db.execute(query, args)
    db.commit()

def fetch_one(db, query, args=()):
    cur = db.execute(query, args)
    return cur.fetchone()

def fetch_all(db, query, args=()):
    cur = db.execute(query, args)
    return cur.fetchall()
