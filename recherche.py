from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from client import *
from donnees import *


# gestionnaire de la recherche
class GestionRecherche:
    def __init__(self, canevas, page):
        self.recherche = Recherche(canevas, self, page)
        self.preferences = Preferences(canevas, self)
        self.page = "recherche"
        
    def show(self):
        exec("self.%s.show()" % self.page)
    
    def change_to(self, page):
        self.hide()
        self.page = page
        self.show()
    
    def hide(self):
        exec("self.%s.hide()" % self.page)


# page de recherche de livres
class Recherche(Frame):
    def __init__(self, canevas, gestionnaire, page):
        super().__init__()
        self.canevas = canevas
        self.gestionnaire = gestionnaire
        self.biblio = Bibliotheque()
        self.page = page

        cx = self.canevas.winfo_width()/2
        cy = self.canevas.winfo_height()/2
        self.can_res = Canvas(canevas, width=cx + 160, height=cy*2 - 140, background=user.couleur_fond, scrollregion=(0, 0, cx + 160, cy*2 - 140))
        
        self.message = ""
        self.res = []
        self.bouton = []
        self.txt_filtre = "tout"
        self.txt_tri = "id ASC"
        self.min = 0

        # titre et barre de recherche
        self.titre = Label(canevas, font="{U.S. 101} 15 bold", borderwidth=6,
                           relief=SUNKEN, text='Recherche', fg='darkblue')
        self.entree = Entry(canevas,
                            background=user.couleur_interface, foreground=user.couleur_texte)
        self.valider = Button(canevas, text="Rechercher", command=self.rechercher,
                              background=user.couleur_interface, foreground=user.couleur_texte)

        # gestion des résultats
        self.filtre = Label(canevas, text="Rechercher par : tout", padx=5, pady=5,
                            background=user.couleur_interface, foreground=user.couleur_texte)
        self.tri = Label(canevas, text="Trier par : id ASC", padx=5, pady=5,
                         background=user.couleur_interface, foreground=user.couleur_texte)
        self.modif = Button(canevas, text="Modifier", command=self.modifier,
                            background=user.couleur_interface, foreground=user.couleur_texte)

    # affiche la page
    def show(self):
        self.can_res.update()
        cx = self.canevas.winfo_width()/2
        cy = self.canevas.winfo_height()/2
        self.titre.place(x=cx - 100, y=20, width=200)
        self.entree.place(x=cx - 100, y=80, width=200)
        self.valider.place(x=cx + 100, y=80)
        self.filtre.place(x=120, y=40)
        self.tri.place(x=120, y=80)
        self.modif.place(x=120, y=120)

        # liste de livres
        nombre = self.biblio.nombre
        if nombre > 0:
            height = cy*2 - 140
            if (nombre*40 + 60) > height:
                nombre = int((height - 20)/40)
                Button(self.can_res, text="▲", command=self.monter,
                       bg=user.couleur_interface, fg=user.couleur_texte).place(x=cx + 130, y=0, width=30, height=30)
                Button(self.can_res, text="▼", command=self.descendre,
                       bg=user.couleur_interface, fg=user.couleur_texte).place(x=cx + 130, y=height - 30, width=30, height=30)
            for i in range(self.min, self.min + nombre):
                self.res.append(Label(self.can_res, text=self.biblio.liste[i], padx=5, pady=5,
                                      background=user.couleur_interface, foreground=user.couleur_texte))
                self.res[i - self.min].place(x=80, y=20 + 40*(i - self.min))
                self.bouton.append(Button(self.can_res, text="Voir plus", command=self.voir_livre,
                                   background=user.couleur_interface, foreground=user.couleur_texte))
                self.bouton[i - self.min].place(x=20, y=20 + 40*(i - self.min))
            self.can_res.place(x=cx - 180, y=120, width=cx + 160, height=cy * 2 - 140)
        else:
            self.res.append(Label(self.can_res, text="Aucun livre trouvé", padx=5, pady=5,
                                  background=user.couleur_interface, foreground=user.couleur_texte))
            self.res[0].place(x=20, y=20)

    # descend dans l'affichage des livres
    def descendre(self):
        nombre = self.biblio.nombre
        cy = self.canevas.winfo_height()/2
        nb_livres = int((cy - 80)/20)
        if (self.min + int(nb_livres*1.5)) < nombre:
            self.min += int(nb_livres/2)
        else:
            self.min = nombre - nb_livres
        self.hide()
        self.show()

    # remonte dans l'affichage des livres
    def monter(self):
        cy = self.canevas.winfo_height() / 2
        nb_livres = int((cy - 80)/20)
        if (self.min - int(nb_livres/2)) >= 0:
            self.min -= int(nb_livres/2)
        else:
            self.min = 0
        self.hide()
        self.show()

    # cache la page
    def hide(self):
        self.titre.place_forget()
        self.entree.place_forget()
        self.valider.place_forget()
        self.filtre.place_forget()
        self.tri.place_forget()
        self.modif.place_forget()
        self.can_res.place_forget()
        self.clear()

    # vide les listes de résultast et de boutons
    def clear(self):
        try:
            for i in range(len(self.res)):
                self.res[i].place_forget()
                self.bouton[i].place_forget()
        except:
            pass
        self.res.clear()
        self.bouton.clear()

    # renvoi vers la page du livre choisi (bouton "voir plus")
    def voir_livre(self):
        y = self.can_res.winfo_pointery() - self.can_res.winfo_rooty()
        i = int((y-20)/40) + self.min
        self.page.reset(self.biblio.liste[i])
        self.hide()
        self.page.show()

    # met à jour les résultats de recherche selon les entrées utilisateur
    def rechercher(self):
        self.message = self.entree.get()
        filtri = self.gestionnaire.preferences.choix.get()
        print(filtri)

        # si rien n'est entré, on ressort tous les livres de la base de données
        if self.message == "" or (self.txt_filtre == "tout" and self.txt_tri == "id croissant"):
            temp = to_livres(tous_les_livres())
        else:
            if self.txt_filtre == "tout":
                # cherche tous les livres, triés, contenant le texte recherché quelque part
                supertramp = to_livres(livres_tri(self.txt_tri))
                temp = []
                for livre in supertramp:
                    if self.message.lower() in livre.__str__().lower():
                        temp.append(livre)
            else:
                # cherche les livres dont la propriété filtre contient message, triés
                temp = to_livres(livres_filtre(self.txt_filtre, self.message, self.txt_tri))

        # si aucun livre n'est trouvé, on recherche avec plus de souplesse
        if len(temp) == 0:
            print("Aucun livre trouvé, recherche élargie")
            supertramp = to_livres(tous_les_livres())
            temp = []
            for livre in supertramp:
                if self.message.lower() in livre.__str__().lower():
                    temp.append(livre)
            if len(temp) > 0:
                messagebox.showinfo("Recherche élargie", "Aucun livre trouvé avec le filtre actuel.")
            else:
                messagebox.showinfo("Aucun livre trouvé", "Recherchez par mot-clé pour plus de résultats.")
        
        self.biblio.set(temp)
        print(self.biblio.__str__())

        # mise à jour de l'interface avec les nouveaux résultats
        self.min = 0
        self.clear()
        self.show()

    # ouvre un menu de préférences de tri et filtre des résultats
    def modifier(self):
        self.hide()
        self.gestionnaire.change_to("preferences")


# page de choix de préférences de recherche
class Preferences(Frame):
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
                           relief=SUNKEN, text='Préférences', fg='darkblue')
        
        # boutons pour le choix du filtre
        self.choix = StringVar()
        self.titre = Radiobutton(self.content, text="titre", value="titre",
                                 variable=self.choix, indicatoron=False)
        self.auteur = Radiobutton(self.content, text="auteur", value="auteur",
                                  variable=self.choix, indicatoron=False)
        self.genre = Radiobutton(self.content, text="genre", value="genre",
                                 variable=self.choix, indicatoron=False)

        # boutons pour le choix du tri
        self.tri_titre = Radiobutton(self.content, text="titre", value="titre ASC",
                                     variable=self.choix, indicatoron=False)
        self.tri_auteur = Radiobutton(self.content, text="auteur", value="auteur ASC",
                                      variable=self.choix, indicatoron=False)
        self.tri_pages = Radiobutton(self.content, text="pages", value="pages ASC",
                                     variable=self.choix, indicatoron=False)
        
        # boutons du bas
        self.reset = Button(self.content, text="Réinitialiser", command=self.reseter,
                            background=user.couleur_interface, foreground=user.couleur_texte)
        self.valider = Button(self.content, text="Valider", command=self.valider,
                              background=user.couleur_interface, foreground=user.couleur_texte)
    
    def show(self):
        self.canevas.update()
        cx = self.canevas.winfo_width()/2
        cy = self.canevas.winfo_height()/2
        self.content.place(x=cx - 350, y=cy - 200)
        self.alert.place(x=150, y=10, width=400)
        Label(self.content, text="Rechercher par :").place(x=100, y=80)
        self.titre.place(x=100, y=110)
        self.auteur.place(x=100, y=140)
        self.genre.place(x=100, y=170)
        Label(self.content, text="Trier par :").place(x=250, y=80)
        self.tri_titre.place(x=250, y=110)
        self.tri_auteur.place(x=250, y=140)
        self.tri_pages.place(x=250, y=170)
        self.reset.place(x=150, y=370, width=150)
        self.valider.place(x=400, y=370, width=150)
    
    def hide(self):
        self.content.place_forget()
    
    def reseter(self):
        self.hide()
        self.gestionnaire.recherche.txt_filtre = "tout"
        self.gestionnaire.recherche.txt_tri = "id ASC"
        self.gestionnaire.recherche.filtre.configure(text="Rechercher par : tout")
        self.gestionnaire.recherche.tri.configure(text="trier par : id ASC")
        self.hide()
        self.gestionnaire.recherche.show()
    
    def valider(self):
        self.hide()
        choix = self.choix.get()
        if choix == "titre" or choix == "auteur" or choix == "genre":
            self.gestionnaire.recherche.txt_filtre = choix
            self.gestionnaire.recherche.filtre.configure(text="Rechercher par : " + choix)
        elif choix == "titre ASC" or choix == "auteur ASC" or choix == "pages ASC":
            self.gestionnaire.recherche.txt_tri = choix
            self.gestionnaire.recherche.tri.configure(text="Trier par : " + choix)
        self.gestionnaire.change_to("recherche")
