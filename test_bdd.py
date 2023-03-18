#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

try:
    conn = sqlite3.connect('database.db')
    cursor=conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT,
        age INTEGER
    )
    """)
    conn.commit()
    cursor.execute("""
    INSERT INTO users(name,age) VALUES(?,?)""", ('olivier',30))

    cursor.execute("""
    INSERT INTO users(name,age) VALUES(?,?)""", ('Jean',44))


    cursor.execute("""SELECT id,name,age FROM users""")
    rows = cursor.fetchall()
    for row in rows:
        print ('{0} : {1} - {2}'.format(row[0],row[1],row[2]))



except sqlite3.OperationalError:
    print('Erreur la table existe deja')
except Exception as e:
    print('Erreur')
    conn.rollback()
finally:
    conn.close()
