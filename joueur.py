class Joueur():
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.vies = 8
        self.f_lettres = []
        self.l_propo = ["", " "]
        self.mot_cherche = []

    def est_mort(self):
        return self.vies <= 0