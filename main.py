#modules
from flask import Flask, render_template, request, redirect, url_for, session
import random
import re
import string

from partie import Partie
from etat_du_jeu import etat
from joueur import Joueur


app = Flask(__name__)
app.secret_key = "3015a467b41f35ccabc66b9de777faaa7a0230508713d047e55f14440d77b7ed"


#routes

@app.route("/")
def index():
    session["code_partie"] = ""
    session["pseudo"] = ""
    return render_template("index.html")


# Routes partie création de partie ########################
@app.route("/creer")
def creer():
    return render_template("creer.html", code_partie=session["code_partie"])

@app.route("/creer/attente")
def creer_attente():
    #récup du pseudo donné par l'utilisateur
    pseudo = request.args.get('pseudo').lower()
    

    #noter le code de jeu et le pseudo dans session
    if session["code_partie"] == "":#pour éviter de changer le code à chaque refresh de la page
        session["pseudo"] = pseudo

        session["code_partie"] = creer_code_jeu()

        #créer le joueur
        j1 = Joueur(pseudo)

        #créer la Partie
        partie = Partie(session["code_partie"])
        partie.joueurs.append(j1) #ajouter le j1 dans la partie (vérifié)
        etat.parties[session["code_partie"]] = partie #ajoute la partie dans l'état du jeu

    #verifier si un joueur à rejoint
    if len(etat.parties[session["code_partie"]].joueurs) == 2:
        msg = etat.parties[session["code_partie"]].joueurs[1].pseudo+" a rejoint la partie"
    else:
        msg = "en attente de joueur"

    return render_template("creer.html", code_partie=session["code_partie"], message=msg)



# Routes partie rejoindre une partie ######################
@app.route("/rejoindre")
def rejoindre():
    return render_template("rejoindre.html")

@app.route("/rejoindre/creation")
def rejoindre_creation():

    #récup du pseudo donné par l'utilisateur
    pseudo = request.args.get('pseudo').lower()
    code_partie = request.args.get('code_partie')

    #rejoindre une partie
    if code_partie not in list(etat.parties.keys()) or len(etat.parties[code_partie].joueurs) != 1:
        return render_template("rejoindre.html", message="la partie n'existe pas")
    
    #créer le joueur
    j2 = Joueur(pseudo)

    #noter le code de jeu et le pseudo dans session
    session["code_partie"] = code_partie
    session["pseudo"] = pseudo

    etat.parties[code_partie].joueurs.append(j2)
    msg = "vous êtes dans la partie, actualisez la page du J1"

    return render_template("rejoindre.html", message=msg)

#fonctions
def creer_code_jeu():
    """
    ne demande rien et retourne un str du code de la partie (5 caractères)
    """
    c = []
    for i in range(0,5):
        c.append(random.choice(creer_liste_pour_code()))
    
    return "".join(c)

def creer_liste_pour_code():
    alph_min = list(string.ascii_lowercase)
    alph_maj = list(string.ascii_uppercase)
    alpha_mix = alph_maj + alph_min

    return alpha_mix









if __name__ == '__main__':
    app.run(debug=True)