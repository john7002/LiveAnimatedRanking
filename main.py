# -*- coding:utf8 -*-
# !/usr/bin/env python


import urllib
import json
import os
import sqlite3
import time
import sys
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template

import requests

# Flask app should start in global layout
app = Flask(__name__)


dict_team = {"0": "Davy Crockett","1": "Billy the kid", "2": "Buffalo Bill", "3": "Tuniques Bleues", "4": "Daltons",
             "5": "Yakari", "6": "Cheyennes", "7": "Apaches", "8": "Iroquois",
             "9": "Sioux", "10": "Navajo", "11": "Visages pâles", "12": "Peaux Rouges",
             "13": "Calamity Jane", "14": "Ulysse 31", "15": "Helene et les garcons"}
global conn


@app.route('/handle_data', methods=['POST'])
def handle_data():
    global conn
    jeux = request.form['jeux']
    equipes = request.form['equipes']
    points = request.form['points']
    #juge_ip = request.environ['REMOTE_ADDR']

    print(f"{jeux},{equipes},{points}")

    url = "http://localhost:3000"
    data = {"equipe": equipes, "points": points}
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    print("poste message")

    cursor = conn.cursor()

    print(jeux)
    print(equipes)

    cursor.execute(
        """SELECT id,jeux,equipe,points FROM tournament WHERE jeux= ? AND equipe = ? """, (jeux, dict_team[equipes]))

    rows = cursor.fetchall()

    print(f'on lit {len(rows)}')

    if len(rows) == 0:
        try:
            r = requests.post(url, data=json.dumps(data),
                              headers=headers, timeout=5)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            sys.exit(1)
        except requests.exceptions.ReadTimeout as e:
            print(e)
        conn.execute("""
            INSERT INTO tournament(jeux,equipe,points) VALUES(?,?,?)""", (jeux, dict_team[equipes], points))
        success = 1
    else:
        print("already score for this team on this game")
        success = 2

    conn.commit()
    return render_template('mobile_jury.html', success=success, jeux=jeux)


@app.route('/handle_admin', methods=['POST'])
def handle_admin():
    equipes = request.form['equipes']
    points = request.form['points']
    print("on a {0} -- {1}".format(equipes, points))

    try:
        data = {"equipe": equipes, "points": points}
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        url = "http://localhost:3000"
        r = requests.post(url, data=json.dumps(data),
                          headers=headers, timeout=5)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        sys.exit(1)
    except requests.exceptions.ReadTimeout as e:
        print(e)

    conn.execute("""
        INSERT INTO tournament(jeux,equipe,points) VALUES(?,?,?)""", ("correction", dict_team[equipes], points))
    conn.commit()
    return "done !"


def webhook():
    return ""


@app.route('/jury/<page>')
def mobile_jury(page):

    if page in ['as', 'brute', 'bourricot', 'selle', 'tomahawk', 'soif', 'kwak', 'bandidos']:
        return render_template('mobile_jury.html', success=0, jeux=page)
    else:
        return 'no page found'


@app.route('/display')
def display_results():
    cursor = conn.cursor()
    cursor.execute("""SELECT id,jeux,equipe,points FROM tournament""")
    rows = cursor.fetchall()

    return render_template('display_result.html', data=rows)


@app.route('/admini')
def admin_results():
    return render_template('admin.html')


@app.route('/rebuild')
def rebuild_from_db():
    cursor = conn.cursor()
    cursor.execute("""SELECT equipe,points FROM tournament""")
    rows = cursor.fetchall()
    for row in rows:
 
        print("on a {0} de type {1} et {2} de type {3}".format(dict_team.keys()[dict_team.values().index(
            row[0])], type(dict_team.keys()[dict_team.values().index(row[0])]), row[1], type(row[1])))

        time.sleep(2)

    return "ok done !"


if __name__ == '__main__':
    try:
        global conn
        conn = sqlite3.connect('tournament_database.db',
                               check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournament(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            jeux TEXT,
            equipe TEXT,
            points INTEGER
        )
        """)
        conn.commit()

    except sqlite3.OperationalError:
        print('Erreur la table existe deja')
    except Exception as e:
        print('Erreur')
        conn.rollback()

    port = int(os.getenv('PORT', 5002))

    print("Starting app on port", port)

    app.run(debug=False, port=port, host='0.0.0.0')
