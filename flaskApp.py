#1) Import nécessaires pour faire rouler l'application
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
cors = CORS(app, resources={r"*": {"origins": "http://localhost:4200"}})
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
        sql = "SELECT * FROM utilisateurs WHERE addresseCourriel=%s"
        val = (adresseCourriel,)
        mycursor.execute(sql, val)
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
        sql = "SELECT prenom, nom, imageProfil, motDePasse FROM utilisateurs WHERE addresseCourriel=%s"
        val = (adresseCourriel,)
        mycursor.execute(sql, val)
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
            sql = "UPDATE utilisateurs SET prenom=%s, nom=%s, imageProfil=%s WHERE addresseCourriel=%s"
            val = (reqJson['prenom'], reqJson['nom'], reqJson['imageProfil'] ,webtoken['user'])
            mycursor.execute(sql, val)
            myresult = mycursor.fetchone()
            connection.commit()
            print(mycursor.rowcount, "record inserted.")

            mycursor.execute("SELECT prenom, nom, imageProfil FROM utilisateurs WHERE addresseCourriel=%s", (webtoken['user'],))
            myresult = mycursor.fetchone()
            
            return jsonify({"reponse":"success", 'prenom':myresult['prenom'], 
            'nom':myresult['nom'], 'imageProfil':myresult['imageProfil']})

        except:
            return jsonify({"reponse":"echec"})


#3) Route qui remet le profil au front-end
@app.route('/api/profil', methods=['POST'])
def get_profil():
    reqJson = myrequest.get_json()

    if not reqJson.get("token"):
        return jsonify({"reponse":"echec"})
    
    else:
        try:
            webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
            mycursor.execute("SELECT prenom, nom, imageProfil FROM utilisateurs WHERE addresseCourriel=%s", (webtoken['user'],))
            myresult = mycursor.fetchone()

            return jsonify({"reponse":"success", 'prenom':myresult['prenom'], 
            'nom':myresult['nom'], 'imageProfil':myresult['imageProfil']})

        
        except:
            return jsonify({"reponse":"echec"})

    
@app.route('/api/marqueauto', methods=['GET'])
def get_infoauto():
    #1 Envoyer toute l'information des marques et modèles d'auto
    mycursor.execute("SELECT * FROM mmauto")
    myresult = mycursor.fetchall()
    return jsonify({'response':myresult})


@app.route('/api/poster_auto', methods=['POST'])
def poster_auto():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()
    reqAutoInfo = reqJson.get('auto')
    marqueModeleAutoChamp = reqAutoInfo.get("marquePost")
    marqueModeleAuto = marqueModeleAutoChamp.split("+")

    titrePost = reqAutoInfo.get("titrePost")
    prixPost = reqAutoInfo.get("prixPost")
    kiloAuto = reqAutoInfo.get("kilometragePost")
    marqueAuto = marqueModeleAuto[0]
    modeleAuto = marqueModeleAuto[1]
    versionAuto = reqAutoInfo.get("versionPost")
    motriciteAuto = reqAutoInfo.get("motricitePost")
    anneAuto = reqAutoInfo.get("annePost")
    etatAuto = reqAutoInfo.get("etat")
    carrosserieAuto = reqAutoInfo.get("carrosseriePost")
    carburantAuto = reqAutoInfo.get("carburantPost")
    transmissionAuto = reqAutoInfo.get("transmissionPost")
    descriptionAuto = reqAutoInfo.get("descriptionPost")
    equipementUn = reqAutoInfo.get("equipement_un")
    equipementDeux = reqAutoInfo.get("equipement_deux")
    equipementTrois = reqAutoInfo.get("equipement_trois")
    equipementQuatre = reqAutoInfo.get("equipement_quatre")
    imageUn = reqAutoInfo.get("image_un")
    imageDeux = reqAutoInfo.get("image_deux")
    imageTrois = reqAutoInfo.get("image_trois")

    # 2 Verifier que l'utilisateur est connnecté
    if not reqJson.get("token"):
        return jsonify({"reponse":"echec"})
    
    else:
        try:
            webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
            if posterAutoVerification(marqueModeleAutoChamp ,titrePost, prixPost, kiloAuto, versionAuto, motriciteAuto ,anneAuto, etatAuto, carrosserieAuto, carburantAuto, transmissionAuto, descriptionAuto, equipementUn, equipementDeux, equipementTrois, equipementQuatre, imageUn, imageDeux, imageTrois) == False:
                print('juns')
                return jsonify({"reponse":"echec"})
            
            else:
                # 3) Verifier que la marque et modèle d'auto sont valide
                mycursor.execute("SELECT * FROM mmauto WHERE Marque=%s AND Modele=%s", (marqueAuto, modeleAuto))
                myresult = mycursor.fetchone()
                print('hello')
                if myresult == None:
                    return jsonify({"reponse":"echec"})
                else:
                    idpost = uniqueID()
                    print('hey')
                    mycursor.execute("CALL entrerPost('{}', '{}', '{}', {}, '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(idpost, webtoken['user'], titrePost, prixPost, descriptionAuto, etatAuto, kiloAuto, '-', transmissionAuto, '-', carburantAuto, carrosserieAuto, marqueAuto, modeleAuto, anneAuto, imageUn, imageDeux, imageTrois, equipementUn, equipementDeux, equipementTrois, equipementQuatre))
                    return jsonify({'response':"success"})
        
        except Error as e:
            print(e)
            return jsonify({"reponse":"echec"})


@app.route('/api/mes_auto', methods=['POST'])
def mes_auto():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()

    try:
        webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
        print('ici 1')
        mycursor.execute("SELECT * FROM postauto WHERE addresseCourriel=%s", (webtoken["user"],))
        print('ici 2')
        myresult = mycursor.fetchall()
        return jsonify({"reponse":"success", "autos":myresult})

    except Error as e:
        print(e)
        return jsonify({"reponse":"echec"})

@app.route('/api/supprimer_autos', methods=['POST'])
def supprimer_autos():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()
    idpost = reqJson.get("idpost")
    print(reqJson)

    if idpost == None:
        return jsonify({"reponse":"echec"})
    
    else:
        try:
            # 2 verifier que le token et valide et renvoyer la réponse
            webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
            val = (idpost, webtoken['user'])
            print('ici')
            mycursor.execute("DELETE FROM postauto WHERE idpost=%s AND addresseCourriel=%s", val)
            connection.commit()
            print(mycursor.rowcount, "record deleted.")
            return jsonify({"reponse":"success"})
        
        except:
            return jsonify({"reponse":"echec"})


@app.route('/api/mes_favoris', methods=['POST'])
def mes_favoris():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()

    try:
        # 2 verifier que le token et valide et renvoyer la réponse
        webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
        val = (webtoken['user'],)
        mycursor.execute("SELECT p.idpost, p.titreAuto, p.marqueAuto, p.modeleAuto, i.urlimage FROM postauto AS p, imageauto AS i WHERE p.addresseCourriel=%s AND  p.idpost=i.idpost", val)
        myresult = mycursor.fetchall()
        if myresult == None:
            return jsonify({"reponse":"echec"})
        
        else:
            return jsonify({"reponse":"success", "favoris":myresult})

    except:
        return jsonify({"reponse":"echec"})


@app.route('/api/poster_favoris', methods=['POST'])
def poster_favoris():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()
    idpost = reqJson.get("idpost")

    if idpost == None:
        return jsonify({"reponse":"echec"})

    try:
        # 2 verifier que le token et valide et renvoyer la réponse
        webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
        val = (idpost, webtoken['user'])
        mycursor.execute("SELECT idpost FROM postfavoris WHERE idpost=%s AND addresseCourriel=%s", val)
        myresult = mycursor.fetchone()
        if myresult == None:
            mycursor.execute("INSERT INTO postfavoris VALUES (%s, %s)", val)
            connection.commit()
            return jsonify({"reponse":"success"})
        
        else:
            return jsonify({"reponse":"echec"})

    except:
        return jsonify({"reponse":"echec"})

@app.route('/api/supprimer_favoris', methods=['POST'])
def supprimer_favoris():
    #1 Extraire toutes les données
    reqJson = myrequest.get_json()
    idpost = reqJson.get("idpost")

    if idpost == None:
        return jsonify({"reponse":"echec"})
    
    else:
        try:
            # 2 verifier que le token et valide et renvoyer la réponse
            webtoken = myjwt.decode(reqJson.get("token"), key=app.config["SECRET_KEY"], algorithms=["HS256"])
            val = (idpost, webtoken['user'])
            mycursor.execute("DELETE FROM postfavoris WHERE idpost=%s AND addresseCourriel=%s", val)
            connection.commit()
            print(mycursor.rowcount, "record deleted.")
            return jsonify({"reponse":"success"})
        
        except:
            return jsonify({"reponse":"echec"})

app.run()
connection.close()