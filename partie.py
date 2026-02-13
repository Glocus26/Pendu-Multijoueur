import random
import re

class Partie:
    def __init__(self, code_partie):
        self.code = code_partie
        self.joueurs = {}
        self.fini = False
        self.gagnant = None

    def creer_mot_a_trouver(self):
        #récupérer les mots de mots.txt
        file = open("/home/yann/flask/pendu/mots.txt", "r", encoding="utf-8")
        mots_fichier = file.read().splitlines()
        file.close()

        #créer le mot_a_trouver
        ran_mot = random.choice(list(filter(lambda mot: len(mot) > 7 and bool(re.search(r"^[a-z]+$", mot)), mots_fichier)))
        self.mot_a_trouver = list(ran_mot.lower())
        
