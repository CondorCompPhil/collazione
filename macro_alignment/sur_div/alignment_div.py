#coding utf8

from lxml import etree
import json,re,os,itertools


from functions_alignment_div_test_tei import *


"""
ce script permet de produire, pour deux témoins d'un même texte, des documents xml avec des marques de paragraphes au niveau des passages qui correspondent sur du texte déjà divisé en éléments div
ce script produit des documents, json, txt et xml qu'il enregistre automatiquement dans un nouveau dossier
l'exécution du script peut prendre un peu de temps (notamment à cause des xsl)
les documents définitifs avec des paragraphes identiques dans les deux textes, au niveau des endroits qui matchent sont les versions "Def"
"""

#on parse les documents
Ao_plein = etree.parse("Ao.xml")
Ez_plein = etree.parse("Ez.xml")

"""
test pour voir si ça fonctionne
root = Ao_plein.get(root)
for elem in root.findall(".//{http://www.tei-c.org/ns/1.0}div"):   
    print(elem)
    a = elem.get("n")
    print(a)
"""


#on applique la méhode prodDiv à nos variables obtenues ci-dessus, besoin d'un id aussi
Ao = XMLtoJsonParDiv("Ao", Ao_plein).prodDiv()
Ez = XMLtoJsonParDiv("Ez", Ez_plein).prodDiv()


#on applique la fonction boucleMatch qui procède à l'alignement
boucleMatch(Ao,Ez)


"""
#exemple pour simplement obtenir la liste de tokens et le dictionnaires des éléments modifiés

liste1 = Ao["div"]

for i1 in liste1:
    print(i1)
    #on récupère les id et correspondances des div du texte1
    c1 = i1["id"]
    corresp1 = i1["corresp"]
    #utilisationn de la méthode recupInfo().token pour obtenir le texte du texte1
    textToMatch1 = recupInfo(i1).token()
    #utilisation de la méthode recupInfo().elem pour obtenir les éléments modifiés du texte1
    elem1 = recupInfo(i1).elem()
    print(textToMatch1)
    print(elem1)
"""

"""
#exemple pour simplement réaliser l'alignement de text_matcher (boucle)

liste1 = Ao["div"]
liste2 = Ez["div"]

for i1 in liste1:
    #id
    c1 = i1["id"]
    #utilisationn de la méthode recupInfo().token pour obtenir le texte du texte1
    textToMatch1 = recupInfo(i1).token()
    for i2 in liste2:
        #s'il y a correspondance entre les div
        if i2["corresp"]==c1:
            #utilisationn de la méthode recupInfo().token pour obtenir le texte du texte2
            textToMatch2 = recupInfo(i2).token()
            #id 
            c2 = i2["id"]

    ta = matcher.Text(textToMatch1, c1)
    tb = matcher.Text(textToMatch2, c2)
    #réalisation du match de text_matcher (on augmente valeur des ngram pour avoir un match plus sûr)
    m = matcher.Matcher(ta, tb, ngramSize=4).match()

    print(m)
"""

