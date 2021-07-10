#coding utf8

#import des librairies nécessaires
from lxml import etree
from xml.etree import ElementTree as et
import json,re,os,itertools
#import des fonctions
from functions_alignment_texts_3 import *

"""
ce script permet de produire, pour troist témoins d'un même texte, des documents xml avec des marques de paragraphes au niveau des passages qui correspondent, sur le texte global
ce script produit des documents, json, txt et xml qu'il enregistre automatiquement dans un nouveau dossier
l'exécution du script peut prendre un peu de temps (notamment à cause des xsl)
les documents définitifs avec des paragraphes identiques dans les trois textes, au niveau des endroits qui matchent sont les versions "correct"

"""

#ci-dessous : marche pour trois textes
#part d'un texte et comparaison avec les deux autres
# TO DO : créer une fonction pour prendre nombre x de textes
# peut-on améliorer ? Ici les résultats sont assez mauvais (peu de <p> produits)

#j'applique la fonction pour transformer mes textes en json/dictionnaires (parse + id)
OA = XMLtoJson(etree.parse("textes/OA.xml"),"OA")
OB = XMLtoJson(etree.parse("textes/OB.xml"),"OB")
OM = XMLtoJson(etree.parse("textes/OM.xml"),"OM")


#définition d'une classe qui fait appel à la classe recupInfo
class text:
    def __init__(self,iden,doc):
        self.doc = doc
        self.iden = iden
    def dico(self):
        return recupInfo(self.doc).elem()
    def element(self):
        return recupInfo(self.doc).token()

# les trois textes sont des objets de la classe
t2 = text("OB",OB)
t1 = text("OA",OA)
t3 = text("OM", OM)

#fonction qui applique text-matcher
def TheMatch(texte1,texte2):
    ta = matcher.Text(texte1.element(), texte1.iden)
    tb = matcher.Text(texte2.element(), texte2.iden)
    m = matcher.Matcher(ta, tb, ngramSize=3).match()
    return(m)

#on applique la fonction 
m1 = TheMatch(t1,t2)
m3 = TheMatch(t1,t3)
#m2 = TheMatch(t2,t3)

# je récupère pour chacun de mes textes la liste des positions
pos1 = m1[1]
pos2 = m1[2]
pos1bis = m3[1]
pos3 = m3[2]
    
#l'idée : récupérer à partir du texte en commun les éléments qui matchent en 2 et 3 : comparer les id de Ao qui apparaissent dans m1 et m3 : seuls ceux qui apparaissent dans les 2 sont conservés : donc après application de la fonction recupid
l1 = recupid(t1.iden,pos1,t1.dico())
l1bis = recupid(t1.iden,pos1bis,t1.dico())
l2 = recupid(t2.iden,pos2,t2.dico())
l3 = recupid(t3.iden,pos3,t3.dico())

#on vérifie 
print(l1)
print(l1bis)
print(l2)
print(l3)

#création de listes vides
val = []
val2 = []
val3 = []
# on récupère les valeurs pour chacun de nos dicos
listeVal = l1["valeurs"]
listeVal1bis = l1bis["valeurs"]
listeVal2 = l2["valeurs"]
listeVal3 = l3["valeurs"]

#boucle qui itère sur les listes
for i in range (len(listeVal)) :
    valTok = listeVal[i]
#si l'id dans la liste issue du premier match se trouve dans la liste du même texte du premier match
    if valTok in listeVal1bis:
        #on obtient la position de l'id qui correspond dans la deuxième liste du premier texte
        rang = listeVal1bis.index(valTok)
        #on obtient la valeur de l'id qui correspond à la position pour le troisième texte
        valTok3 = listeVal3[rang]
        #on récupère aussi la valeur de l'id pour le deuxième texte grâce à la position de valTok donc de la place de l'id dans 1ere liste 1er texte
        valTok2 = listeVal2[i]
        #on remplit nos listes des valeurs
        val.append(valTok)
        val2.append(valTok2)
        val3.append(valTok3)

#on vérifie la liste
print(val)
print(val2)
print(val3)
        
#fonction qui produit l'XML
xml1 = prodXML(t1.dico(),val,t1.iden)
xml2 = prodXML(t2.dico(),val2,t2.iden)
xml3 = prodXML(t3.dico(),val3,t3.iden)





