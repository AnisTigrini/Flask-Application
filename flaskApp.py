#1) Import nécessaires pour faire rouler l'application
from dns.message import make_response
import flask
import mysql.connector
import jwt as myjwt
import datetime
from flask_bcrypt import Bcrypt
from flask import jsonify
from flask import request as myrequest
from flask_cors import CORS
from mysql.connector import cursor
from mysql.connector.errors import Error
from helper import *


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "jikikiautoestlemeilleursitedautoaumondeselontoutlemonde"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
bcrypt = Bcrypt(app)

connection = mysql.connector.connect(host='127.0.0.1',
                             user='root',
                             password='4991',
                             database='jikiki',
                             charset='utf8mb4')

mycursor = connection.cursor(buffered=True,dictionary=True)

#2) Route qui prend en charge l'inscriptipon
@app.route('/api/inscription', methods=['POST'])
def getter():
    # 2.1) Extraire toutes nos donnés
    reqJson = myrequest.get_json()
    adresseCourriel = reqJson.get("adresseCourriel")
    motDePasse = reqJson.get("motDePasse")
    anneNaissance = reqJson.get("anneNaissance")
    nomUtilisateur = reqJson.get("nomUtilisateur")
    prenomUtilisateur = reqJson.get("prenomUtilisateur")

    # 2.2) Vérifier l'integrité des données reçus
    if not inscriptionVerification(adresseCourriel, motDePasse, anneNaissance, nomUtilisateur, prenomUtilisateur):
        return jsonify({"reponse":"echec"})
    # 2.2) Si les donnés sont bonnes
    else:
        mycursor.execute("SELECT * FROM utilisateurs WHERE addresseCourriel='{}'".format(adresseCourriel))
        myresult = mycursor.fetchone()

        if myresult == None:
            pw_hash = bcrypt.generate_password_hash(motDePasse).decode("utf-8")
            imageProfil = "https://cdn.dribbble.com/users/5642965/screenshots/12675462/profile_picture_4x.jpg"
            val = (adresseCourriel, prenomUtilisateur, nomUtilisateur, anneNaissance, pw_hash, imageProfil)
            sql = "INSERT INTO utilisateurs VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(sql, val)
            connection.commit()
            print(mycursor.rowcount, "record inserted.")
            return jsonify({"reponse":"succes"})
        
        else:
            return jsonify({"reponse":"echec"})

#3) Route qui prend en charge la connexion
@app.route('/api/connexion', methods=['POST'])
def connexion():
    reqJson = myrequest.get_json()
    adresseCourriel = reqJson.get("adresseCourriel")
    motDePasse = reqJson.get("motDePasse")

    if not connexionVerification(adresseCourriel, motDePasse):
        return jsonify({"reponse":"echec"})
    
    else:
        mycursor.execute("SELECT prenom, nom, imageProfil, motDePasse FROM utilisateurs WHERE addresseCourriel='{}'".format(adresseCourriel))
        myresult = mycursor.fetchone()

        if myresult == None:
            return jsonify({"reponse":"echec"})
            
        else:
            if bcrypt.check_password_hash(myresult['motDePasse'], motDePasse):
                token = myjwt.encode({'user':adresseCourriel, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, app.config["SECRET_KEY"])
                return jsonify({"reponse":"success",
                'prenom':myresult['prenom'],
                'nom':myresult['nom'],
                'imageProfil':myresult['imageProfil'],
                'addresseCourriel':adresseCourriel,
                'token': token})
            
            else : 
                return jsonify({"reponse":"echec"})


#3) Route qui prend en charge la connexion
@app.route('/api/maj-profil', methods=['POST'])
def maj_profil():
    reqJson = myrequest.get_json()
    
    if not reqJson.get("token"):
        return jsonify({"reponse":"echec"})

    else:
        try:
            webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
            mycursor.execute('''UPDATE utilisateurs SET prenom='{}', nom='{}', imageProfil='{}' 
            WHERE addresseCourriel='{}' '''.format(reqJson['prenom'], reqJson['nom'], reqJson['imageProfil'] ,webtoken['user']))
            myresult = mycursor.fetchone()
            connection.commit()
            print(mycursor.rowcount, "record inserted.")

            mycursor.execute("SELECT prenom, nom, imageProfil FROM utilisateurs WHERE addresseCourriel='{}'".format(webtoken['user']))
            myresult = mycursor.fetchone()
            
            return jsonify({"reponse":"success", 'prenom':myresult['prenom'], 
            'nom':myresult['nom'], 'imageProfil':myresult['imageProfil']})

        except:
            return jsonify({"reponse":"echec"})


app.run()
connection.close()