# File for helper functions
import datetime
import re

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