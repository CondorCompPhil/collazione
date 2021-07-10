#coding utf-8

from lxml import etree

#script incluant deux xsl successives pour obtenir un fichier XML avec des variantes catégorisées


# attention, le xml doit avoir des xml:id différents pour chaque mot, sinon ne fonctonne pas
#on parse l'XML
cat = etree.parse("out.xml")

#fonction
def XSL(monXML,cle):
    #première XSL : on regroupe les types de variantes
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" exclude-result-prefixes="xsl" version="1.0">
<!-- fichier de transformation vers l xml issu de collatex vers un xml plus conforme étape 1-->
    
    <!-- génération de la sortie -->
    
 <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>

    <!-- structure -->
    <xsl:template match="/">
        <xsl:element name="text">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!-- pour mettre les informations dans des app et rdg imbriquées, utilisation d'une boucle géante (besoin de xslt 1 pour parser en python) -->
    <xsl:template match="app">
        <xsl:element name="app">
            <!-- pour chaque lemme -->
            <xsl:for-each select="child::rdg[not(@lemma = preceding-sibling::rdg/@lemma)]">
                <xsl:variable name="w">
                    <xsl:for-each select="../rdg[@lemma = current()/@lemma]">
                        <xsl:value-of select="@wit"/>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:variable name="id">
                    <xsl:for-each select="../rdg[@lemma = current()/@lemma]">
                        <xsl:value-of select="concat(@xml:id, ' ')"/>
                    </xsl:for-each>
                </xsl:variable>
                <!-- création d'un élément avec ses attributs -->
                <xsl:element name="rdg">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'subst'"/>
                    </xsl:attribute>
                    <xsl:attribute name="wit">
                        <xsl:value-of select="$w"/>
                    </xsl:attribute>
                    <xsl:attribute name="corresp">
                        <xsl:value-of select="$id"/>
                    </xsl:attribute>
                    <xsl:attribute name="lemma">
                        <xsl:value-of select="@lemma"/>
                    </xsl:attribute>
                    <!-- pour chaque pos différent -->
                    <xsl:for-each
                        select="../rdg[@lemma = current()/@lemma and not(@pos = preceding-sibling::rdg[@lemma = current()/@lemma]/@pos)]">
                        <xsl:variable name="w2">
                            <xsl:for-each
                                select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos]">
                                <xsl:value-of select="@wit"/>
                            </xsl:for-each>
                        </xsl:variable>
                        <xsl:variable name="id2">
                            <xsl:for-each
                                select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos]">
                                <xsl:value-of select="concat(@xml:id, ' ')"/>
                            </xsl:for-each>
                        </xsl:variable>
                        <xsl:choose>
                            <!-- si tém lemm et tém pos sont égaux -->
                            <xsl:when test="$w = $w2">
                                <!-- on teste morph -->
                                <xsl:for-each
                                    select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and not(@msd = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos]/@msd)]">
                                    <xsl:variable name="w3">
                                        <xsl:for-each
                                            select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]">
                                            <xsl:value-of select="@wit"/>
                                        </xsl:for-each>
                                    </xsl:variable>
                                    <xsl:variable name="id3">
                                        <xsl:for-each
                                            select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]">
                                            <xsl:value-of select="concat(@xml:id, ' ')"/>
                                        </xsl:for-each>
                                    </xsl:variable>
                                    <xsl:choose>
                                        <!-- si tém morph égaux -->
                                        <xsl:when test="$w2 = $w3">
                                            <!-- on test texte -->
                                            <xsl:for-each
                                                select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and not(text() = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]/text())]">
                                                <xsl:variable name="w4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="@wit"/>
                                                  </xsl:for-each>
                                                </xsl:variable>
                                                <xsl:variable name="id4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="concat(@xml:id, ' ')"
                                                  />
                                                  </xsl:for-each>
                                                </xsl:variable>
                                                <xsl:choose>
                                                  <!-- si tout est égal -->
                                                  <xsl:when test="$w3 = $w4">
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id4"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="pos">
                                                  <xsl:value-of select="@pos"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="msd">
                                                  <xsl:value-of select="@msd"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:when>
                                                  <!-- si diff de graphie -->
                                                  <!-- on rajoute les infos ling sur le rdg -->
                                                  <xsl:otherwise>
                                                  <xsl:if test="position() = 1">
                                                  <xsl:attribute name="pos">
                                                  <xsl:value-of select="@pos"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="msd">
                                                  <xsl:value-of select="@msd"/>
                                                  </xsl:attribute>
                                                  </xsl:if>
                                                  <!-- on crée l'élément de diff de graphie -->
                                                  <xsl:element name="rdg">
                                                  <xsl:attribute name="type">
                                                  <xsl:value-of select="'graph'"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w4"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id4"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:element>
                                                  </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:for-each>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <!-- pour diff de morph : on répète les mêmes choix et règles après avoir créé l'élément et l'info ling sur l'élément précédent-->
                                            <xsl:if test="position() = 1">
                                                <xsl:attribute name="pos">
                                                  <xsl:value-of select="@pos"/>
                                                </xsl:attribute>
                                            </xsl:if>
                                            <xsl:element name="rdg">
                                                <xsl:attribute name="type">
                                                  <xsl:value-of select="'morph'"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w3"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id3"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="msd">
                                                  <xsl:value-of select="@msd"/>
                                                </xsl:attribute>
                                                <!-- récupération des variables -->
                                                <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and not(text() = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]/text())]">
                                                  <xsl:variable name="w4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="@wit"/>
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:variable name="id4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="concat(@xml:id, ' ')"
                                                  />
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:choose>
                                                  <!-- si graphies similaire, on met juste le texte -->
                                                  <xsl:when test="$w3 = $w4">
                                                  <xsl:value-of select="."/>
                                                  </xsl:when>
                                                  <!-- si diff de graphie, nouvel élément -->
                                                  <xsl:otherwise>
                                                  <xsl:element name="rdg">
                                                  <xsl:attribute name="type">
                                                  <xsl:value-of select="'graph'"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w4"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id4"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:element>
                                                  </xsl:otherwise>
                                                  </xsl:choose>
                                                </xsl:for-each>
                                            </xsl:element>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:for-each>
                            </xsl:when>
                            <!-- pour diff de pos, on répète les mêmes choix et règles après avoir créé l'élément-->
                            <xsl:otherwise>
                                <xsl:element name="rdg">
                                    <xsl:attribute name="type">
                                        <xsl:value-of select="'pos'"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="wit">
                                        <xsl:value-of select="$w2"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="corresp">
                                        <xsl:value-of select="$id2"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="pos">
                                        <xsl:value-of select="@pos"/>
                                    </xsl:attribute>
                                    <!-- récupération des variables -->
                                    <xsl:for-each
                                        select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and not(@msd = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos]/@msd)]">
                                        <xsl:variable name="w3">
                                            <xsl:for-each
                                                select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]">
                                                <xsl:value-of select="@wit"/>
                                            </xsl:for-each>
                                        </xsl:variable>
                                        <xsl:variable name="id3">
                                            <xsl:for-each
                                                select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]">
                                                <xsl:value-of select="concat(@xml:id, ' ')"/>
                                            </xsl:for-each>
                                        </xsl:variable>
                                        <xsl:choose>
                                            <!-- si tém morph égaux -->
                                            <xsl:when test="$w2 = $w3">
                                                <!-- on test texte -->
                                                <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and not(text() = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]/text())]">
                                                  <xsl:variable name="w4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="@wit"/>
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:variable name="id4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="concat(@xml:id, ' ')"
                                                  />
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:choose>
                                                  <!-- si tout est égal -->
                                                  <xsl:when test="$w3 = $w4">
                                                  <xsl:attribute name="msd">
                                                  <xsl:value-of select="@msd"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:when>
                                                  <!-- si diff de graphie -->
                                                  <xsl:otherwise>
                                                  <xsl:element name="rdg">
                                                  <xsl:attribute name="type">
                                                  <xsl:value-of select="'graph'"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w4"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id4"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:element>
                                                  </xsl:otherwise>
                                                  </xsl:choose>
                                                </xsl:for-each>
                                            </xsl:when>
                                            <!-- si pas d'égalité -->
                                            <xsl:otherwise>
                                                <xsl:element name="rdg">
                                                  <xsl:attribute name="type">
                                                  <xsl:value-of select="'morph'"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w3"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id3"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="msd">
                                                  <xsl:value-of select="@msd"/>
                                                  </xsl:attribute>
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and not(text() = preceding-sibling::rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd]/text())]">
                                                  <xsl:variable name="w4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="@wit"/>
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:variable name="id4">
                                                  <xsl:for-each
                                                  select="../rdg[@lemma = current()/@lemma and @pos = current()/@pos and @msd = current()/@msd and text() = current()/text()]">
                                                  <xsl:value-of select="concat(@xml:id, ' ')"
                                                  />
                                                  </xsl:for-each>
                                                  </xsl:variable>
                                                  <xsl:choose>
                                                  <xsl:when test="$w3 = $w4">
                                                  <xsl:value-of select="."/>
                                                  </xsl:when>
                                                  <!-- si diff de graphie -->
                                                  <xsl:otherwise>
                                                  <xsl:element name="rdg">
                                                  <xsl:attribute name="type">
                                                  <xsl:value-of select="'graph'"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="wit">
                                                  <xsl:value-of select="$w4"/>
                                                  </xsl:attribute>
                                                  <xsl:attribute name="corresp">
                                                  <xsl:value-of select="$id4"/>
                                                  </xsl:attribute>
                                                  <xsl:value-of select="."/>
                                                  </xsl:element>
                                                  </xsl:otherwise>
                                                  </xsl:choose>
                                                  </xsl:for-each>
                                                </xsl:element>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:for-each>
                                </xsl:element>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:element>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
</xsl:stylesheet>


    ''')
    #on met l'xsl dans etree
    monXSL = etree.XSLT(monXSL)
    result1 = monXSL(monXML)
    #on enregistre le fichier XML
    fichier = open(cle+"_cat_auto_step1.xml", "wb")  
    fichier.write(result1)
    #on parse ce résultat d'étape
    result11 = etree.parse(cle+"_cat_auto_step1.xml")
    #deuxième xsl qui permet une structuration conforme
    monXSL2 = etree.XML('''
<!-- fichier de transformation de l'xml avec des rdg vers une structuration plus conforme-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" exclude-result-prefixes="xsl" version="1.0">
    
    <!-- génération de la sortie -->
    <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>
  
    <!-- structure -->
    <xsl:template match="/">
        <xsl:element name="text">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="app">
        
        <xsl:choose>
            <!-- pour avoir l'app de diff de mots -->
            <xsl:when test="count(child::rdg[@type = 'subst']) != 1">
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'subst'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:when>
            <!-- pour les  app qui ne comportent pas qu'une seule leçon mais sans diff de mots : juste élément app-->
            <xsl:when test="count(child::rdg[@type = 'subst']) = 1 and child::rdg/child::rdg">
                <xsl:element name="app">
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="rdg">
        <!-- pour les leçons identiques partout -->
        <xsl:if
            test="@type = 'subst' and parent::app[count(child::rdg) = 1] and not(child::rdg)">
            <xsl:element name="app"><xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @lemma | @pos | @msd"/>
                <xsl:apply-templates/>
            </xsl:element></xsl:element>
        </xsl:if>
        
        <!-- pour les rdg sans enfants (juste diff de mots) -->
        <xsl:if
            test="@type = 'subst' and not(child::rdg) and parent::app[count(child::rdg) != 1]">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @lemma | @pos | @msd"/>
                <xsl:apply-templates/>
            </xsl:element>
            
        </xsl:if>
        
        <!-- si enfant de subst : pos -->
        <xsl:if test="@type = 'subst' and child::rdg[@type = 'pos']">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @lemma"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'pos'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si pos avec enfant morph-->
        <xsl:if test="@type = 'pos' and child::rdg[@type = 'morph']">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @pos"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'morph'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si pos avec enfant graph -->
        <xsl:if test="@type = 'pos' and child::rdg[@type = 'graph']">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @pos | @msd"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'graph'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si pos sans enfant -->
        <xsl:if test="@type = 'pos' and not(child::rdg)">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @pos | @msd"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:if>
        
        <!-- si enfant morph de subst -->
        <xsl:if test="@type = 'subst' and child::rdg[@type = 'morph']">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @lemma | @pos"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'morph'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si morph avec enfant (forcément graph)-->
        <xsl:if test="@type = 'morph' and child::rdg">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @pos | @msd"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'graph'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si morph sans enfant -->
        <xsl:if test="@type = 'morph' and not(child::rdg)">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @pos | @msd"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:if>
        
        <!-- si enfant graph (de subst)-->
        <xsl:if test="@type = 'subst' and child::rdg[@type = 'graph']">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp | @lemma | @pos | @msd"/>
                <xsl:element name="app">
                    <xsl:attribute name="type">
                        <xsl:value-of select="'graph'"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:if>
        
        <!-- si graph -->
        <xsl:if test="@type = 'graph'">
            <xsl:element name="rdg">
                <xsl:copy-of select="@wit | @corresp"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:if>
        
    </xsl:template>
    
</xsl:stylesheet>

    ''')
    #on met l'xsl dans etree
    monXSL2 = etree.XSLT(monXSL2)
    resultDef = monXSL2(result11)
    #écriture du fichier
    fichier = open(cle+"_cat_auto.xml", "wb")  
    fichier.write(resultDef)
    print("Categorization done")

#application de la fonction
XSL(cat, "out")