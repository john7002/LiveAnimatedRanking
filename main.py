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
from flask_socketio import SocketIO, emit

import requests

# Flask app should start in global layout
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")#, async_mode='eventlet')




dict_team = {"0": "Les Daisy","1": "Les Golden Boy", "2": "Les flappers", "3": "Les wolf pack", "4": "Les peaky blinders",
             "5": "La black mafia", "6": "Les Miami boys", "7": "Les faucheurs de Long Island", "8": "Charleston mob",
             "9": "Les fantômes de gasby", "10": "Baltimore crew", "11": "Jazmafia", "12": "Dickson blood",
             "13": "Dycksy mafia", "14": "Le gang d'Eddy Nach", "15": "Chipiro brothers"}
global conn




@app.route('/handle_data', methods=['POST'])
def handle_data():
    global conn
    jeux = request.form['jeux']
    equipes = request.form['equipes']
    points = request.form['points']

    print(f"{jeux},{equipes},{points}")

    cursor = conn.cursor()
    cursor.execute(
        """SELECT id,jeux,equipe,points FROM tournament 
        WHERE jeux= ? AND equipe = ? """, 
        (jeux, dict_team[equipes])
    )

    rows = cursor.fetchall()

    if len(rows) == 0:
        # Émission unique avec syntaxe corrigée
        socketio.emit('score_update', {
            'equipe': equipes,
            'points': points
        }, broadcast=True)  # Pas de '=True' ici
        
        conn.execute("""
            INSERT INTO tournament(jeux,equipe,points) 
            VALUES(?,?,?)""", 
            (jeux, dict_team[equipes], points))
        success = 1
    else:
        print("Score déjà existant")
        success = 2

    conn.commit()
    return render_template('mobile_jury.html', success=success, jeux=jeux)




@app.route('/handle_admin', methods=['POST'])
def handle_admin():
    equipes = request.form['equipes']
    points = request.form['points']
    print("on a {0} -- {1}".format(equipes, points))

    socketio.emit('score_update', {
            'equipe': equipes,
            'points': points
        }, broadcast=True)

    conn.execute("""
        INSERT INTO tournament(jeux,equipe,points) VALUES(?,?,?)""", ("correction", dict_team[equipes], points))
    conn.commit()
    return "done !"


def webhook():
    return ""


@app.route('/jury/<page>')
def mobile_jury(page):

    if page in ['GoldTwister', 'peluche', 'pyramide', 'roulette', 'cocktail', 'parcours', 'cassetete', 'gonflable']:
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
        team_name = [k for k, v in dict_team.items() if v == row[0]][0]
    
        print(f"On a {team_name} de type {type(team_name)} et {row[1]} de type {type(row[1])}")
        
        socketio.emit('score_update', {
            'equipe': team_name,
            'points': row[1]
        }, broadcast=True)

        time.sleep(2)

    return "ok done !"


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@app.route('/')
def display_ranking():
    return render_template('main.html')

def send_score_update(equipe, points):
    socketio.emit('score_update', {'equipe': equipe, 'points': points})



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

    if __name__ == '__main__':
        # pour la prod
        socketio.run(app, host='0.0.0.0', port=5002, allow_unsafe_werkzeug=True)
        #pour le test local
        #socketio.run(app, host='0.0.0.0', port=5002)

