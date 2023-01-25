from tkinter.colorchooser import askcolor
from tkintermapview import TkinterMapView
from tkinter import filedialog
from recherche import *
from compte import *


# initialisation de la fenêtre graphique
def init(window):
    window.title("Geev - Chargement...")
    window.iconphoto(True, PhotoImage(file="images/icone.png"))
    window.resizable(False, False)
    canvas = Canvas(window, width=largeur, height=hauteur)
    canvas.pack()
    return canvas


# détermine si un texte représente un entier positif
def is_int(pages):
    try:
        tempo = int(pages)
        return tempo > 0
    except:
        return False


# fenêtre de choix de couleur
def choix_couleur(defaut):
    res = askcolor(color=defaut, title="Choix de couleur de fond")
    return res[1]


# page d'acceuil
class Acceuil(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas

        self.texte = \
            "Bienvenue sur notre projet ! \nNotre but : premettre à tout le monde \nde donner des livres \n" \
            "et en récupérer gratuitement, \nun peu à la manière d'un réseau \nde cabanes à livres en ligne. \n" \
            "Pour récupérer des livre, \nil faut en déposer : \nc'est donnant donnant."

        # Crée le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400)
        img = Image.open("images/logo.png")
        img = img.resize((406, 610), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(img)
        self.content.create_image(520, 170, image=self.logo)

        self.titre = Label(self.content, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Accueil', fg='darkblue')

    # affiche la page
    def show(self):
        self.content.place(x=cx - 350, y=cy - 200)
        self.titre.place(x=150, y=10, width=400)
        Label(self.content, text=self.texte, font="{Courier New} 10 normal").place(x=20, y=120)

    # cache la page
    def hide(self):
        self.content.place_forget()


# page d'affichage d'un livre
class PageLivre(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas
        self.livre = Livre(0, "", "", "", 0, "", "", "", "")
        self.nb_reserv = None
        self.reserver = None
        self.nom = "Aucun livre choisi"

        # image d'illustration du livre
        self.illustr = Canvas(canevas, width=largeur/4, height=largeur/3, highlightthickness=0)
        self.illustr.create_image(0, 0, image=ouvrir("images/Lenna.png"))

        # titre du livre en haut de page
        self.titre = Label(self.canevas, font="{U.S. 101} 15 bold", borderwidth=6, padx=20,
                           relief=SUNKEN, text=self.nom, fg='darkblue')

        # propriétés du livre
        self.auteur = Label(canevas, text="Auteur", padx=5, pady=5,
                            background=user.couleur_interface, foreground=user.couleur_texte)
        self.genre = Label(canevas, text="Genre", padx=5, pady=5,
                           background=user.couleur_interface, foreground=user.couleur_texte)
        self.pages = Label(canevas, text="Pages", padx=5, pady=5,
                           background=user.couleur_interface, foreground=user.couleur_texte)

        # délais de l'annonce
        self.date_depot = Label(canevas, text="Date de dépôt", padx=5, pady=5,
                                background=user.couleur_interface, foreground=user.couleur_texte)
        self.date_retrait = Label(canevas, text="Date de retrait", padx=5, pady=5,
                                  background=user.couleur_interface, foreground=user.couleur_texte)
        self.erreur = Label(canevas, text="Se connecter pour réserver/retirer un livre", padx=5, pady=5,
                            background=user.couleur_interface, foreground=user.couleur_texte)

        # boutons
        self.retirer = Button(self.canevas, text="Retirer", command=self.retrait,
                              background=user.couleur_interface, foreground=user.couleur_texte)
        self.annuler = Button(self.canevas, text="Retirer l'annonce", command=self.popup,
                              background=user.couleur_interface, foreground=user.couleur_texte)
        self.adresse = Button(self.canevas, text="Voir l'adresse", command=self.voir_adresse,
                              background=user.couleur_interface, foreground=user.couleur_texte)

    # place les données d'un livre dans la page
    def reset(self, livre):
        self.livre = livre
        self.nom = livre.titre
        self.titre.configure(text=self.nom)
        self.auteur.configure(text="Auteur : " + livre.auteur)
        self.genre.configure(text="Genre : "+livre.genre)
        self.pages.configure(text="Nombre de pages : "+str(livre.pages))
        self.date_depot.configure(text="Date de dépôt : " + livre.depot)
        self.date_retrait.configure(text="Date de retrait : " + livre.retrait)

        # si l'utilistauer a réservé ce livre, on affiche son rang de priorités et les commandes correspondantes
        if a_reserve(user.mail, livre.id) == "1":
            self.nb_reserv = Label(self.canevas, text="Votre rang de priorité : " + self.rang(user.mail) + " / " + nb_reservations(livre.id),
                                   padx=5, pady=5, background=user.couleur_interface, foreground=user.couleur_texte)
            self.reserver = Button(self.canevas, text="Déréserver", command=self.dereservation,
                                   background=user.couleur_interface, foreground=user.couleur_texte)

        # sinon, il peut le réserver si le délai correspondant n'est pas dépassé ou si personne n'a réservé le livre à temps
        else:
            reservations = int(nb_reservations(livre.id))
            texte_reserv = StringVar()
            texte_reserv.set("Personne n'a réservé ce livre")
            self.nb_reserv = Label(self.canevas, textvariable=texte_reserv,
                                   padx=5, pady=5, background=user.couleur_interface, foreground=user.couleur_texte)
            if reservations > 0:
                texte_reserv.set(str(reservations) + " utilisateurs veulent ce livre")
            if livre.retrait > today or reservations == 0:
                self.reserver = Button(self.canevas, text="Réserver", command=self.reservation,
                                       background=user.couleur_interface, foreground=user.couleur_texte)
            else:
                self.reserver = Label(self.canevas, text="Délai de réservation passé", padx=5, pady=5,
                                      background=user.couleur_interface, foreground=user.couleur_texte)

        # si l'utilisateur a déposé ce livre, il peut retirer l'annonce
        if user.mail == livre.depositaire:
            self.annuler.configure(command=self.annulation)

    # affiche la page
    def show(self):
        self.illustr.place(x=cx*0.5, y=80)
        self.titre.place(x=cx - 5*self.nom.__len__(), y=20)
        self.auteur.place(x=cx*1.2, y=80)
        self.genre.place(x=cx*1.2, y=120)
        self.pages.place(x=cx*1.2, y=160)
        self.date_depot.place(x=cx*1.2, y=200)
        self.date_retrait.place(x=cx*1.2, y=240)
        if self.livre.adresse != "":
            self.adresse.place(x=cx*1.2, y=360)
        try:
            self.nb_reserv.place(x=cx * 1.2, y=280)
            if user.connecte:
                print(user.mail)
                print(self.livre.depositaire)
                if user.mail == self.livre.depositaire:
                    self.annuler.place(x=cx*1.2, y=320)
                elif user.score >= 10 or a_reserve(user.mail, self.livre.id) == "1":
                    self.reserver.place(x=cx*1.2, y=320)
                    if self.rang(user.mail) == "1" and self.livre.retrait <= today:
                        self.retirer.place(x=cx*1.2 + 100, y=320)
            else:
                self.erreur.place(x=cx*1.2, y=320)
        except Exception as e:
            print(e)

    # cache la page
    def hide(self):
        self.illustr.place_forget()
        self.titre.place_forget()
        self.auteur.place_forget()
        self.genre.place_forget()
        self.pages.place_forget()
        self.date_depot.place_forget()
        self.date_retrait.place_forget()
        self.erreur.place_forget()
        self.adresse.place_forget()
        try:
            self.nb_reserv.place_forget()
            self.reserver.place_forget()
            self.retirer.place_forget()
            self.annuler.place_forget()
        except Exception as e:
            print(e)

    # rafraishit la page
    def refresh(self):
        self.hide()
        self.reset(self.livre)
        self.show()

    def reservation(self):
        reserver_livre(user.mail, self.livre.id, today)
        compte.livres.remplir()
        compte.membre.reserv.configure(text="Livres réservés : " + str(len(compte.livres.reserv.liste)))
        self.refresh()

    def dereservation(self):
        annuler_reservation(user.mail, self.livre.id, today)
        compte.livres.remplir()
        compte.membre.reserv.configure(text="Livres réservés : " + str(len(compte.livres.reserv.liste)))
        self.refresh()

    # retire un livre
    def retrait(self):
        retirer_livre(self.livre.id)
        annuler_toute_reservation(self.livre.id)
        ajout_score(user.mail, (user.score - 10))
        compte.livres.remplir()
        compte.membre.reserv.configure(text="Livres réservés : " + str(len(compte.livres.reserv.liste)))
        self.hide()
        self.__init__(self.canevas)
        carte.map_widget.set_address(self.livre.adresse, marker=True)
        messagebox.showinfo("Livre retiré", "Redirection vers la carte pour voir son adresse.")
        carte.show()

    # retourne le rang de priorité d'user pour le livre choisi
    def rang(self, mail):
        liste = to_liste(liste_reservations(self.livre.id))
        print(liste)
        i = 0
        trouve = False
        while i < len(liste) and not trouve:
            trouve = mail == liste[i]
            i += 1
        return str(i)

    # demande confirmation pour retirer l'annonce d'un livre
    def annulation(self):
        res = messagebox.askokcancel("Supprimer ce livre", "Voulez-vous vraiment supprimer l'annonce de ce livre ?\n")
        if res:
            retirer_livre(self.livre.id)
            ajout_score(user.mail, -10)
            compte.livres.remplir()
            compte.membre.depots.configure(text="Livres déposés : " + str(len(compte.livres.depots.liste)))
            page_acceuil()

    # montre l'adresse du livre dans la carte
    def voir_adresse(self):
        carte.map_widget.set_address(self.livre.adresse, marker=True)
        self.hide()
        carte.show()

    # indique l'inutilité de cliquer sur un bouton
    @staticmethod
    def popup():
        messagebox.showerror("Aucun livre choisi", "Cette action est impossible.")


# page d'ajout de livre
class Ajout(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas
        self.image = None

        # Crée le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400)
        img = Image.open("images/logo.png")
        img = img.resize((406, 610), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(img)
        self.content.create_image(520, 170, image=self.logo)

        # titre de la page et bouton de validation
        self.titre = Label(self.content, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Ajouter un livre', fg='darkblue')
        self.ajout = Button(self.content, text="Ajouter livre", command=self.ajout,
                            background=user.couleur_interface, foreground=user.couleur_texte)

        # imporation de fichier image
        self.parcourir = Button(self.content, text="Parcourir", command=self.importation)
        self.nom_image = Label(self.content, text="Aucun fichier sélectionné")

        # saisies des informations
        self.nom = Entry(self.content)
        self.auteur = Entry(self.content)
        self.genre = Entry(self.content)
        self.pages = Entry(self.content)
        self.adresse = Entry(self.content)
        self.date = DateEntry(self.content)

    # affiche la page
    def show(self):
        self.content.place(x=largeur/2-350, y=hauteur/2-200)
        self.titre.place(x=150, y=10, width=400)
        self.ajout.place(x=400, y=350)
        self.parcourir.place(x=200, y=280)
        self.nom_image.place(x=200, y=310)

        # saisies des informations
        self.nom.place(x=200, y=80)
        self.auteur.place(x=200, y=120)
        self.genre.place(x=200, y=160)
        self.pages.place(x=200, y=200)
        self.date.place(x=200, y=240)
        self.adresse.place(x=200, y=330)

        # textes invariables
        Label(self.content, text="Titre*", padx=5, pady=5).place(x=50, y=80)
        Label(self.content, text="Auteur*", padx=5, pady=5).place(x=50, y=120)
        Label(self.content, text="Genre*", padx=5, pady=5).place(x=50, y=160)
        Label(self.content, text="Pages*", padx=5, pady=5).place(x=50, y=200)
        Label(self.content, text="Récupération", padx=5, pady=5).place(x=50, y=240)
        Label(self.content, text="Image", padx=5, pady=5).place(x=50, y=280)
        Label(self.content, text="Adresse", padx=5, pady=5).place(x=50, y=330)

    # cache la page
    def hide(self):
        self.titre.place_forget()
        self.content.place_forget()

    # ajoute le livre si possible
    def ajout(self):
        date = self.date.get_date().isoformat()
        print(date)
        if date < today:
            messagebox.showwarning("Date impossible", "Voyager dans le passé n'est pas encore à la portée de nos utilisateurs.")
        elif not is_int(self.pages.get()):
            messagebox.showinfo("Erreur sur le nombre pages", "Entrée un entier positif en entrée ")
        elif len(self.nom.get()) > 0 and len(self.auteur.get()) > 0 and len(self.genre.get()) > 0 and len(self.pages.get()) > 0:
            if date == today:
                messagebox.showinfo("Date non informée", "La date de récupération sera fixée à aujourd'hui.")
            else:
                entrer_livre(self.nom.get(), self.auteur.get(), self.genre.get(), self.pages.get(), str(date), user.mail, self.adresse.get())
                dscore = 10 - int(user.score/50)
                if dscore < 5:
                    dscore = 5
                ajout_score(user.mail, (user.score + dscore))
                compte.livres.remplir()
                compte.membre.score.configure(text="Votre score : " + str(user.score))
                compte.membre.depots.configure(text="Livres déposés : " + str(len(compte.livres.depots.liste)))

                # on indique que l'ajout est terminé et on vide les entrées de texte pour éviter d'ajouter deux fois le même livre
                messagebox.showinfo("Ajout réussi", "Livre ajouté avec succès !")
                self.nom.delete(0, END)
                self.auteur.delete(0, END)
                self.genre.delete(0, END)
                self.pages.delete(0, END)

                print(export(self.image))
        else:
            messagebox.showerror("Champs manquants", "Veuillez remplir tous les champs obligatoires (*).")

    # procédure pour importer un fichier image
    def importation(self):
        # boîte de dialogue pour choisir le fichier dans la bibliothèque
        self.image = filedialog.askopenfile(initialdir="/", title="Choisissez une image",
                                            filetypes=(("Tous les fichiers", "*.*"), ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg")))
        # si l'on a choisi un fichier, on affiche son nom
        if self.image is not None:
            self.nom_image.configure(text=self.image.name)


class Carte(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas

        # CrÃ©e le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400, borderwidth=5)

        # create map widget
        self.map_widget = TkinterMapView(self.content, width=700, height=350, corner_radius=00,
                                         borderwidth=8, highlightcolor="black", highlightbackground="black",
                                         relief=RAISED)

        self.alert = Label(self.canevas, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Carte', fg='darkblue')

        # google normal tile server
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_address("Chambery France", marker=False)

        self.depart = Label(self.content, text='Départ', fg='darkblue', background=user.couleur_interface)
        self.arrive = Label(self.content, text='Adresse :', fg='darkblue', background=user.couleur_interface)

        self.arrivr = Button(self.content, text="Localiser", background=user.couleur_interface,
                             foreground=user.couleur_texte, command=self.chercher)
        self.arriv = Entry(self.content, foreground=user.couleur_texte, background=user.couleur_interface)

        self.resete = Button(self.content, text="Chambéry", background=user.couleur_interface,
                             foreground=user.couleur_texte, command=self.reset)
        self.dep = Entry(self.content, foreground=user.couleur_texte, background=user.couleur_interface)

    # affiche la page
    def show(self):
        self.content.place(x=cx - 345, y=cy - 200)
        self.alert.place(x=cx - 100, y=20, width=200)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.place(x=0, y=0)
        self.arrivr.place(x=500, y=365, width=100, height=20)
        # self.dep.place(x=100, y=365,width=300, height= 20)
        self.resete.place(x=500, y=390, width=100, height=20)
        self.arriv.place(x=100, y=390, width=300, height=20)

        # self.depart.place(x=5, y=365, width=100, height= 20)
        self.arrive.place(x=5, y=390, width=100, height=20)

        # self.titre.place(x=cx - 100, y=20, width=200)
        # self.texte.place(x=cx - 60, y=120)

    # cache la page
    def hide(self):
        self.content.place_forget()
        self.alert.place_forget()

    def chercher(self):
        self.map_widget.set_address(self.arriv.get(), marker=True)

    def reset(self):
        self.map_widget.set_address("Chambery France", marker=False)
        self.arriv.delete("0", "end")
        self.dep.delete("0", "end")


# contenu superposé indépendant de la page
class Global(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas

        # crée le canvas avec le fond et collé au bord de la fenêtre
        self.bg_frame = Canvas(canevas, width=largeur, height=hauteur, highlightthickness=0)
        self.bg_app = ImageTk.PhotoImage(Image.open('images/cc.png'))
        self.bg_frame.create_image(0, 0, image=self.bg_app, anchor='nw')
        self.bg_frame.place(x=0, y=0)

        # boutons de gauche pour changer de page (menu)
        self.b1 = Button(canevas, text="Acceuil", command=page_acceuil,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b2 = Button(canevas, text="Compte", command=page_compte,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b3 = Button(canevas, text="Recherche", command=page_recherche,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b4 = Button(canevas, text="Ajout", command=page_ajout,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b5 = Button(canevas, text="Livre", command=page_livre,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b6 = Button(canevas, text="Carte", command=page_carte,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.b7 = Button(canevas, text="Profil", command=page_compte,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.warning = Label(self.canevas, text="se connecter",
                             background=user.couleur_interface, foreground=user.couleur_texte)

        # boutons de choix des couleurs en haut à droite
        self.c1 = Button(canevas, text="Couleur de fond", command=self.set_fond,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.c2 = Button(canevas, text="Couleur interface", command=self.set_interface,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.c3 = Button(canevas, text="Couleur de texte", command=self.set_texte,
                         background=user.couleur_interface, foreground=user.couleur_texte)

        # affichage de la date en bas à gauche
        self.date = Label(canevas, text=today, background=user.couleur_interface, foreground=user.couleur_texte)

    def show(self):
        self.b1.place(x=20, y=20)
        self.b2.place(x=20, y=60)
        self.b3.place(x=20, y=100)
        self.b5.place(x=20, y=180)
        self.b6.place(x=20, y=220)
        self.c1.place(x=cx*2 - 110, y=20)
        self.c2.place(x=cx * 2 - 110, y=50)
        self.c3.place(x=cx * 2 - 110, y=80)
        self.date.place(x=20, y=hauteur - 40)

    def show_ajout(self):
        self.warning.place_forget()
        self.b4.place(x=20, y=140)

    def hide_ajout(self):
        self.warning.place(x=20, y=140)
        self.b4.place_forget()
        
    def show_Profil(self):
        self.b2.place_forget()
        self.b7.place(x=20, y=60)
        
    def hide_Profil(self):
        self.b2.place(x=20, y=60)
        self.b7.place_forget()

    # personnalisation de la couleur d'interface
    def set_fond(self):
        col = choix_couleur(user.couleur_fond)
        user.couleur_fond = col

        compte.livres.can_reserv.configure(background=col)
        compte.livres.can_depots.configure(background=col)
        recherche.recherche.can_res.configure(background=col)

    # personnalisation de la couleur d'interface
    # beaucoup de modification par ici attention
    def set_interface(self):
        col = choix_couleur(user.couleur_interface)
        user.couleur_interface = col

        # widgets du menu
        self.b1.configure(background=col)
        self.b2.configure(background=col)
        self.b3.configure(background=col)
        self.b4.configure(background=col)
        self.b5.configure(background=col)
        self.b6.configure(background=col)
        self.b7.configure(background=col)
        self.warning.configure(background=col)
        self.date.configure(background=col)
        self.c1.configure(background=col)
        self.c2.configure(background=col)
        self.c3.configure(background=col)

        # boutons des pages de compte
        compte.membre.delete.configure(background=col)
        compte.membre.logout.configure(background=col)
        compte.membre.livres.configure(background=col)
        compte.membre.updat.configure(background=col)
        compte.modifier.submit.configure(background=col)
        compte.modifier.back.configure(background=col)
        compte.connexion.signup.configure(background=col)
        compte.connexion.submit.configure(background=col)
        compte.inscription.back.configure(background=col)
        compte.inscription.submit.configure(background=col)

        # widgets des pages de recherche
        recherche.recherche.valider.configure(background=col)
        recherche.recherche.entree.configure(background=col)
        recherche.recherche.filtre.configure(background=col)
        recherche.recherche.tri.configure(background=col)
        recherche.recherche.modif.configure(background=col)
        recherche.preferences.reset.configure(background=col)
        recherche.preferences.valider.configure(background=col)

        # labels de la page de livre
        ajout.ajout.configure(background=col)
        pagelivre.auteur.configure(background=col)
        pagelivre.genre.configure(background=col)
        pagelivre.pages.configure(background=col)
        pagelivre.date_depot.configure(background=col)
        pagelivre.date_retrait.configure(background=col)
        pagelivre.erreur.configure(background=col)
        pagelivre.adresse.configure(background=col)
        try:
            pagelivre.nb_reserv.configure(background=col)
            pagelivre.reserver.configure(background=col)
            pagelivre.retirer.configure(background=col)
        except:
            pass

        # widgets de la page de carte
        carte.arriv.configure(background=col)
        carte.arrive.configure(background=col)
        carte.arrivr.configure(background=col)
        carte.resete.configure(background=col)

    # personnalisation de la couleur d'interface
    def set_texte(self):
        col = choix_couleur(user.couleur_texte)
        user.couleur_texte = col

        # widgets du menu
        self.b1.configure(foreground=col)
        self.b2.configure(foreground=col)
        self.b3.configure(foreground=col)
        self.b4.configure(foreground=col)
        self.b5.configure(foreground=col)
        self.b6.configure(foreground=col)
        self.b7.configure(foreground=col)
        self.warning.configure(foreground=col)
        self.date.configure(foreground=col)
        self.c1.configure(foreground=col)
        self.c2.configure(foreground=col)
        self.c3.configure(foreground=col)

        # boutons des pages de compte
        compte.membre.updat.configure(foreground=col)
        compte.membre.livres.configure(foreground=col)
        compte.membre.delete.configure(foreground=col)
        compte.membre.logout.configure(foreground=col)
        compte.modifier.submit.configure(foreground=col)
        compte.modifier.back.configure(foreground=col)
        compte.connexion.signup.configure(foreground=col)
        compte.connexion.submit.configure(foreground=col)
        compte.inscription.back.configure(foreground=col)
        compte.inscription.submit.configure(foreground=col)

        # widgets des pages de recherche
        recherche.recherche.valider.configure(foreground=col)
        recherche.recherche.entree.configure(foreground=col)
        recherche.recherche.filtre.configure(foreground=col)
        recherche.recherche.tri.configure(foreground=col)
        recherche.recherche.modif.configure(foreground=col)
        recherche.preferences.reset.configure(foreground=col)
        recherche.preferences.valider.configure(foreground=col)

        # labels de la page de livre
        ajout.ajout.configure(foreground=col)
        pagelivre.auteur.configure(foreground=col)
        pagelivre.genre.configure(foreground=col)
        pagelivre.pages.configure(foreground=col)
        pagelivre.date_depot.configure(foreground=col)
        pagelivre.date_retrait.configure(foreground=col)
        pagelivre.erreur.configure(foreground=col)
        pagelivre.adresse.configure(foreground=col)
        try:
            pagelivre.nb_reserv.configure(foreground=col)
            pagelivre.reserver.configure(foreground=col)
            pagelivre.retirer.configure(foreground=col)
        except:
            pass

        # widgets de la page de carte
        carte.arriv.configure(foreground=col)
        carte.arrive.configure(foreground=col)
        carte.arrivr.configure(foreground=col)
        carte.resete.configure(foreground=col)


# procédure effaçant la fenêtre
def effacer():
    global acceuil, compte, recherche, ajout, pagelivre
    acceuil.hide()
    compte.hide()
    recherche.hide()
    ajout.hide()
    pagelivre.hide()
    carte.hide()


# procédures affichant les différentes pages
def page_acceuil():
    effacer()
    acceuil.show()
    root.title("Geev - Acceuil")


def page_compte():
    effacer()
    if user.connecte:
        compte.membre.show()
        root.title("Geev - Gestion du compte")
    else:
        compte.connexion.show()
        root.title("Geev - Connexion")
        

def page_recherche():
    effacer()
    recherche.show()
    root.title("Geev - Recherche de livres")


def page_ajout():
    effacer()
    ajout.show()
    root.title("Geev - Dépôt de livre")


def page_livre():
    effacer()
    pagelivre.show()
    root.title("Geev - " + pagelivre.nom)


def page_carte():
    effacer()
    carte.arriv.delete("0", "end")
    carte.arriv.delete("0", "end")
    carte.show()
    root.title("Geev - Carte")


# retourne une image rognée en 3:4 selon son chemin relatif
# normalement ça marche mais là non
def ouvrir(chemin):
    img = Image.open(chemin)
    w, h = img.size
    ratio = h/w
    box = (0, 0, w, h)
    if ratio > 4/3:
        nh = int(w*4/3)
        box = (0, int((h-nh)/2), w, nh + int((h-nh/2)))
    elif ratio < 4/3:
        nw = int(h*3/4)
        box = (int((w-nw)/2), 0, nw + int((w-nw)/2), h)
    # res = ImageTk.PhotoImage(img.crop(box).resize((int(largeur/4), int(largeur/3))))
    res = ImageTk.PhotoImage(img.resize((int(largeur/4), int(largeur/3))))
    return res


root = Tk()
graph = init(root)
graph.create_rectangle(0, 0, largeur + 10, hauteur + 10, fill=user.couleur_fond)
root.geometry(str(largeur) + "x" + str(hauteur))


globalle = Global(graph)
acceuil = Acceuil(graph)
ajout = Ajout(graph)
pagelivre = PageLivre(graph)
compte = Compte(graph, globalle, pagelivre)
recherche = GestionRecherche(graph, pagelivre)
carte = Carte(graph)

globalle.show()
globalle.hide_ajout()
page_acceuil()
