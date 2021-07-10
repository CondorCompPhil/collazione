#coding utf-8

from text_matcher import matcher
from lxml import etree
import json,re,os,itertools

try:
    os.mkdir("fichiers_prod_auto_align")
except OSError:
    pass

#obtain json/dico
def XMLtoJson(xmlInput,iden):
    #creation of a first dico
    witness = {}
    #first value
    witness['id'] = iden
    print(witness)
    #XSL : create a dico for every token
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei xs"
    version="1.0">
    
    <xsl:output method="text"/>
     <xsl:strip-space elements="*"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="tei:teiHeader"/>
        
        <!-- elements not kept-->
        <!--can be modify here depending on the present elements in the basic text-->
    <xsl:template match="tei:sic|tei:pc|tei:orig|tei:abbr|tei:corr[@source]|tei:corr[@type='editorial']|tei:note"/>
    
    
    <!-- choose of regularised and corrected versions-->
    <xsl:template match="tei:corr[not(@source) or not(@type)]|tei:reg|tei:expan|tei:ex">
        <xsl:choose>
            <xsl:when test="child::tei:choice">
                <xsl:apply-templates select="descendant::tei:corr | descendant::tei:reg"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>          
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="tei:hi|tei:l|tei:lg|tei:lb">
    <xsl:apply-templates/>
    </xsl:template>
 
    
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
        <xsl:if test="@pos">
        <xsl:text>", "pos": "</xsl:text>
        <xsl:value-of select="@pos"/>
        <xsl:choose>
        <xsl:when test="@msd">
        <xsl:text>", "morph": "</xsl:text>
        <xsl:value-of select="@msd"/>
        </xsl:when>
        <xsl:otherwise>
        <xsl:text>", "morph": "empty</xsl:text>
        </xsl:otherwise>
        </xsl:choose>
        </xsl:if>
        
        <xsl:text>"}</xsl:text>
        <xsl:if test="following::tei:w">
            <xsl:text>,&#10;</xsl:text>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
    ''')
    #parse xsl
    monXSL = etree.XSLT(monXSL)
    t = monXSL(xmlInput)
    print(t)
    #val of i with results from xsl as a list
    i = json.loads( '[' +str(t) +']')
    #second value of the first dico which corr to this list
    witness['tokens']=i
    #file in we save the dico
    with open("fichiers_prod_auto_align/"+iden+"_dico.json", "w") as text_file:
            text_file.write(str(witness))
    #dico witness with ids and tokens
    return witness
    

#class which get a text and list of values
class recupInfo:
    def __init__(self,witness):
        self.witness = witness
    #get the text
    def token(self):
        #corr to the list of tojens
        token_witness = self.witness['tokens']
        #empty list in which we're going to put the value
        liste_de_tok_wit = []
        pos= 0
        #loop on each token
        for i in range (0, len(token_witness)) :
            #get the whole value of each elem
            elem = token_witness[i]
            #list for lemmas
            l = elem['lemme']
            # we fill this list
            liste_de_tok_wit.append(l)
        #list as a string : we got the text
        text = " ".join(liste_de_tok_wit)
        # final value : the text
        return text
    # this enables to modify the list of elements : we add a numerotation and the position of the first letter for each token
    def elem(self):
        token_witness = self.witness['tokens']
        #pos which corr to the value of the first letter of each word
        pos = 0
        # loop on each element
        for i in range (0, len(token_witness)) :
            #we get the position
            token_witness[i]["n"]=i
            elem = token_witness[i]
            l = elem['lemme']
            #if first word
            if elem["n"]==0:
                #new key with value 0
                elem["debut_mot"] = pos
                # we get the lenght of the word in order to have the position for the next word
                pos = len(l)
            # for every other word
            else:
                # pos : last value of pos more 1 (which corresponds to the space) = first letter of the word
                pos = pos +1
                #new key with this new value
                elem["debut_mot"] = pos
                #we add the lenght of the current word at the pos value
                pos = pos + len(l)
        #we get the list of elements with the new items
        return token_witness
 
#function to get the list of ids of the words which start matching passages
def recupid(iden,text,json):
    #empty dico
    val = {}
    #first key : the id of the text
    val["id"] = iden
    #get the value of the id for each position
    liste_des_val = []
    #loop on every element : len(text) =  the number of the matches
    for i in range (0, len(text)) :
    # get the value of first character
        lieuText = text[i][0]
        #loop on the list of modified elements
        for elem in json:
            #if one value of the list of positions corr to value of "debut_mot" of one of the elements
            if lieuText ==  elem["debut_mot"]:
                # I get the id of this element
                liste_des_val.append(elem["id"])
    #new key to my dictionnary with the list of the ids
    val["valeurs"] = liste_des_val
    # get this dico
    return val

#class text, using recupInfo function
class text:
    def __init__(self,iden,doc):
        self.doc = doc
        self.iden = iden
    def dico(self):
        return recupInfo(self.doc).elem()
    def element(self):
        return recupInfo(self.doc).token()

#function for producing XML document
def prodXML(val,listev,cle):
    #creation of the root element
    root = etree.Element("text")
    # loop on every element of the dico of tokens
    for i in val:
        #get all the values
        l = i["lemme"]
        iden = i["id"]
        text = i["text"]
        pos = i["n"]
        po = i["pos"]
        m = i["morph"]
        # if the id is in the list of ids which match
        if iden in listev:
            # creation of an id for paragraph (more 1 because I will need a 0 value)
            piden = listev.index(iden)+1
            piden = str(piden)
            # creation of p element
            p = etree.SubElement(root, "p")
            # creation of attribut
            p.set("n", piden)
        #creation of W element with attributes
        e = etree.SubElement(root, "w")
        e.set("{http://www.w3.org/XML/1998/namespace}id", iden)
        e.set("lemma", l)
        e.set("pos",po)
        e.set("msd",m)
        e.text = text
    #creation of the first XML
    doc = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    #we save it in order to not have pbs of encoding (type bytes, etc)
    fichier = open("fichiers_prod_auto_align/export"+cle+".xml", "wb")  
    fichier.write(doc)
    #xsl to put correct paragraphs
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xsl xs" version="1.0"
   >
    <!-- output-->
    <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>
    
    <!--root-->
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>
    
    <!--text element-->
    <xsl:template match="text">
            <xsl:element name="text">
                <xsl:apply-templates select="p|w"/>
            </xsl:element>      
    </xsl:template>

    <!-- paragraph structure -->
    <xsl:template match="p">
        <xsl:variable name="numP">
            <xsl:value-of select="@n"/>
        </xsl:variable>
        <xsl:element name="p">
            <xsl:attribute name="n">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <!--all the words which are following the current p will be inside the p-->
           <xsl:for-each select="following::w[preceding::p[1][@n=$numP]]">
               <xsl:element name="w">
                   <xsl:copy-of select="@*"/>
                   <xsl:value-of select="."/>
               </xsl:element>
           </xsl:for-each>
        </xsl:element>
    </xsl:template>

    <!--creation of the first paragraph -->
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
    
    <!--no rule because rules already applied-->
    <xsl:template match="w[preceding::p]"/>

</xsl:stylesheet>

    ''')
    #xsl in etree
    monXSL = etree.XSLT(monXSL)
    #apply xsl on the new XML doc
    result_XML = monXSL(etree.parse("fichiers_prod_auto_align/export"+cle+".xml"))
    #we write the finale result
    fichier = open("fichiers_prod_auto_align/export"+cle+"_correct.xml", "wb")  
    fichier.write(result_XML)
    return result_XML

# text-macther as a function
# we can here modify if we want the ngramSize value
def TheMatch(texte1,texte2):
    ta = matcher.Text(texte1.element(), texte1.iden)
    tb = matcher.Text(texte2.element(), texte2.iden)
    m = matcher.Matcher(ta, tb, ngramSize=2).match()
    return(m)

# function which returns the lists of the ids which are concerned by the alignment
def matchXtext(textedeBase, autres):
    #using of text-matcher
    m = TheMatch(textedeBase, autres)
    #we get the list
    pos1 = m[1]
    pos2 = m[2]
    #execution of recupid function
    l1 = recupid(textedeBase.iden,pos1,textedeBase.dico())
    l2 = recupid(autres.iden,pos2,autres.dico())
    #we get our lists of ids
    listeVal1 = l1["valeurs"]
    listeVal2 = l2["valeurs"]    
    return listeVal1, listeVal2

#function which returns list of id concerned by the paragraph
#with list of all the ids which match in text base and the other text, the position of the list to take
def intersection(valL1,valL2,j):
    # get the values sim in valL1
    r  = set.intersection(*[set(list) for list in valL1])
    val1 =[]
    val2 = []
    #get the correct list in list 1 (depending on which text is for now treated)
    for i in range(len(valL1[j])):
        #get the value
            valTok = valL1[j][i]
            #if the value is in the list of the similar values
            if valTok in r :
                #we get the index
                rang = valL1[j].index(valTok)
                # we get the value of the corresponding list thanks to the index
                valTokB = valL2[j][rang]
                #we get this
                val1.append(valTok)
                val2.append(valTokB)
                print(valTokB)
    return val1, val2

#function which makes the action on the folder
# first arg should be the name of the folder, seconde one, the name without extension of the text we want to take as a base of alignment
def boucle(dossier, tbase):
    for dossier, sous_dossiers, fichiers in os.walk('./textes'):
        #get the basic text
        for f in fichiers:
             if f.endswith('.xml') and f == tbase+'.xml':
                cle = re.search('[^.]*', f).group(0)
                with open(os.path.join(dossier, f), 'r') as xml:
                    j = XMLtoJson(etree.parse(xml), cle)
                    # text as an object of the class text
                    textebase = text(cle, j)
        valT = []
        valA =[]
        # get the other texts
        #two loops : first : to obtain all the ids concerned, second : to obtain the ids which match
        for f in fichiers:
            if f.endswith('.xml') and f != tbase+'.xml':
                cle = re.search('[^.]*', f).group(0)
                with open(os.path.join(dossier, f), 'r') as xml:
                    j = XMLtoJson(etree.parse(xml), cle)
                    # text as an object of the text class
                    t = text(cle, j)
                    #apply the match
                    o = matchXtext(textebase, t)
                    #get the list of the values after applying text matcher
                    valT.append(o[0])
                    valA.append(o[1])
        #second loop
        for i, f in enumerate(fichiers):
            if f.endswith('.xml') and f != tbase+'.xml':
                cle = re.search('[^.]*', f).group(0)
                with open(os.path.join(dossier, f), 'r') as xml:
                    j = XMLtoJson(etree.parse(xml), cle)
                    #again as textclass
                    t = text(cle, j)
                #the actual position
                posi = i
                #application of the functiun which gets back the good ids
                val2 = intersection(valT,valA,posi)[1]
                val1 = intersection(valT,valA,posi)[0]
                #functiun of producing XML on texts
                prodXML(t.dico(),val2,t.iden)
    #produce XML for basic text
    prodXML(textebase.dico(),val1, textebase.iden)
