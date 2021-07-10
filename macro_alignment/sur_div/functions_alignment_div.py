#coding utf8

from text_matcher import matcher
from lxml import etree
import json,re,os,itertools

#création du dossier dans lequel les fichiers créés vont s'enregistrer
try:
    os.mkdir("fichiers_prod_auto_align_div")
except OSError:
    pass

#fonction qui permet de créer pour chaque div un dictionnaires avec des valeurs
def XMLtoJson(iden,corresp,xmlInput):
    #création d'un dictionnaire
    div = {}
    #première valeur
    div['id'] = iden
    #enregistrement d'une deuxième valeur
    div['corresp'] = corresp
    print(div)    
    #XSL : crée un dico pour chaque token
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei xs"
    version="1.0">
    
    <xsl:output method="text"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
        <xsl:template match="tei:teiHeader"/>
        
        <xsl:template match="tei:div">
        <xsl:apply-templates/>
        </xsl:template>
        
    <xsl:template match="tei:head"/>
    
    <xsl:template match="tei:w">
        <xsl:text>{"text": "</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>", "id": "</xsl:text>
        <xsl:value-of select="@xml:id"/>
        <xsl:text>", "lemme": "</xsl:text>
        <!--pour la valeur des lemmes, on enlève les + qui gênent sinon le calcul du nb de caractères à cause du tokeniser de text_matcher-->
        <xsl:choose>
            <xsl:when test="contains(@lemma, '+')">
                <xsl:value-of select="concat(substring-before(@lemma, '+'), substring-after(@lemma, '+'))"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@lemma"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>"}</xsl:text>
        <xsl:if test="following::tei:w">
            <xsl:text>, </xsl:text>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
    ''')
    #on parse l'xml
    monXSL = etree.XSLT(monXSL)    
    #valeur de i avec résultat de l'xsl sous forme de liste
    i = json.loads( '[' +str(monXSL(xmlInput)) +']')
    #deuxième valeur du dico div correspond à la liste déf ci-dessus
    div["tokens"]=i
    return div
    #on obtient le dico div, contenant les id et les tokens avec leurs valeurs
    #chaque dico est ensuite ajouté à une liste générale contenant toutes les valeurs des div de chaque texte

#classe qui permet de transformer les document XML en input : besoin d'un identifiant et du document XML parsé
class XMLtoJsonParDiv:
    def __init__(self,idGnl,XML):
        self.XML = XML
        self.idGnl = idGnl
        #permet de produire le dictionnaire de base dans lesquelles vont être nos données
    def prodDiv(self):
        #création du dictionnaire
        witness = {}
        #définition de l'id
        witness['idGnl'] = self.idGnl
        #liste de div
        witness['div']=[]
        liste_par = witness['div']
        #on obtient la racine du document
        doc = self.XML.getroot()
        #création d'une boucle pour pouvoir itérer sur chacun des éléments div, avec espace de nom TEI
        for par in doc.iter("{http://www.tei-c.org/ns/1.0}div"):
            iden = par.get("{http://www.w3.org/XML/1998/namespace}id")
            corresp = par.get("corresp")
            print(iden)
            print(type(par))
            print(par)
            #on applique la fonctionXMLtoJSON définie ci-après à partir des éléments obtenus depuis l'itération sur le document XML
            div = XMLtoJson(iden,corresp,par)
            #on ajoute le résultat (un dictionnaire de valeurs de tokens à cette div)
            liste_par.append(div)
        #le résultat est le dictionnaire général contenant toutes les infos
        with open("fichiers_prod_auto_align_div/"+self.idGnl+"_dico.json", "w") as text_file:
            text_file.write(str(witness))
        return witness

#définition d'une classe qui récupère les infos nécessaires à l'alignement
class recupInfo:
    def __init__(self,witness):
        self.witness = witness
    #permet d'obtenir le texte
    def token(self):
        #variable qui correspond à la liste de tokens
        token_witness = self.witness['tokens']
        #list vide créée dans laquelle on va mettre les lemmes
        liste_de_tok_wit = []
        pos= 0
        #boucle pour itérer sur chaque token
        for i in range (0, len(token_witness)) :
            #variable pour récupérer dans cette boucle la valeur complète de chaque élément
            elem = token_witness[i]
            #variable pour conserver les lemmes dans une liste
            l = elem['lemme']
            # on remplit la liste de lemmes au fur et à mesure
            liste_de_tok_wit.append(l)
        #on transforme la liste en chaîne de caractères
        text = " ".join(liste_de_tok_wit)
        #valeur finale : le texte
        return text
    #permet de modifier la liste des éléments, en rajoutant une numérotation et pour chaque élément la position de chacun des premiers caractères
    def elem(self):
        token_witness = self.witness['tokens']
        #définition de pos qui correspond à la valeur du premier caractère de chaque mot
        pos = 0
        #on boucle sur chaque élément
        for i in range (0, len(token_witness)) :
            #on rajoute une position
            token_witness[i]["n"]=i
            elem = token_witness[i]
            l = elem['lemme']
            #s'il s'agit du premier mot
            if elem["n"]==0:
                #on crée une nouvelle clé, qui a comme valeur 0
                elem["debut_mot"] = pos
                # on obtient la longueur de la chaîne de caractères à la fin pour avoir une nouvelle valeur de pos
                pos = len(l)
            #pour tous les autre tokens
            else:
                # on modifie la valeur de pos = dernière longueur obtenue + 1 (espace) qui permet d'avoir le premier caractère de chaque mot 
                pos = pos +1
                #on crée la clé avec la nouvelle valeur
                elem["debut_mot"] = pos
                #on ajoute à pos la longueur du token que l'on vient de traiter
                pos = pos + len(l)
        #on obtient la liste des éléments modifiés, avec deux nouvelles valeurs
        return token_witness

#nouvelle fonction pour récupérer la liste des id des mots qui commencent des passages qui matchent, dans un dico avec valeur de nos deux textes
def recupid(iden,text,json):
    #dictionnaire vide créé
    val = {}
    #première clé : l'identifiant du texte
    val["id"] = iden
    #création d'une liste vide qui doit récupérer les valeurs des id corr à chaque position
    liste_des_val = []
    #boucle sur chacun des éléments (len(text) = nombre de matchs)
    for i in range (0, len(text)) :  
    # je récupère la position pour avoir le début du mot : correspond au premier caractère du premier mot du match 
        lieuText = text[i][0]       
    #je crée une boucle sur les éléments dans la liste des éléments modifiés
        for elem in json:
            #si la valeur dans la liste des positions obtenues dans text_matcher correspond à la valeur debut_mot d'un de mes éléments
            if lieuText ==  elem["debut_mot"]:
                #j'ajoute l'id de cet élément à ma liste de valeurs des id
                liste_des_val.append(elem["id"])
    # je crée une nouvelle clé de valeurs à mon dictionnaire, qui donne les id de chacun des mots
    val["valeurs"] = liste_des_val
    # je récupère mon dico
    return val

#fonction qui réalise l'alignement : utilise les json (dictionnaires) produit pour récupérer tous les éléments nécessaires à l'alignement; aligne et écrit l'XML  
def boucleMatch(texte1,texte2):
    #les actions se réalisent à chaque fois pour les deux textes
    
    #on récupère la liste des div
    liste1 = texte1["div"]
    liste2 = texte2["div"]
    #on récupère l'id du texte
    idText1 = texte1["idGnl"]
    idText2 = texte2["idGnl"]

#création de deux listes vides
    v1 = []
    v2 = []
# boucle sur les div
    for i1 in liste1:
        print(i1)
        #on récupère les id et correspondances des div du texte1
        c1 = i1["id"]
        corresp1 = i1["corresp"]
        #utilisationn de la méthode recupInfo().token pour obtenir le texte du texte1
        textToMatch1 = recupInfo(i1).token()
        #utilisation de la méthode recupInfo().elem pour obtenir les éléments modifiés du texte1
        elem1 = recupInfo(i1).elem()
        #on itère sur la deuxième liste
        for i2 in liste2:
            #s'il y a correspondance entre les div
            if i2["corresp"]==c1:
                #utilisationn de la méthode recupInfo().token pour obtenir le texte du texte2
                textToMatch2 = recupInfo(i2).token()
                #utilisation de la méthode recupInfo().elem pour obtenir les éléments modifiés du texte2
                elem2 = recupInfo(i2).elem()
                #on récupère les id et correspondances des div du texte2
                c2 = i2["id"]
                corresp2 = c1
    
        #application de text_matcher sur les textes obtenus grâces à ci-dessuss
        ta = matcher.Text(textToMatch1, c1)
        tb = matcher.Text(textToMatch2, c2)
        #réalisation du match de text_matcher (on augmente valeur des ngram pour avoir un match plus sûr)
        m = matcher.Matcher(ta, tb, ngramSize=4).match()
        #m renvoie une liste avec les positions des positions de caractères qui commencent et terminent les matchs

        # je récupère pour chacun de mes textes la liste des positions
        pos1 = m[1]
        pos2 = m[2]

        #pour chacun de mes textes : j'applique ma fonction recupid, avec un nom, la liste des positions, la liste des éléments, qui permet de récupérer la liste des id qui matchent
        l1 = recupid(c1,pos1,elem1)
        l2 = recupid(c2,pos2,elem2)

        #on checke la longueur pour vérifier que tout va bien (doivent être égale, et égale au nombre de matchs trouvés par text_matcher)
        print(len(l1["valeurs"]))
        print(len(l2["valeurs"]))

        # je transforme en chaîne de car les listes pour pouvoir les écrire
        m_ecr = str(m)
        l1_ecr = str(l1)
        l2_ecr = str(l2)

        #j'écris mes résultats dans un fichier de log, pour chaque match (chaque div)
        with open("fichiers_prod_auto_align_div/log_match"+c1+"_"+c2+".txt", "w") as text_file:
            text_file.write("Voici les identifiants des mots qui matchent entre les deux textes :")
            text_file.write(l1_ecr)
            text_file.write(l2_ecr)
            text_file.write("Ce qui suit est le log de text_matcher ")
            text_file.write(m_ecr)
        
        #j'applique ma fonction de production d'XML à partir de la liste de tokens, de la liste des identifiants qui matchent, et des autres id
        xml1 = prodXML(elem1,l1,idText1,c1,corresp1)
        xml2 = prodXML(elem2,l2,idText2,c2,corresp2)
        
        # je remplis mes listes pour qu'elles contiennent toutes les div
        v1.append(xml1)
        v2.append(xml2)
        #fin de la boucle
        
    # je joins mes listes et mets un élément racine    
    val1 = "<text>" + ''.join(v1) + "</text>"
    val2 = "<text>" + ''.join(v2) + "</text>"

    #on écrit le résultat (une simple chaîne de caractères) dans notre document XML
    with open("fichiers_prod_auto_align_div/export_par_div_"+idText1+".xml", "w") as text_file:
        text_file.write(val1)

    with open("fichiers_prod_auto_align_div/export_par_div_"+idText2+".xml", "w") as text_file:
        text_file.write(val2)
    
    # on parse les document qu'on vient de créer (plus simple pour la manipulation des données XML)
    #on applique la fonction exportDef qui permet de mettre les paragraphes au bon niveau
    Def1 = exportDef(etree.parse("fichiers_prod_auto_align_div/export_par_div_"+idText1+".xml"))
    Def2 = exportDef(etree.parse("fichiers_prod_auto_align_div/export_par_div_"+idText2+".xml"))
    
    #on écrit le résultat dans d'autres fichiers
    fichier = open("fichiers_prod_auto_align_div/export"+idText1+"Def.xml", "wb")  
    fichier.write(Def1)
    fichier = open("fichiers_prod_auto_align_div/export"+idText2+"Def.xml", "wb")  
    fichier.write(Def2)

    
#définiton de la fonction qui va construire un premier document XML, à partir du dictionnaire des tokens et de la liste des identifiants qui matchent
def prodXML(val,listev,cle,clediv,corresp):
    #variable qui récupère les valeurs des identifiants qui marchent
    liste_des_valeurs = listev["valeurs"]
    #création d'un premier élément racine, avec ses attributs, qui corr à son id et à sa correspondance
    div = etree.Element("div")
    div.set("{http://www.w3.org/XML/1998/namespace}id", clediv)
    div.set("corresp", corresp)
    # boucle qui va itérer sur chacun des élément du dictionnaires de token
    for i in val:
        #on récupère les valeurs de ce dico
        l = i["lemme"]
        iden = i["id"]
        text = i["text"]
        pos = i["n"]
        #si l'identifiant se trouve dans la liste des identifiants qui marchent
        if iden in liste_des_valeurs:
            #je crée un identifiant de paragraphe +1 (car besoin ensuite de créer un avec valeur 0)
            piden = liste_des_valeurs.index(iden)+1
            #le type int fonctionne pas, donc str
            piden = str(piden)
            #je crée l'élément p
            p = etree.SubElement(div, "p")
            #je lui crée un attribut avec pour valeur sa position
            p.set("n", piden)
        # création de l'élément w avec ses attributs à partir de la liste de tokens  
        e = etree.SubElement(div, "w")
        e.set("{http://www.w3.org/XML/1998/namespace}id", iden)
        e.set("lemma", l)
        e.text = text
    #création de l'XML intermédiaire
    doc = etree.tostring(div, encoding="unicode")
    #on l'enregistre dans un fichier; cette étape nous permet d'éviter le problème d'encodage de l'xml (bytes, strings...)
    fichier = open("fichiers_prod_auto_align_div/export"+clediv+".xml", "w")  
    fichier.write(doc)
    return doc

def exportDef(text):
 #définition de l'xsl pour bien placer les paragraphes
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xsl xs" version="1.0"
   >
    <!-- génération de la sortie -->
    <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>
    
    <!--racine-->
<xsl:template match="/">
    <xsl:apply-templates/>
</xsl:template>

<!--création d'un élément text-->
<xsl:template match="text">
    <xsl:element name="text">
        <xsl:apply-templates select="div"/>
    </xsl:element>
</xsl:template>

<xsl:template match="div">
    <xsl:element name="div">
        <xsl:copy-of select="@*"/>
        <xsl:apply-templates select="p|w"/>
    </xsl:element>
</xsl:template>

<!-- on reprend la structure en paragraphe -->
<xsl:template match="p">
    <xsl:variable name="numP">
        <xsl:value-of select="@n"/>
    </xsl:variable>
    <xsl:variable name="numDiv">
        <xsl:for-each select="parent::div">
            <xsl:value-of select="@xml:id"/>
        </xsl:for-each>
    </xsl:variable>
    <xsl:element name="p">
        <xsl:attribute name="n">
            <xsl:value-of select="@n"/>
        </xsl:attribute>
        <!--on met à l'intérieur de chaque paragraphe les mots qui suivent-->
        <xsl:for-each select="following::w[preceding::p[1][@n=$numP] and ancestor::div[@xml:id=$numDiv]]">
            <xsl:element name="w">
                <xsl:copy-of select="@*"/>
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:for-each>
    </xsl:element>
</xsl:template>

<!--pour les mots avant le premier paragraphe obtenu par text_matcher : on crée un paragraphe-->
<xsl:template match="w[not(preceding::p)]">
    <xsl:if test="position()=1">
        <xsl:element name="p">
            <xsl:attribute name="n">
                <xsl:value-of select="0"/>
            </xsl:attribute>
            <xsl:element name="w">
                <xsl:copy-of select="@*"/>
                <xsl:apply-templates/>
            </xsl:element>
            <xsl:for-each select="following::w[not(preceding::p)]">
                <xsl:element name="w">
                    <xsl:copy-of select="@*"/>
                    <xsl:value-of select="."/>
                </xsl:element>
            </xsl:for-each>
        </xsl:element>
    </xsl:if>
</xsl:template>
    
    <!--comme le reste des mots sont compris ci-dessus, on n'applique pas de règle-->
    <xsl:template match="w[preceding::p]"/>

</xsl:stylesheet>

    ''')
    #on met l'xsl dans etree
    monXSL = etree.XSLT(monXSL)
    #on applique l'xsl à notre document xml ci-dessus créé
    result_XML = monXSL(text)
    return result_XML

