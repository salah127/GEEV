import socket
import threading
import mysql.connector


# - - - ANNEXES - - - #


# retourne la partie du texte précédant le premier '/'
def premier(texte):
    i = 0
    while texte[i] != '/' and i < len(texte):
        i += 1
    return texte[0:i]


# retourne la partie du texte suivant le premier '/'
def reste(texte):
    i = 1
    while texte[i - 1] != "/" and i < len(texte):
        i += 1
    return texte[i:len(texte)]


# scinde un texte en une liste de mots selon les '/'
def scinder(texte):
    res = []
    while texte != ".":
        res.append(premier(texte))
        texte = reste(texte)
    return res


# - - - BASE DE DONNEES - - - #


# connection à la base de données fournie
def connection():
    return mysql.connector.connect(host="localhost", port=3306, user="l2_info_4", password="Ooquai2e",
                                   database="l2_info_4")


# connexion avec putty
def putty():
    return mysql.connector.connect(host="localhost", port="1183", user="l2_info_4", password="Ooquai2e",
                                   database="l2_info_4")


# connection à une base de données locale
def local():
    return mysql.connector.connect(host="localhost", user="root", database="l2_info_4")


# creation des tables dans la base de donnee
def initialisation_base():
    db = connection()
    cursor = db.cursor()
    sql_init_livres = "CREATE TABLE IF NOT EXISTS Livre (id	INT AUTO_INCREMENT, titre VARCHAR(50) NOT NULL, auteur VARCHAR(50) NOT NULL, genre VARCHAR(50) NOT NULL, " \
                      "pages INT DEFAULT 0, depot DATETIME DEFAULT CURRENT_TIMESTAMP, recuperation DATETIME NOT NULL, depositaire VARCHAR(100) NOT NULL, " \
                      "CONSTRAINT pk_livre PRIMARY KEY (id), CONSTRAINT fk_livre_compte FOREIGN KEY (depositaire) REFERENCES Compte (mail))"
    sql_init_comptes = "CREATE TABLE IF NOT EXISTS Compte (pseudo VARCHAR(100) NOT NULL, sexe VARCHAR(100), nationalite VARCHAR(100), mail VARCHAR(100) NOT NULL, " \
                       "date_de_naissance DATETIME, mot_de_passe VARCHAR(100) NOT NULL, score INT DEFAULT 0, CONSTRAINT pk_compte PRIMARY KEY (mail))"
    sql_init_reservation = "CREATE TABLE IF NOT EXISTS Reservation (user VARCHAR(100) NOT NULL, livre INT NOT NULL, date_resa DATETIME DEFAULT CURRENT_TIMESTAMP, " \
                           "CONSTRAINT pk_reservation PRIMARY KEY (user, livre), CONSTRAINT fk_reservation_compte FOREIGN KEY (user) REFERENCES Compte (mail), " \
                           "CONSTRAINT fk_reservation_livre FOREIGN KEY (livre) REFERENCES Livre (id))"
    cursor.execute(sql_init_livres)
    cursor.execute(sql_init_comptes)
    cursor.execute(sql_init_reservation)


# exécute une requête pré-écrite, la soumet à la BDD, et retourne la réponse de celle-ci
def send_requete(requete, conn, commande, cursor):
    res = "commande invalide"
    print("\n" + requete)
    # on essaie d'envoyer la requête puis de récupérer une réponse de la base de données
    try:
        cursor.execute(requete)
        # si on veut insérer ou supprimer des données, on utilise commit()
        try:
            conn.commit()
        except Exception as ex:
            res = "erreur d'enregistrement : " + str(ex)
        # si on cherche des données, on utilise cursor.fetchall()
        try:
            # si on cherche directement un nombre de retours, on met directement len()
            if commande == "nb_reservations" or commande == "a_reserve":
                res = str(len(cursor.fetchall()))
            else:
                res = str(cursor.fetchall())
        except Exception as ex:
            res = "erreur (fetchall) : " + str(ex)
            print("erreur (fetchall) : " + str(ex))
    except Exception as e:
        res = "erreur d'execution : " + str(e)
        print("erreur d'execution : " + str(e))
    return res


# supprime un compte, ses réservations et livres, et les réservations sur ses livres
def supprimer_compte(commande, conn, cursor):
    requete3 = "DELETE FROM Reservation WHERE `user` = '"+ commande[1]+ "'"
    requete1 = "SELECT id FROM Livre WHERE depositaire ='"+ commande[1]+"'"
    requete2 = "DELETE FROM Livre WHERE depositaire ='"+commande[1]+"'"
    id_livres = send_requete(requete1, conn, commande[0], cursor)
    print(str(id_livres))
    for val in id_livres:
        requete = "DELETE FROM Reservation WHERE livre = "+str(val[0])
        send_requete(requete, conn, commande[0], cursor)
    send_requete(requete2, conn, commande[0], cursor)
    send_requete(requete3, conn, commande[0], cursor)
    return "DELETE FROM `Compte` WHERE `mail` = '" + commande[1] + "'"


# modifie un compte, met à jour ses réservations et livres, et les réservations sur ses livres
"""def modifier_compte(commande, conn, cursor):
    requete1 = "SELECT id FROM Livre WHERE depositaire ='" + commande[4] + "'"
    requete3 = "UPDATE Livre SET user ='" + commande[1] + "' WHERE depositaire ='" + commande[4] + "'"
    requete4 = "UPDATE `Compte` SET `pseudo`='" + commande[1] + "',`date_de_naissance`='" + commande[2]\
               + "',`sexe`='" + commande[3] + "' WHERE  `mail` = '" + commande[4] + "'"
    id_livres = send_requete(requete1, conn, commande[0], cursor)
    for val in id_livres:
        requete2 = "UPDATE Reservation SET user ='" + commande[4] + "'  WHERE user ="+str(val[0])
        send_requete(requete2, conn, commande[0], cursor)
    send_requete(requete3, conn, commande[0], cursor)
    send_requete(requete4, conn, commande[0], cursor)
    return "UPDATE `Compte` SET `pseudo`='" + commande[1] + "',`date_de_naissance`='" + commande[2]\
           + "',`sexe`='" + commande[3] + "' WHERE  `mail` = '" + commande[4] + "'"""""


# traite une commande sous forme de tableau (fonction en valeur 0, paramètres ensuite)
# retourne un texte : erreur s'il y a, réponse de la base de données sinon
# cette fonction ouvre une connexion SQL, fait son travail, puis ferme la connexion, à chaque appel
def traiter(commande):
    conn = connection()
    cursor = conn.cursor()
    requete = ""
    res = "aucun resultat"

    # on traite au cas par cas la fonction choisie pour écrire la commande SQL correspondante
    if commande[0] == "entrer_livre":
        requete = "INSERT INTO `Livre` (`id`, `titre`, `auteur`, `genre`, `pages`, `recuperation`, `depositaire`, `adresse`) VALUES(NULL, '" \
                  + commande[1] + "', '" + commande[2] + "', '" + commande[3] + "', '" + commande[4] + "', '" + commande[5] + " 00:00:00', '" + commande[6] + "', '" + commande[7] + "')"

    elif commande[0] == "entrer_compte":
        requete = "INSERT INTO `Compte` (`mail`, `mot_de_passe`, `pseudo`,`date_de_naissance`,`sexe` ) VALUES ('" \
                  + commande[1] + "', '" + commande[2] + "', '" + commande[3] + "', '" + commande[4] + "', '" + commande[5] + "')"

    elif commande[0] == "modifier_compte":
        requete = "UPDATE `Compte` SET `pseudo`='" + commande[1] + "',`date_de_naissance`='" + commande[2] + \
                  "',`sexe`='" + commande[3] + "' WHERE `mail`= '" + commande[4] + "'"

    elif commande[0] == "tous_les_livres":
        requete = "SELECT * FROM `Livre`"

    elif commande[0] == "ajout_score":
        requete = "UPDATE `Compte` SET `score` = '" + commande[2] + "' WHERE `mail` = '" + commande[1] + "'"

    elif commande[0] == "annuler_toute_reservation":
        requete = "DELETE FROM `Reservation` WHERE `id` = '" + commande[1] + "'"

    elif commande[0] == "Supprimer_compte":
        requete = supprimer_compte(commande, conn, cursor)

    elif commande[0] == "livres_filtre":
        requete = "SELECT * from `Livre` WHERE `" + commande[1] + "` LIKE '%" + commande[2] + "%' ORDER BY " + commande[3]

    elif commande[0] == "livres_tri":
        requete = "SELECT * from `Livre` ORDER BY " + commande[1]

    elif commande[0] == "livres_deposes":
        requete = "SELECT * from `Livre` WHERE `depositaire` = '" + commande[1] + "'"

    elif commande[0] == "livres_reserves":
        requete = "SELECT l.* from Livre AS l JOIN Reservation AS r ON r.livre = l.id WHERE r.user = '" + commande[1] + "'"

    elif commande[0] == "trouver_compte":
        requete = "SELECT `mail`, `mot_de_passe`, `pseudo`, `score` FROM `Compte` WHERE `mail` = '" + commande[1] + "' AND `mot_de_passe` = '" + commande[2] + "'"

    elif commande[0] == "reserver_livre":
        requete = "INSERT INTO `Reservation` (`user`, `livre`,`date_resa`) VALUES ('" + commande[1] + "', '" + commande[2] + "', '" + commande[3] + "')"

    elif commande[0] == "annuler_reservation":
        requete = "DELETE FROM `Reservation` WHERE `user` = '" + commande[1] + "' AND `livre` = '" + commande[2] + '" AND `date_resa` = "' + commande[3] + "'"

    elif commande[0] == "retirer_livre":
        requete = "DELETE FROM Reservation WHERE `livre` = " + commande[1]
        send_requete(requete, conn, commande[0], cursor)
        requete = "DELETE FROM `Livre` WHERE `id` = '" + commande[1] + "'"

    elif commande[0] == "nb_reservations":
        requete = "SELECT * FROM `Reservation` WHERE `livre` = '" + commande[1] + "'"

    elif commande[0] == "a_reserve":
        requete = "SELECT * FROM `Reservation` WHERE `user` = '" + commande[1] + "' and `livre` = '" + commande[2] + "'"

    elif commande[0] == "liste_reservations":
        requete = "SELECT `mail` FROM `Compte` JOIN `Reservation` ON `Compte`.`mail` = `Reservation`.`user`" \
                  "WHERE `Reservation`.`livre` = " + commande[1] + " ORDER BY `Compte`.`score` DESC"

    else:
        res = "commande invalide"

    res = send_requete(requete, conn, commande[0], cursor)
    conn.close()
    return res


# - - - SOCKET - - - #


class ClientThread(threading.Thread):

    # création d'un thread pour communiquer à une nouvelle adresse
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket

    # boucle du thread
    def run(self):
        print("Connexion de %s au port %s" % (self.ip, self.port,))
        message = ""
        while message != "stop":
            message = self.clientsocket.recv(8192).decode()
            try:
                commande = scinder(message)
                try:
                    reponse = traiter(commande)
                    self.clientsocket.send(reponse.encode())
                except Exception as e:
                    print(e)
            except:
                break
        print("\nARRET DU THREAD\n\n")


print("Lancement de server.py")
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(("", 42000))
initialisation_base()


while True:
    tcpsock.listen(10)
    print("En ecoute...")
    (monsocket, (adresse, monport)) = tcpsock.accept()
    newthread = ClientThread(adresse, monport, monsocket)
    newthread.start()
