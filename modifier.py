import re
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from donnees import *
from client import *


# page de Modifier
class Modifier(Frame):
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
                           relief=SUNKEN, text='Modification des informations', fg='darkblue')
        self.pseudo = Entry(self.content)
        self.mail = Entry(self.content)
        self.alert.place(x=150, y=10, width=400)
        # self.mail.insert(0,"user.mail")

        # boutons pour le choix du sexe
        self.valeurSexe = StringVar()
        self.M = Radiobutton(self.content, text="MASCULIN", value="Homme",
                             variable=self.valeurSexe, indicatoron=False, font=("Arial", 10))
        self.F = Radiobutton(self.content, text="FEMININ", value="Femme",
                             variable=self.valeurSexe, indicatoron=False, font=("Arial", 10))

        # calendrier dynamique pour la date de naissance
        self.dateN = DateEntry(self.content)

        # entrées du mot de passe
        self.password = Entry(self.content, show='*')

        # boutons du bas
        self.submit = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface, text="Modifier",
                             command=self.on_update)
        self.back = Button(self.content, fg=user.couleur_texte, bg=user.couleur_interface, command=self.retourner,
                           text="Retour")

    def show(self):
        cx = self.canevas.winfo_width() / 2
        cy = self.canevas.winfo_height() / 2
        self.content.place(x=cx - 350, y=cy - 200)
        Label(self.content, text='Pseudonyme* :', font="{Courier New} 10 normal").place(x=50, y=80)
        self.pseudo.place(x=200, y=80)
        Label(self.content, text='Mail* :', font="{Courier New} 10 normal").place(x=50, y=130)
        self.mail.place(x=200, y=130)
        self.mail.bind(user.mail)
        Label(self.content, text='Genre :', font="{Courier New} 10 normal").place(x=50, y=180)
        self.M.place(x=160, y=180)
        self.F.place(x=260, y=180, width=80)
        Label(self.content, text='Naissance :', font="{Courier New} 10 normal").place(x=50, y=230)
        self.dateN.place(x=200, y=230, width=124)
        self.submit.grid(ipadx=10, ipady=2)
        self.submit.place(x=150, y=370, width=150)
        self.back.grid(ipadx=10, ipady=2)
        self.back.place(x=400, y=370, width=150)
        Label(self.content, text='Entrez votre mot de passe actuel pour valider :',
              font="{Courier New} 10 normal").place(x=50, y=280)
        Label(self.content, text='Mot de passe* :', font="{Courier New} 10 normal").place(x=50, y=320)
        self.password.place(x=200, y=320)
        self.mail.insert(0, self.gestionnaire.user.mail)
        self.pseudo.insert(0, self.gestionnaire.user.pseudo)

    def hide(self):
        self.content.place_forget()

    def retourner(self):
        self.hide()
        self.gestionnaire.membre.show()

    def on_update(self):
        """ Bouton d'inscription pressé, il faut vérifier les données """
        error = []  # Liste vide pour les erreurs
        date = self.dateN.get_date().isoformat()

        # on vérifie que tous les champs sont remplis
        if not self.pseudo.get() or not self.mail.get():
            messagebox.showerror("Champs manquants", "Vous devez remplir tous les champs obligatoires (*).")

        # on vérifie qu'il n'y a aucun caractère spécial dans le pseudonyme
        elif len(re.findall('[A-Za-z0-9_-]', self.pseudo.get())) != len(self.pseudo.get()):
            error.append('')
            messagebox.showwarning("Pseudonyme invalide", "Votre pseudonyme contient des caractères spéciaux.")

        # on vérifie que la date de naissance est passée
        elif date >= today:
            error.append('')
            messagebox.showwarning("Date de naissance invalide", "Veuillez entrer une date passée.")

        elif self.mail.get() != user.mail:
            error.append('')
            messagebox.showwarning("Mail inchangable", "Ne changer pas votre mail.")

        # on vérifie que le mot de passe est assez long pour être fiable
        elif self.password.get() != user.mdp:
            error.append('')
            messagebox.showwarning("mot de passe invalide", "Veuillez entrer le bon mot de passe")

        # s'il y a des erreurs, on efface les entrées du mot de passe
        elif error:
            self.password.delete(0, END)

        # sinon, on ajoute le nouveau compte à la base de données
        else:
            modifier_compte(self.pseudo.get(), str(self.dateN.get_date()), str(self.valeurSexe.get()), user.mail)
            self.gestionnaire.user.insertion(user.mail, self.password.get(), self.pseudo.get(), user.score)
            self.gestionnaire.membre.deconnection()
            self.gestionnaire.on_login()
            messagebox.showinfo("Mise à jour confirmée", "Vous avez modifié vos informations avec succès")
            self.event_generate('<<SIGNUP_SUCCESS>>')
