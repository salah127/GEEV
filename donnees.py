from datetime import datetime


# ensemble des livres correspondant à la recherche


class Bibliotheque:
    def __init__(self):
        self.liste = []
        self.nombre = 0

    # vide la bibliothèque et la remplit avec une nouvelle liste de livres
    def set(self, liste):
        self.liste.clear()
        self.nombre = 0
        for i in range(len(liste)):
            self.liste.append(liste[i])
            self.nombre += 1

    def __str__(self):
        if self.nombre > 0:
            res = f'{self.nombre} livres :'
            for i in range(self.nombre):
                res += f'\n'
                res += self.liste[i].__str__()
        else:
            res = "aucun livre ne correspond"
        return res + f'\n'


# un livre quoi
class Livre:
    # stockage local de toutes les informations d'un livre
    def __init__(self, n, title, autor, gender, nb, depot, retrait, membre, adresse):
        self.id = n
        self.titre = title
        self.auteur = autor
        self.genre = gender
        self.pages = nb
        self.depot = depot
        self.retrait = retrait
        self.depositaire = membre
        self.adresse = adresse

    # description textuelle unique du livre
    def __str__(self):
        return f'{self.id} : {self.titre} - {self.auteur} - {self.genre} - {self.pages} pages - {self.adresse}'


# données utilisateur
class Utilisateur:
    # création d'un objet de stockage local "vide"
    def __init__(self):
        self.score = 0
        self.connecte = False
        self.mail = "votre mail"
        self.mdp = "votre mdp"
        self.pseudo = "votre pseudo"
        self.couleur_fond = "#440044"
        self.couleur_interface = "#FF8800"
        self.couleur_texte = "#000000"

    # insertion des données utilisateur dans l'objet local
    def insertion(self, mail, mdp, pseudo, score):
        self.mail = mail
        self.mdp = mdp
        self.pseudo = pseudo
        self.score = score
        self.connecte = True

    # s'il faut faire un test ou quoi sans se compliquer la vie
    def connexion(self):
        self.connecte = True

    # voilà quoi
    def deconnection(self):
        self.connecte = False

    # description textuelle unique du compte
    def __str__(self):
        if self.connecte:
            txt = "connecté.e"
        else:
            txt = "déconnecté.e"
        return f'{self.pseudo}, de mail {self.mail} (mdp : {self.mdp}) : {txt}, {self.score} points'


# transforme le résultat (string) d'un SELECT de SQL en une liste d'objets livres
# ATTENTION : méthode de lecture nulle, susceptible de casser si on change la bdd
def to_livres(liste):
    print(liste)
    res = []
    i = 2

    # on traite chaque livre de la liste jusqu'arriver au bout
    while i < len(liste) - 2:
        try:
            # id du livre
            n = ""
            while liste[i] != ",":
                n += liste[i]
                i += 1
            i += 3

            # titre du livre
            titre = ""
            while (liste[i] != "'" and liste[i] != '"') or liste[i+1] != ",":
                titre += liste[i]
                i += 1
            i += 4

            # auteur du livre
            auteur = ""
            while (liste[i] != "'" and liste[i] != '"') or liste[i+1] != ",":
                auteur += liste[i]
                i += 1
            i += 4

            # genre du livre
            genre = ""
            while liste[i] != "'":
                genre += liste[i]
                i += 1
            i += 3

            # nombre de pages
            pages = ""
            while liste[i] != ",":
                pages += liste[i]
                i += 1
            i += 20

            # date de dépôt : on veut seulement la date d'un datetime
            depot = ""
            while liste[i] != ",":
                depot += liste[i]
                i += 1
            i += 2
            depot += "-"
            while liste[i] != ",":
                depot += liste[i]
                i += 1
            i += 2
            depot += "-"
            while liste[i] != ",":
                depot += liste[i]
                i += 1
            while liste[i] != ")":
                i += 1
            i += 21

            # date de retrait : on veut seulement la date d'un datetime
            recup = ""
            while liste[i] != ",":
                recup += liste[i]
                i += 1
            i += 2
            recup += "-"
            while liste[i] != ",":
                recup += liste[i]
                i += 1
            i += 2
            recup += "-"
            while liste[i] != ",":
                recup += liste[i]
                i += 1

            while liste[i] != ")":
                i += 1
            i += 4

            # dépositaire du livre
            membre = ""
            while (liste[i] != "'" and liste[i] != '"') or (liste[i+1] != "," and liste[i+1] != ")"):
                membre += liste[i]
                i += 1
            i += 4

            # adresse de dépôt du livre
            adresse = ""
            while (liste[i] != "'" and liste[i] != '"') or (liste[i + 1] != "," and liste[i + 1] != ")"):
                adresse += liste[i]
                i += 1

            # on remercie SQL d'enlever les 0 en début de nombres
            if depot[6] == "-":
                depot = depot[0:5] + "0" + depot[5:len(depot)]
            if recup[6] == "-":
                recup = recup[0:5] + "0" + recup[5:len(recup)]

            # on crée un nouveau livre avec tout ça et on l'ajoute à la liste de résultats
            nouv = Livre(int(n), titre, auteur, genre, int(pages), depot, recup, membre, adresse)
            res.append(nouv)

            # livre suivant
            while i < len(liste) - 2 and liste[i] not in "0123456789":
                i += 1

        except Exception as e:
            print("\nERREUR DE LECTURE (to_livres) :", e, "\n")
    return res


# transorme le résultat unique d'un SELECT en objet utilisateur
# ATTENTION : méthode de lecture nulle comme ci-dessus
def to_user(chaine):
    res = user
    i = 3
    try:
        temp = ""
        while chaine[i+1] != ",":
            temp += chaine[i]
            i += 1
        res.mail = temp

        i += 4
        temp = ""
        while chaine[i + 1] != ",":
            temp += chaine[i]
            i += 1
        res.mdp = temp

        i += 4
        temp = ""
        while chaine[i + 1] != ",":
            temp += chaine[i]
            i += 1
        res.pseudo = temp
        
        i += 3
        temp = ""
        while chaine[i+1] != "]":
            temp += chaine[i]
            i += 1
        res.score = int(temp)

        print(res)
        return res

    except Exception as e:
        print("\nERREUR DE LECTURE (to_user) :", e, "\n")
        return user
    
    
def to_liste(chaine):
    res = []
    i = 3
    
    print(chaine)
    try:
        while chaine[i] != "]":
            if i != 3:
                i += 4
            temp = ""
            while chaine[i+1] != ",":
                temp += chaine[i]
                i += 1
            res.append(temp)
            i += 3
        return res
     
    except Exception as e:
        print("\nERREUR DE LECTURE (to_liste) :", e, "\n")
        return []


user = Utilisateur()
today = str(datetime.now())[0:10]
print("Date actuelle : ", today)
