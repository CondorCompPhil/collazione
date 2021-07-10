#coding utf8

#import des librairies nécessaires
from lxml import etree
from xml.etree import ElementTree as et
import json,re,os,itertools
#import des fonctions
from functions_alignment_text import *

"""
ce script permet de produire, pour deux témoins d'un même texte, des documents xml avec des marques de paragraphes au niveau des passages qui correspondent, sur le texte global
ce script produit des documents, json, txt et xml qu'il enregistre automatiquement dans un nouveau dossier
l'exécution du script peut prendre un peu de temps (notamment à cause des xsl)
les documents définitifs avec des paragraphes identiques dans les deux textes, au niveau des endroits qui matchent sont les versions "correct"
"""

#j'applique la fonction pour transformer mes textes en json/dictionnaires (parse + id)
Ao = XMLtoJson(etree.parse("Ao.xml"),"Ao")
Ez = XMLtoJson(etree.parse("Ez.xml"),"Ez") 

#j'applique ma fonction pour produire des paragraphes là où les textes matchent
boucleMatch(Ao,Ez)

#exemple pour simplement obtenir la liste des tokens du dictionnaires et le match
"""
class text:
    def __init__(self,iden,doc):
        self.doc = doc
        self.iden = iden
    def dico(self):
        return recupInfo(self.doc).elem()
    def element(self):
        return recupInfo(self.doc).token()


t1 = text("Ao",Ao)
t2 = text("Ez",Ez)

print(t1.dico())

ta = matcher.Text(t1.element(), t1.iden)
tb = matcher.Text(t2.element(), t2.iden)
m = matcher.Matcher(ta, tb, ngramSize=4).match()
print(m)
"""






