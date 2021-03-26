#1) Import nécessaires pour faire rouler l'application
import flask
import mysql.connector
from flask import jsonify
from flask import request as myrequest
from flask_cors import CORS
from helper import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

connection = mysql.connector.connect(host='127.0.0.1',
                             user='root',
                             password='4991',
                             database='jikiki',
                             charset='utf8mb4')

mycursor = connection.cursor()

#2) Route qui prend en charge l'inscriptipon
@app.route('/api/inscription', methods=['POST'])
def getter():
    inscriptionVerification(myrequest.get_json())
    return jsonify({"reponse":"Merci de votre post!"})

#3) Route qui prend en charge la connexion
@app.route('/api/connexion', methods=['POST'])
def connexion():
    connexionVerification(myrequest.get_json())
    return jsonify({"reponse":"Merci de votre post!"})

app.run()
connection.close()