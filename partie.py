class Partie:
    def __init__(self, code_partie):
        self.code = code_partie
        self.joueurs = []
        self.finie = False
        self.gagnant = None