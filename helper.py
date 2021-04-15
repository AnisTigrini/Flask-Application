# File for helper functions
import datetime
import re
import random

# 1 S'assurer qu'on a les bonnes données pour la connexion
def connexionVerification(adresseCourriel, motDePasse):
    # 1.1 Verifier qu'on trouve l'adresse et le mot de pase
    if adresseCourriel == None or motDePasse == None:
        return False
    
    else:
        if len(motDePasse) < 4:
            return False

        if not re.search(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+', adresseCourriel):
            return False


    return True

# 2 S'assurer qu'on valide les données pour l'inscription
def inscriptionVerification(adresseCourriel, motDePasse, anneNaissance, nomUtilisateur, prenomUtilisateur):
    # 1.1 Verifier que tout les paramètres sont présents dans la requête
    if adresseCourriel == None or motDePasse == None or anneNaissance == None or nomUtilisateur == None or prenomUtilisateur == None:
        return False
    
    # 1.2 Dans le cas ou tout les paramétres sont présents, on fait d'autres vérifications 
    else:
        if len(motDePasse) < 4 or len(nomUtilisateur) < 1 or len(prenomUtilisateur) < 1:
            return False

        if not re.search(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+', adresseCourriel):
            return False

        try:
            anneNaissance = datetime.datetime.strptime(anneNaissance, '%Y-%m-%d')
            
            if anneNaissance > datetime.datetime.now():
                return False
        
        except ValueError:
            return False
        
    return True

# 3) S'assurer que les données des posts d'autos sont valides
def posterAutoVerification(marqueModeleAutoChamp ,titrePost, prixPost, kiloAuto, versionAuto, motriciteAuto ,anneAuto, etatAuto, carrosserieAuto, carburantAuto, transmissionAuto, descriptionAuto, equipementUn, equipementDeux, equipementTrois, equipementQuatre, imageUn, imageDeux, imageTrois):
    # 1.1 Verifier que tout les paramètres sont présents dans la requête
    if marqueModeleAutoChamp == None or titrePost == None or prixPost == None or kiloAuto == None or anneAuto == None or etatAuto == None or versionAuto == None or motriciteAuto == None:
        return False
    elif carrosserieAuto == None or carburantAuto == None or transmissionAuto == None or descriptionAuto == None:
        return False
    elif equipementUn == None or equipementDeux == None or equipementTrois == None or equipementQuatre == None:
        return False
    elif imageUn == None or imageDeux == None or imageTrois == None:
        return False
    
    # 1.1 Verifier que les donnnées son justes
    if len(titrePost) < 4 or len(titrePost) > 60 or isinstance(prixPost, int) == False or isinstance(kiloAuto, int) == False:
        return False

    elif anneAuto.isnumeric() == False or etatAuto not in ["usage", "nouveau"]:
        return False
    elif carrosserieAuto not in ["Camionnette", "VUS", "Berline", "Fourgonnette", "Voitures sport et coupés", "À hayon", "Familiale"]:
        return False
    elif carburantAuto not in ["Essence", "Diesel", "Électrique", "Hybride", "Autres"]:
        return False
    elif transmissionAuto not in ["Automatique", "Manuelle"]:
        print('ici')
        return False
    elif len(descriptionAuto) < 20 or len(imageUn) < 4 or len(imageDeux) < 4:
        print('ici 2')
        return False
    elif imageUn == imageDeux or imageDeux == imageTrois:
        print('ici 3')
        return False

    return True

# 4 Fonction qui retourn un id unique
def uniqueID():
    monTexte = "1234567890qwertyuiopasdfghjklzxcvbnm"
    longMonTexte = len(monTexte) - 1
    monID = ""

    while len(monID) < 10:
        aleatoire = random.randint(0, longMonTexte)
        monID += monTexte[aleatoire]

    return monID 