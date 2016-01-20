# -*- coding: utf-8 -*-
##########################
# Création d'un parser d'URL destiné à extraire les objets web analytics présents sur une page #
# ---------------------- #
# Auteur : David SMILOVITZ #
# Crée le : 18/01/2016 #
##########################

import os, requests, tkinter.filedialog, tkinter.messagebox
from bs4 import BeautifulSoup
from sys import platform as _platform
from selenium import webdriver
from urllib.parse import urlsplit
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from tkinter import *

class MainApplication(Frame):
    #  Peut être remplacé sur les 2 lignes suivantes de cette façon avec un appel avec argument
    # def __init__(self, parent, *args, **kwargs):
    #     Frame.__init__(self, parent, *args, **kwargs)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        parent.title("Scrapeur d'urls")
        parent.geometry('800x800+800+200')
        parent['bg']='grey69'

        result =[]
        list_title = []
        list_objet = []

        def identification_os():
            if _platform == "linux" or _platform == "linux2":
                # linux
                # print("linux")
                return str("\n")
            elif _platform == "darwin":
                # OS X
                return str("\n")
            elif _platform == "win32":
                # Windows...
                # print("windows")
                return "\r\n"
            else:
                print("Votre systeme d'exploitation n'a pas été reconnu")
                return "unknown"

        identification_os()

        def ecrire_resultat_objet(type_de_fichier, nom_fichier, nom_objet, url, type_code):
            chemin_repertoire = repertoire
            #J'ouvre le fichier en mode a pour ajouter les éléments et ne pas les écraser
            with open(chemin_repertoire + "/"+ type_de_fichier + nom_fichier +'.txt', "a") as mon_fichier:
                mon_fichier.write(str(nom_objet).strip('['']') + ',' + str(url).strip('['']') + ',' + type_code)

        # Bloc sélection d'un répertoire de dépot des fichiers
        selection_depot = Frame(parent, width=30, height=30, padx=30, pady=30, bd=1,relief=RAISED)
        selection_depot.pack(side=TOP,fill=NONE)
        Label(selection_depot, text="Veuillez sélectionner le répertoire dans lequel les fichiers vont se déposer").pack()

        def choixrep():
            os.getcwd()
            global repertoire
            repertoire = tkinter.filedialog.askdirectory(title='Choisissez un répertoire pour votre scraping')
            if len(repertoire) > 0:
                l = LabelFrame(selection_depot, text="Informations sur le répertoire utilisé par le programme")
                l.pack(fill="both", expand="yes")
                Label(l, text="Vos fichiers vont se déposer dans le répertoire suivant : \n" +repertoire).pack(fill="both", expand="yes")

        Button(selection_depot, text='Choisir répertoire', command=choixrep).pack()
        # Fin du block de sélection répertoire 

        def ecrire_sitemap_ds_csv(type_de_fichier, nom_fichier, nom_objet):
            chemin_repertoire = repertoire
            with open(chemin_repertoire + "/" + type_de_fichier + nom_fichier +'.txt', "a") as mon_fichier:
                for line in nom_objet:
                    mon_fichier.write(line+'\n')

        def extraire_sitemap(url):
            #je retraite l'url pour generer un nom_de_fichier
            #newUrl = re.sub(r'^(https?:\/\/)|(http?:\/\/)|((/)|(/sitemap.xml)|(sitemap.xml))', '', url)
            base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
            newbase_url = re.sub(r'^(https?:\/\/)|(http?:\/\/)|((/)|(/sitemap.xml)|(sitemap.xml))', '', base_url)
            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data, "lxml")
            #J'encapsule chaque url dans un élément liste de python. 
            #Cela permet d'y accéder ensuite via un index.
            for url in soup.findAll("loc"):
                result.append(url.text)
            ecrire_sitemap_ds_csv("Liste_url_de_", newbase_url, result)
            Label(wd_Sitemap, text="Le parsing est terminé et les urls sont à disposition dans le répertoire").pack()      
            
        def recupere_url():
            url = entree.get()
            extraire_sitemap(url)

        # Bloc renseignement Sitemap
        # --------------------------------------------------------------------------
        wd_Sitemap = Frame(parent, width=30, height=30, padx=30, pady=30, bd=1, relief=RAISED)
        wd_Sitemap.pack(side=TOP, fill=NONE)
        Label(wd_Sitemap, text="Veuillez coller l'url de la sitemap dans le champs ci-dessous").pack()
        url_sitemap = StringVar() 
        entree = Entry(wd_Sitemap, textvariable=url_sitemap, width=30)
        entree.pack()
        Button(wd_Sitemap, text='Parser le Xml', command=recupere_url).pack()

        # Bloc de sélection d'un fichier pour y parcourir les urls
        selection_fichier = Frame(parent, width=30, height=30, padx=30, pady=30, bd=1, relief=RAISED)
        selection_fichier.pack(side=TOP,fill=NONE)
        Label(selection_fichier, text="Veuillez sélectionner le fichier dont vous souhaitez que les urls soient parsées").pack()

        def openF():
            rep = os.getcwd()                                    
            global fname 
            fname = tkinter.filedialog.askopenfilename(title ="Ouvrir le fichier : " ,\
            initialdir =rep, filetypes = [("All", "*"),("Fichiers Image",\
                   "*.jpeg;*.gig;*.jpg;*.png")])
            if len(fname) > 0:
                l = LabelFrame(selection_fichier, text="Informations sur le chemin du fichier parsé")
                l.pack(fill="both", expand="yes")
                Label(l, text="Le fichier utilisé sera le suivant : \n" +fname).pack(fill="both", expand="yes")
                return fname

        # Bloc de selection de l'element extrait
        def selected():
            return int(c_a_c.get())

        def script_principal(fname):
            try:
                repertoire
                driver = webdriver.Firefox()
                with open(fname, 'r') as f:
                        try:
                            j = 0
                            for row in f.readlines(): 
                                # retraitement de la liste python pour parser chaque url
                                row = row.replace("'","")
                                row = row.replace(",","")
                                if j < 100:
                                    driver.get(row)
                                    if selected() == 1:
                                        try:
                                            driver.execute_script("return ga(function(tracker){customDim=tracker.get('trackingId');return customDim;});")
                                            objetWa = driver.execute_script("return customDim;")  
                                            objetWb = "universal analytics"                                            
                                        except Exception:
                                            try :
                                                driver.execute_script("return ga(function(){tracker = ga.getByName('newTracker1'); customDim=tracker.get('trackingId');});")
                                                objetWa = driver.execute_script("return customDim;")
                                                objetWb = "universal analytics avec tracker nommé"
                                            except Exception:
                                                objetWa = driver.execute_script("return pageTracker = _gat._getTrackerByName(); customDim = pageTracker._getAccount();")
                                                objetWb = "ga asynchrone"                                              
                                    elif selected()== 2:
                                        objetWa = driver.execute_script("return dataLayer;")
                                    else:
                                        print("l'objet retourné n'a pas été reconnu")
                                       
                                    list_objet.append(objetWa)
                                    ecrire_resultat_objet("extraction_de_", "GA", objetWa, row, objetWb)
                                    # page_title = driver.find_element_by_xpath('//h1').text
                                    j +=1
                                    continue
                                else:
                                    break

                        finally:
                            driver.close()
            except NameError:
                Label(parent, text="Veuillez sélectionner un répertoire de destination des fichiers", bg='red', fg='white').pack(fill="both", expand="yes") 
                def msg_error():
                    messagebox.showinfo("Attention", "Veuillez sélectionner un répertoire en haut de l'interface \n \
                        dans lequel vont se déposer les fichiers générés")
                B1 = Button(parent, text="Repertoire inexistant", command=msg_error).pack()
         
        def lancer_script():
            script_principal(fname)

        Button(selection_fichier, text='Choisir fichier', command=openF).pack()

        wd_checkbox = Frame(parent, width=30, height=30, padx=30, pady=30, bd=1, relief=RAISED)
        wd_checkbox.pack(side=TOP,fill=NONE)
        Label(wd_checkbox, text="Veuillez Sélectionner l'objet que vous souhaitez récupérer").pack()
        c_a_c = StringVar() 
        bouton1 = Radiobutton(wd_checkbox, text="GA", variable=c_a_c, value=int(1), command=selected).pack()
        bouton2 = Radiobutton(wd_checkbox, text="GTM", variable=c_a_c, value=int(2), command=selected).pack()

        Button(parent, text='Lancer le script', command=lancer_script).pack()
        bouton=Button(parent, text="Fermer", command=parent.quit)
        bouton.pack(side=TOP,fill=NONE)

if __name__ == "__main__":
    root = Tk()
    MainApplication(root).pack(side=TOP, fill=NONE, expand=False)
    root.mainloop()