from tkinter import *
from tkinter import messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from modifier import Modifier
from donnees import *
from client import *
import re


largeur, hauteur = 1000, 600
cx, cy = largeur/2, hauteur/2


# gestion des pages liées au compte
class Compte:
    def __init__(self, canevas, menu, page_livre):
        self.menu = menu
        self.user = Utilisateur()
        self.livres = MesLivres(canevas, self, page_livre)
        self.membre = Membre(canevas, self)
        self.modifier = Modifier(canevas, self)
        self.connexion = Connexion(canevas, self)
        self.inscription = Inscription(canevas, self)
        self.erreur = Erreur(canevas)
        self.page = "connexion"

    def show(self):
        exec("self.%s.show()" % self.page)

    def hide(self):
        self.membre.hide()
        self.livres.hide()
        self.connexion.hide()
        self.inscription.hide()
        self.erreur.hide()

    def change_to(self, page):
        self.hide()
        self.page = page
        self.show()

    def on_signup(self):
        self.connexion.hide()
        self.connexion.mail.delete("0", "end")
        self.connexion.password.delete("0", "end")
        self.inscription.show()

    def on_login(self):
        self.inscription.hide()
        self.inscription.pseudo.delete("0", "end")
        self.inscription.password.delete("0", "end")
        self.inscription.mail.delete("0", "end")
        self.inscription.password_repeat.delete("0", "end")
        self.connexion.show()

    def login_success(self):
        self.inscription.hide()
        self.connexion.hide()
        self.membre.show()

    def click_modif(self):
        self.membre.hide()
        self.modifier.show()


# page de membre
class Membre(Frame):
    def __init__(self, canevas, gestionnaire):
        super().__init__()
        self.canevas = canevas
        self.gestionnaire = gestionnaire

        # crée le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400)
        img = Image.open("images/logo.png")
        img = img.resize((406, 610), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(img)
        self.content.create_image(520, 170, image=self.logo)

        # affiche l'alerte
        self.alert = Label(self.content, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Page de membre', fg='darkblue')

        # informations utilisateur
        self.bienvenue = Label(self.content, text="Bonjour...?", font="{Courier New} 10 normal")
        self.mail = Label(self.content, text="Votre mail : ???", font="{Courier New} 10 normal")
        self.score = Label(self.content, text="Votre score : ???", font="{Courier New} 10 normal")
        self.reserv = Label(self.content, text="Livres réservés : ???", font="{Courier New} 10 normal")
        self.depots = Label(self.content, text="Livres déposés : ???", font="{Courier New} 10 normal")

        # boutons de commandes
        self.livres = Button(self.content, text="Voir mes livres", command=self.voir_livres,
                             fg=user.couleur_texte, bg=user.couleur_interface)
        self.logout = Button(self.content, text='Se déconnecter', command=self.deconnection,
                             fg=user.couleur_texte, bg=user.couleur_interface)
        self.delete = Button(self.content, text='Supprimer', command=self.suppression,
                             fg=user.couleur_texte, bg=user.couleur_interface)
        self.updat = Button(self.content, text='Modifier', command=self.modifier,
                            fg=user.couleur_texte, bg=user.couleur_interface)

    def connexion(self):
        self.gestionnaire.livres.remplir()
        txt = "Bonjour, %s !" % self.gestionnaire.user.pseudo
        self.bienvenue.configure(text=txt)
        self.mail.configure(text="Votre mail : "+self.gestionnaire.user.mail)
        self.score.configure(text="Votre score : " + str(self.gestionnaire.user.score))
        self.reserv.configure(text="Livres réservés : " + str(len(self.gestionnaire.livres.reserv.liste)))
        self.depots.configure(text="Livres déposés : " + str(len(self.gestionnaire.livres.depots.liste)))
        
    def show(self):
        self.content.place(x=cx - 350, y=cy - 200)
        self.alert.place(x=150, y=10, width=400)
        self.bienvenue.place(x=50, y=80)
        self.mail.place(x=50, y=120)
        self.score.place(x=50, y=160)
        self.reserv.place(x=50, y=200)
        self.depots.place(x=50, y=240)
        self.livres.place(x=50, y=280)
        self.updat.place(x=75, y=370, width=150)
        self.logout.place(x=275, y=370, width=150)
        self.delete.place(x=475, y=370, width=150)

    def hide(self):
        self.content.place_forget()

    # redirige vers la page listant les livres déposés et réservés
    def voir_livres(self):
        self.gestionnaire.change_to("livres")

    # redirige vers la page de modification des informations
    def modifier(self):
        self.hide()
        self.gestionnaire.modifier.mail.delete("0", "end")
        self.gestionnaire.modifier.pseudo.delete("0", "end")
        self.gestionnaire.modifier.password.delete("0", "end")
        self.gestionnaire.click_modif()

    # on se déconnecte du compte pour retourner à la page de connection
    def deconnection(self):
        """ Evenement pour se déconnecter du jeu """
        self.event_generate('<<LOGOUT_GAME>>')
        self.gestionnaire.user.deconnection()
        self.hide()
        self.gestionnaire.menu.hide_ajout()
        self.gestionnaire.menu.hide_Profil()
        self.gestionnaire.on_login()
        user.deconnection()
        self.gestionnaire.connexion.password.delete("0", "end")
        self.gestionnaire.connexion.mail.delete("0", "end")

    # on demande confirmation pour la suppression, et si c'est bon, on se déconnecte et on supprime le compte
    def suppression(self):
        res = messagebox.askokcancel("Supprimer mon compte", "Voulez-vous vraiment supprimer ce compte ?\nCette action est irréversible.")
        if res:
            Supprimer_compte(self.gestionnaire.user.mail)
            self.deconnection()


# page de gestion des livres déposés et réservés
class MesLivres(Frame):
    def __init__(self, canevas, gestionnaire, page):
        super().__init__()
        self.canevas = canevas
        self.gestionnaire = gestionnaire
        self.page = page
        self.reserv = Bibliotheque()
        self.depots = Bibliotheque()
        self.res_a, self.res_b = [], []
        self.bouton_a, self.bouton_b = [], []

        # canevas contenant les deux listes de livres
        cx = self.canevas.winfo_width() / 2
        cy = self.canevas.winfo_height() / 2
        self.txt_reserv = Label(self.canevas, font="{U.S. 101} 12 bold", borderwidth=4, relief=SUNKEN, text='Réservés', fg='darkblue')
        self.txt_depots = Label(self.canevas, font="{U.S. 101} 12 bold", borderwidth=4, relief=SUNKEN, text='Déposés', fg='darkblue')
        self.can_reserv = Canvas(canevas, width=cx + 160, height=cy * 2 - 140, background=user.couleur_fond)
        self.can_depots = Canvas(canevas, width=cx + 160, height=cy * 2 - 140, background=user.couleur_fond)

        self.titre = Label(canevas, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Mes livres', fg='darkblue')

    def show(self):
        self.remplir()
        cx = self.canevas.winfo_width()/2
        cy = self.canevas.winfo_height()/2
        self.titre.place(x=cx - 100, y=20, width=200)
        self.txt_reserv.place(x=120, y=90, width=100)
        self.txt_depots.place(x=cx + 70, y=90, width=100)
        self.can_reserv.place(x=100, y=120, width=cx - 70, height=cy * 2 - 140)
        self.can_depots.place(x=cx + 50, y=120, width=cx - 70, height=cy * 2 - 140)

        # liste des livres réservés
        if self.reserv.nombre > 0:
            for i in range(self.reserv.nombre):
                self.res_a.append(Label(self.can_reserv, text=self.reserv.liste[i], padx=5, pady=5,
                                        background=user.couleur_interface, foreground=user.couleur_texte))
                self.res_a[i].place(x=80, y=20 + 40 * i)
                self.bouton_a.append(Button(self.can_reserv, text="Voir plus", command=self.voir_reserv,
                                            background=user.couleur_interface, foreground=user.couleur_texte))
                self.bouton_a[i].place(x=20, y=20 + 40 * i)
        else:
            self.res_a.append(Label(self.can_reserv, text="Aucun livre trouvé", padx=5, pady=5,
                                    background=user.couleur_interface, foreground=user.couleur_texte))
            self.res_a[0].place(x=20, y=20)

        # liste des livres déposés
        if self.depots.nombre > 0:
            for i in range(self.depots.nombre):
                self.res_b.append(Label(self.can_depots, text=self.depots.liste[i], padx=5, pady=5,
                                        background=user.couleur_interface, foreground=user.couleur_texte))
                self.res_b[i].place(x=80, y=20 + 40 * i)
                self.bouton_b.append(Button(self.can_depots, text="Voir plus", command=self.voir_depots,
                                            background=user.couleur_interface, foreground=user.couleur_texte))
                self.bouton_b[i].place(x=20, y=20 + 40 * i)
        else:
            self.res_b.append(Label(self.can_depots, text="Aucun livre trouvé", padx=5, pady=5,
                                    background=user.couleur_interface, foreground=user.couleur_texte))
            self.res_b[0].place(x=20, y=20)

    def hide(self):
        self.titre.place_forget()
        self.txt_reserv.place_forget()
        self.txt_depots.place_forget()
        self.can_reserv.place_forget()
        self.can_depots.place_forget()
        self.clear()

    # vide les listes de résultast et de boutons
    def clear(self):
        try:
            for i in range(len(self.res_a)):
                self.res_a[i].place_forget()
                self.bouton_a[i].place_forget()
        except:
            pass
        try:
            for i in range(len(self.res_b)):
                self.res_b[i].place_forget()
                self.bouton_b[i].place_forget()
        except:
            pass
        self.res_a.clear()
        self.res_b.clear()
        self.bouton_a.clear()
        self.bouton_b.clear()

    # appel de self.voir_livre depuis can_reserv
    def voir_reserv(self):
        self.voir_livre(self.can_reserv.winfo_pointery() - self.can_reserv.winfo_rooty(), self.reserv)

    # appel de self.voir_livre depuis can_depots
    def voir_depots(self):
        self.voir_livre(self.can_depots.winfo_pointery() - self.can_depots.winfo_rooty(), self.depots)

    # renvoi vers la page du livre choisi (bouton "voir plus")
    def voir_livre(self, y, biblio):
        i = int((y - 20) / 40)
        print("Position : " + str(y))
        print("Indice : " + str(i))
        self.page.reset(biblio.liste[i])
        self.hide()
        self.page.show()

    # met à jour les deux listes (tri par défaut)
    def remplir(self):
        self.reserv.set(to_livres(livres_reserves(self.gestionnaire.user.mail)))
        self.depots.set(to_livres(livres_deposes(self.gestionnaire.user.mail)))
        print("Livres réservés :\n" + self.reserv.__str__())
        print("Livres déposés : \n" + self.depots.__str__())


# page de connexion
class Connexion(Frame):
    __trials = 3  # nombre d'essais maximum de connexion

    def __init__(self, canevas, gestionnaire):
        super().__init__()
        self.canevas = canevas
        self.gestionnaire = gestionnaire

        # Crée le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400)
        img = Image.open("images/logo.png")
        img = img.resize((406, 610), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(img)
        self.content.create_image(520, 170, image=self.logo)

        # Crée le compteur d'essais
        self.compteur = Label(self.content, bg='white', text=str(self.__trials) + ' essais restants', fg='orange')

        # Affiche l'alerte
        self.alert = Label(self.content, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Connexion', fg='darkblue')

        # champs de texte de pseudo et mot de passe
        self.mail = Entry(self.content)
        self.password = Entry(self.content, show='*')

        # boutons pour se connecter ou s'inscire
        self.submit = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface, text='Se connecter', command=self.on_login)
        self.signup = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface, text='Pas encore de compte ?', command=self.gestionnaire.on_signup)

    def show(self):
        self.content.place(x=cx - 350, y=cy - 200)
        self.compteur.place(x=155, y=10)
        self.alert.place(x=150, y=10, width=400)
        Label(self.content, text='Mail', font="{Courier New} 10 normal").place(x=50, y=130)
        self.mail.place(x=200, y=130)
        Label(self.content, text='Mot de passe', font="{Courier New} 10 normal").place(x=50, y=200)
        self.password.place(x=200, y=200)
        self.submit.grid(ipadx=10, ipady=2)
        self.submit.place(x=150, y=370, width=150)
        self.signup.grid(ipadx=10, ipady=2)
        self.signup.place(x=400, y=370, width=150)

    def hide(self):
        self.content.place_forget()

    def on_login(self):
        """ Bouton de connexion pressé, il faut vérifier les données """

        # on vérifie que les deux champs soient remplis
        if not self.mail.get() or not self.password.get():
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
        else:
            compte = trouver_compte(self.mail.get(), self.password.get())
            # le pseudo et le mot de passe correspondent
            if compte != "[]":
                # si les données sont correctes, on génère l'évènement pour ouvrir la page de membre
                self.event_generate('<<LOGIN_SUCCES>>')
                try:
                    print("Compte trouvé :", compte)
                    temp = to_user(compte)
                    self.gestionnaire.user.insertion(temp.mail, temp.mdp, temp.pseudo, temp.score)
                    self.gestionnaire.user.connexion()
                    user.connexion()
                    self.gestionnaire.menu.show_Profil()
                    self.gestionnaire.menu.show_ajout()
                    self.gestionnaire.membre.connexion()
                except Exception as e:
                    print(e)
                finally:
                    self.gestionnaire.login_success()
            else:
                self.password.delete(0, END)  # supprime le mot de passe pré-rempli
                messagebox.showerror("Connexion imposible", "Identifiant ou mot de passe incorrect.")
                self.__trials -= 1  # consomme 1 essai

    def on_signup(self):
        # génère l'évenement pour ouvrir la page d'inscription
        self.event_generate('<<SIGNUP_PRESS>>')


# page d'insciption
class Inscription(Frame):
    def __init__(self, canevas, gestionnaire):
        super().__init__()
        self.canevas = canevas
        self.gestionnaire = gestionnaire

        # Crée le conteneur des informations
        self.content = Canvas(self.canevas, width=700, height=400)
        img = Image.open("images/logo.png")
        img = img.resize((406, 610), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(img)
        self.content.create_image(520, 170, image=self.logo)

        # Affiche l'alerte
        self.alert = Label(self.content, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Inscription', fg='darkblue')
        self.pseudo = Entry(self.content)
        self.mail = Entry(self.content)
        self.alert.place(x=150, y=10, width=400)

        # boutons pour le choix du sexe
        self.valeurSexe = StringVar()
        self.M = Radiobutton(self.content, text="MASCULIN", value="homme",
                             variable=self.valeurSexe, indicatoron=False, font=("Arial", 10))
        self.F = Radiobutton(self.content, text="FEMININ", value="femme",
                             variable=self.valeurSexe, indicatoron=False, font=("Arial", 10))

        # calendrier dynamique pour la date de naissance
        self.dateN = DateEntry(self.content)

        # entrées du mot de passe
        self.password = Entry(self.content, show='*')
        self.password_repeat = Entry(self.content, show='*')

        # boutons du bas
        self.submit = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface, text="S'inscrire", command=self.on_signup)
        self.back = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface,
                           text="J'ai déjà un compte", command=self.gestionnaire.on_login)

    def show(self):
        self.content.place(x=largeur/2-350, y=hauteur/2-200)
        Label(self.content, text='Pseudonyme* :', font="{Courier New} 10 normal").place(x=50, y=80)
        self.pseudo.place(x=200, y=80)
        Label(self.content, text='Mail* :', font="{Courier New} 10 normal").place(x=50, y=130)
        self.mail.place(x=200, y=130)
        Label(self.content, text='Genre :', font="{Courier New} 10 normal").place(x=50, y=180)
        self.M.place(x=160, y=180)
        self.F.place(x=260, y=180, width=80)
        Label(self.content, text='Naissance :', font="{Courier New} 10 normal").place(x=50, y=230)
        self.dateN.place(x=200, y=230, width=124)
        Label(self.content, text='Mot de passe* :', font="{Courier New} 10 normal").place(x=50, y=280)
        self.password.place(x=200, y=280)
        Label(self.content, text='Confirmation* :', font="{Courier New} 10 normal").place(x=50, y=330)
        self.password_repeat.place(x=200, y=330)
        self.submit.grid(ipadx=10, ipady=2)
        self.submit.place(x=150, y=370, width=150)
        self.back.grid(ipadx=10, ipady=2)
        self.back.place(x=400, y=370, width=150)

    def hide(self):
        self.content.place_forget()

    def back_page(self):
        """ Retourne sur la page de connexion """
        self.event_generate('<<SIGNUP_BACK>>')

    def on_signup(self):
        """ Bouton d'inscription pressé, il faut vérifier les données """
        error = []  # Liste vide pour les erreurs
        date = self.dateN.get_date().isoformat()
        

        # on vérifie que tous les champs sont remplis
        if not self.pseudo.get() or not self.password.get() or not self.password_repeat.get() or not self.mail.get():
            messagebox.showerror("Champs manquants", "Vous devez remplir tous les champs obligatoires (*).")

        # on vérifie qu'il n'y a aucun caractère spécial dans le pseudonyme
        elif len(re.findall('[A-Za-z0-9_-]', self.pseudo.get())) != len(self.pseudo.get()):
            error.append('')
            messagebox.showwarning("Pseudonyme invalide", "Votre pseudonyme contient des caractères spéciaux.")

        # on vérifie que la date de naissance est passée
        elif date >= today:
            error.append('')
            messagebox.showwarning("Date de naissance invalide", "Veuillez entrer une date passée.")
       
        # on vérifie que le mot de passe est assez long pour être fiable
        elif len(self.password.get()) < 6:
            error.append('')
            messagebox.showwarning("Mot de passe peu fiable", "Le mot de passe doit être d\'au moins 6 caractères.")

        # on vérifie que les deux mots de passe entrés sont identiques
        elif self.password_repeat.get() != self.password.get():
            error.append('')
            messagebox.showwarning("Faute de frappe ?", "Les deux mots de passe ne sont pas identiques.")
            self.password.delete("0", "end")
            self.password_repeat.delete("0", "end")

        # s'il y a des erreurs, on efface les entrées du mot de passe
        elif error:
            self.password.delete(0, END)
            self.password_repeat.delete(0, END)

        # sinon, on ajoute le nouveau compte à la base de données
        else:
            entrer_compte(self.mail.get(), self.password.get(), self.pseudo.get(), str(self.dateN.get_date()), self.valeurSexe.get())
            self.gestionnaire.user.insertion(self.mail.get(), self.password.get(), self.pseudo.get(), 0)
            print(self.gestionnaire.user.mail)
            messagebox.showinfo("Inscription réussie", "Vous pouvez vous connecter.")
            self.gestionnaire.on_login()
            self.event_generate('<<SIGNUP_SUCCESS>>')


# page d'erreur répétée de connexion
class Erreur(Frame):
    def __init__(self, canevas):
        super().__init__()
        self.canevas = canevas

        # image de fond
        self.bg_frame = Canvas(self.canevas, width=largeur, height=hauteur, highlightthickness=0)
        self.bg_app = ImageTk.PhotoImage(Image.open('images/cc.png'))
        self.bg_frame.create_image(0, 0, image=self.bg_app, anchor='nw')

        # conteneur des informations
        self.message = Label(self.canevas, bg='white', fg='darkred', padx=5, pady=5,
                             text="Vous avez épuisé votre nombre d'essais.\nFermez l'application pour réessayer.")

    def show(self):
        self.bg_frame.place(x=0, y=0)
        self.message.place(x=cx, y=cy/2)

    def hide(self):
        self.bg_frame.place_forget()
        self.canevas.place_forget()
