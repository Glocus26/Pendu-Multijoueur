#modules
from flask import Flask, render_template, request, redirect, url_for, session
import random
import re
import string
import secrets

from partie import Partie
from etat_du_jeu import etat
from joueur import Joueur
from bonhommes import bonhommes

app = Flask(__name__)
app.secret_key = str(secrets.token_hex())


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

    #noter le code de jeu et le pseudo dans session
    if session["code_partie"] == "":#pour éviter de changer le code à chaque refresh de la page
        
        #récup du pseudo donné par l'utilisateur
        pseudo = request.args.get('pseudo').lower()
    
        session["pseudo"] = pseudo

        session["code_partie"] = creer_code_jeu()

        #créer le joueur
        j1 = Joueur(pseudo)

        #créer la Partie
        partie = Partie(session["code_partie"])
        partie.joueurs[pseudo] = j1 #ajouter le j1 dans la partie
        etat.parties[session["code_partie"]] = partie #ajoute la partie dans l'état du jeu
        partie.creer_mot_a_trouver()

        partie.joueurs[session["pseudo"]].mot_cherche = creer_mot_cherche()

    #verifier si un joueur à rejoint
    if len(list(etat.parties[session["code_partie"]].joueurs.keys())) == 2:
        etat.parties[session["code_partie"]].etat = "commencée"
        return redirect(url_for('partie'))
    else:
        return render_template("creer.html", code_partie=session["code_partie"], message="en attente de joueur")


@app.route("/creer/est-ce-que-adversaire-a-rejoint")
def adversaire_a_rejoint():
    return str(len(list(etat.parties[session["code_partie"]].joueurs.keys())) == 2)

# Routes partie rejoindre une partie ######################
@app.route("/rejoindre")
def rejoindre():
    return render_template("rejoindre.html")

@app.route("/rejoindre/creation")
def rejoindre_creation():

    pseudo = request.args.get('pseudo').lower()
    code_partie = request.args.get('code_partie')

    #rejoindre une partie
    if code_partie not in list(etat.parties.keys()):
        return render_template("rejoindre.html", message="la partie n'existe pas")
    
    elif len(list(etat.parties[code_partie].joueurs.keys())) == 2:
        return redirect(url_for('partie'))
    
    else:
        #créer le joueur
        j2 = Joueur(pseudo)

        #noter le code de jeu et le pseudo dans session
        session["code_partie"] = code_partie
        session["pseudo"] = pseudo

        partie = etat.parties[code_partie]

        partie.joueurs[pseudo] = j2

        partie.joueurs[session["pseudo"]].mot_cherche = creer_mot_cherche()

        return redirect("/partie")



@app.route("/partie")
def partie():
    code_partie = session["code_partie"]
    partie = etat.parties[code_partie]
    joueur = partie.joueurs[session["pseudo"]]

    pseudo_autre_joueur = next(pseudo for pseudo in partie.joueurs if pseudo != session["pseudo"])
    autre_joueur = partie.joueurs[pseudo_autre_joueur]

    verif_lettre()

    if partie.fini == True:
        return render_template("fin.html", msg="Trop tard", mot="".join(partie.mot_a_trouver))


    joueur_a_trouve_mot = partie.mot_a_trouver == joueur.mot_cherche

    if joueur_a_trouve_mot:
        partie.fini = True
        partie.gagnant = session["pseudo"]
        return render_template("fin.html", msg="Bravo !!", mot="".join(partie.mot_a_trouver))
    
    if joueur.est_mort():
        return render_template("fin.html", msg="Game Over", mot="".join(partie.mot_a_trouver))

    mot_cherche = joueur.mot_cherche
    vies = joueur.vies
    f_lettres = ", ".join(joueur.f_lettres)

    

    return render_template("jeu.html", bonhommes=bonhommes, mot_cherche_aj=re.sub('[A-Za-z]', 'X', "".join(autre_joueur.mot_cherche)), vies_aj=autre_joueur.vies, pseudo_autre_joueur=pseudo_autre_joueur, vies=vies, f_lettres=f_lettres, pseudo=session["pseudo"], mot_cherche=" ".join(mot_cherche))

@app.route("/partie/adversaire")
def partie_adversaire():
    code_partie = session["code_partie"]
    partie = etat.parties[code_partie]
    joueur = partie.joueurs[session["pseudo"]]

    pseudo_autre_joueur = next(pseudo for pseudo in partie.joueurs if pseudo != session["pseudo"])
    autre_joueur = partie.joueurs[pseudo_autre_joueur]

    return render_template("jeu_adversaire.html", bonhommes=bonhommes, mot_cherche_aj=re.sub('[A-Za-z]', 'X', "".join(autre_joueur.mot_cherche)), vies_aj=autre_joueur.vies, pseudo_autre_joueur=pseudo_autre_joueur)



#fonctions

def verif_lettre():
    """
    automatique : ne retourne rien, demande rien et actualise les variables
    """
    partie = etat.parties[session["code_partie"]]

    #récupérer la lettre donnée
    let_give = request.args.get('lettre')

    if let_give == "" or let_give == None:
        return

    if len(let_give) != 1:
        return
    
    if let_give.isalpha() == False:
        return

    if let_give.lower() in partie.joueurs[session["pseudo"]].l_propo:
        return

    let_give = let_give.lower()
    partie.joueurs[session["pseudo"]].l_propo.append(let_give)
    good = False

    for i,lettre in enumerate(partie.mot_a_trouver):
        if lettre == let_give:
            
            nouveau = partie.joueurs[session["pseudo"]].mot_cherche
            nouveau[i] = let_give
            partie.joueurs[session["pseudo"]].mot_cherche = nouveau

            good = True

    if good == False:
        partie.joueurs[session["pseudo"]].f_lettres.append(let_give)
        partie.joueurs[session["pseudo"]].vies = partie.joueurs[session["pseudo"]].vies - 1


def creer_code_jeu():
    """
    retourne un str du code de la partie (5 caractères)
    """
    c = []
    for i in range(0,4):
        c.append(random.choice(creer_liste_pour_code()))
    
    return "".join(c)

def creer_liste_pour_code():
    """
    retourne une liste avec toutes les lettres de l'alphabet en maj et min
    """
    alph_min = list(string.ascii_lowercase)
    alph_maj = list(string.ascii_uppercase)
    alpha_mix = alph_maj + alph_min

    return alph_min

def creer_mot_cherche():
    """
    retourne la liste mot_cherche
    """
    partie = etat.parties[session["code_partie"]]

    mot_cherche = []

    for l in partie.mot_a_trouver:#met un _ pour chaque lettre de mot_a_trouver dans mot_cherche
        mot_cherche.append("_")

    return mot_cherche


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
