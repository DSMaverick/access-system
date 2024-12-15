import os
import calendar
from datetime import datetime
import string
import random
import base64
import sys
import sqlite3
import time
import pandas as pd
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask import send_from_directory
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_file
import backend
from machine_learning import run_face_recognition

persoane_autorizate = set(['Sebastian Delorean']) #Hardcoded

name_to_id = dict()
name_to_id['Sebastian Delorean'] = 1
design = {0: 'off', 1: 'on'}

app = Flask(__name__, static_folder='resources')  #Create the application instance setting static folder as 'resources'
app.config.from_object(__name__)  #Load config from this file , flaskr.py
app.config['CORS_HEADERS'] = 'Content-Type'

#Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'angajati.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def epoch_to_iso(seconds):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ',
                         time.localtime(seconds))

def seconds_to_hours(seconds):
    return str(datetime.timedelta(seconds=seconds))

#Create database if it doesnt exist
conn = sqlite3.connect('angajati.db', check_same_thread=False)
try:
    conn.execute('''CREATE TABLE IF NOT EXISTS angajati (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        access_time TEXT NOT NULL
                    );''')
    conn.commit()
except sqlite3.OperationalError as e:
    print(f"Error: {e}")

#Init database
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    print("Schema.sql executata cu success.")
    db.commit()

#Update
def update_db():
    db = get_db()
    try:
        db.execute('''CREATE TABLE IF NOT EXISTS angajati (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        access_time TEXT NOT NULL
                      );''')
        db.commit()
    except sqlite3.OperationalError as e:
        print(f"Error occurred: {e}")

#Conect
def connect_db():
    """Se conecteaza la baza de date."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.teardown_appcontext
def close_db(error):
    """Inchide baza de date la sf requestului."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_db():
    """Deschide o conexiune la baza de date daca nu e deschisa niciuna."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#Flask routes
@app.route('/raspi', methods=['POST'])
def raspi_post():
    image_data = request.form['image']
    extension = request.form['extension']
    N = 10
    # Random string generation for image files
    filename = ''.join(random.choices(
                       string.ascii_uppercase + string.digits, k=N))
    with open(str("./static/" + filename) + "." + str(extension), "wb") as fh:
        fh.write(base64.decodebytes(image_data.encode()))
    final_filename = './static/' + filename + '.' + str(extension)
    ml_name = run_face_recognition(final_filename, 'run')
    
    result = dict()

    print("Identitate persoana: %s" % ml_name)
    if ml_name in persoane_autorizate:
        print("Fata recunoscuta!")
        result['name'] = ml_name
        db = get_db()
        time_now = calendar.timegm(time.gmtime())

         #Insert full name and access time into the database
        db.execute('INSERT INTO angajati (full_name, access_time) VALUES (?, ?)',
                   (ml_name, epoch_to_iso(time_now)))
        db.commit()

        print(name_to_id)
        result['status'] = 'Recunoscut'

        return jsonify(result)
    else:
        result['error'] = 'Eroare! Personal neidentificat'
        result['status'] = 'Intrus'
        result['name'] = 'Intrus'

        return jsonify(result)

@app.route('/uploads/<path:filename>')
@cross_origin()
def download_file(filename):
    '''Image fetching'''
    return send_from_directory('./static',
                               filename, as_attachment=True)

#Dataframes to convert database to .csv and .xml using pandas as pd
angajati_df = pd.read_sql_query("SELECT * FROM angajati", conn)
angajati_df.to_csv("./resources/angajati.csv", index=False)
angajati_df.to_xml("./resources/angajati.xml", index=False)

@app.route('/')
def index():
    cursor = conn.execute("SELECT full_name, access_time from angajati")
    angajati = cursor.fetchall()

    #Format the data as a list of dictionaries
    angajati_list = [
        {
            "full_name": row[0],
            "access_time": datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%SZ').strftime('%d-%m-%Y %H:%M:%S')
        }
        for row in angajati
    ]
    return render_template('index.html', angajati=angajati_list)

#Download route for .xml and .csv file
@app.route('/download/<string:file_name>')
def download(file_name):
    file_path = os.path.join(app.static_folder, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        print("Initializare Baza de Date")
        with app.app_context():
            init_db()
    elif sys.argv[1] == 'run':
        print('Ruleaza aplicatia...')
        app.run(host='0.0.0.0')
    else:
        raise ValueError("Numar incorect de argumente!")