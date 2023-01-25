import socket
from tkinter import messagebox


# envoie un message au serveur et retourne sa réponse
def envoi(message):
    print("Envoi de :", message)
    try:
        s.send(message.encode())
        return s.recv(8192).decode()
    except:
        messagebox.showerror("Requête impossible", "Aucune liaison établie avec le serveur.")
        return "[]"


# envoie un fichier image comme illustration de livre
def export(image):
    print("Envoi de :", image.name)
    s.send(image)
    return s.recv(8192).decode()


def entrer_livre(title, autor, gender, pages, date, mail, adresse):
    return envoi("entrer_livre/" + title + "/" + autor + "/" + gender
                 + "/" + pages + "/" + date + "/" + mail + "/" + adresse + "/.")


def entrer_compte(mail, mdp, pseudo, date_de_naissance, sex):
    return envoi("entrer_compte/" + mail + "/" + mdp + "/" + pseudo
                 + "/" + date_de_naissance + "/" + sex + "/.")


def modifier_compte(pseudo, date, sexe, mail):
    return envoi("modifier_compte/" + pseudo + "/" + date + "/" + sexe + "/" + mail + "/.")


def ajout_score(mail, score):
    return envoi("ajout_score/" + mail + "/" + str(score) + "/.")


def annuler_toute_reservation(identifiant):
    return envoi("annuler_toute_reservation/" + str(identifiant) + "/.")


def Supprimer_compte(mail):
    return envoi("Supprimer_compte/" + mail + "/.")


def tous_les_livres():
    return envoi("tous_les_livres/.")


def livres_filtre(filtre, valeur, tri):
    return envoi("livres_filtre/" + filtre + "/" + valeur + "/" + tri + "/.")


def livres_tri(tri):
    return envoi("livres_tri/" + tri + "/.")


def livres_deposes(mail):
    return envoi("livres_deposes/" + mail + "/.")


def livres_reserves(mail):
    return envoi("livres_reserves/" + mail + "/.")


def trouver_compte(mail, mdp):
    return envoi("trouver_compte/" + mail + "/" + mdp + "/.")


def reserver_livre(mail, identifiant, date):
    return envoi("reserver_livre/" + mail + "/" + str(identifiant) + "/" + date + "/.")


def annuler_reservation(mail, livre, date):
    return envoi("annuler_reservation/" + mail + "/" + str(livre) + "/" + date + "/.")


def a_reserve(mail, identifiant):
    return envoi("a_reserve/" + mail + "/" + str(identifiant) + "/.")


def retirer_livre(identifiant):
    return envoi("retirer_livre/" + str(identifiant) + "/.")


def nb_reservations(identifiant):
    return envoi("nb_reservations/" + str(identifiant) + "/.")


def liste_reservations(livre):
    return envoi("liste_reservations/" + str(livre) + "/.")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("localhost", 42000))
except:
    messagebox.showwarning("Connection impossible", "Echec de la liaison avec le serveur.")
