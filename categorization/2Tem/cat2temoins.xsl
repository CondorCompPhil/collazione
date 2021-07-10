<?xml version="1.0" encoding="UTF-8"?>
<!-- fichier de transformation vers l xml issu de collatex vers de la tei propre
catégorisation des variantes sur deux témoins
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="#all" version="2.0"
    xmlns="http://www.tei-c.org/ns/1.0">
    <!-- génération de la sortie -->
    <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>

    <!-- on crée la structure du document avec un teiHeader rempli -->
    <xsl:template match="/">
        <xsl:element name="TEI">
            <xsl:element name="teiHeader">
                <xsl:element name="fileDesc">
                    <xsl:copy-of
                        select="document('AF_travail_lemmes.xml')/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt"/>
                    <xsl:copy-of
                        select="document('AF_travail_lemmes.xml')/tei:TEI/tei:teiHeader/tei:fileDesc/tei:publicationStmt"/>

                    <xsl:element name="sourceDesc">
                        <xsl:element name="p">
                            <xsl:text>La collation présente ici est réalisée sur deux témoins de l'oeuvre, le BNF français 768, dans l'édition d'Elspeth Kennedy, et le Bibliothèque Mazarine, Inc 491. </xsl:text>
                        </xsl:element>
                    </xsl:element>
                </xsl:element>
                <xsl:element name="encodingDesc">
                    <xsl:element name="projectDesc">
                        <xsl:element name="p">
                            <xsl:text>Il s'agit ici du résultat d'une collation réalisée avec le module python de Collatex.</xsl:text>
                        </xsl:element>
                    </xsl:element>
                    <xsl:element name="editorialDecl">
                        <xsl:element name="normalization">
                            <xsl:element name="p">
                                <xsl:text>Le texte est normalisé, les abréviations sont résolues. Seules les lettres non accentuées dans les originaux restent fidèles à leur source.</xsl:text>
                            </xsl:element>
                        </xsl:element>
                        <xsl:element name="segmentation">
                            <xsl:element name="p">
                                <xsl:text>Le texte est struturé en divisions, correspondant aux chapitres, et en paragraphes. Chaque variante se retrouve encodée dans dans un élément particulier, qui met les deux leçons en regard.</xsl:text>

                            </xsl:element>
                            <xsl:element name="p">
                                <xsl:text>Chaque mot se situe à l'intérieur d'une balise. Cet élément comporte des attributs donnant un identifiant, le lemme de référence, un étiquetage morpho-syntaxique.</xsl:text>
                            </xsl:element>
                        </xsl:element>
                    </xsl:element>
                </xsl:element>
                <xsl:element name="revisionDesc">
                    <xsl:element name="change">
                        <xsl:attribute name="resp">
                            <xsl:value-of select="'#LI'"/>
                        </xsl:attribute>
                        <xsl:attribute name="status">
                            <xsl:value-of select="'collConf'"/>
                        </xsl:attribute>
                        <xsl:text>Fichier de collation conforme à la TEI, à partir du fichier généré par Collatex et de nos fichiers TEI d'origine, comportant les lemmes, créé le </xsl:text>
                        <xsl:element name="date">
                            <xsl:attribute name="when">
                                <xsl:value-of select="'2018-04-20'"/>
                            </xsl:attribute>
                            <xsl:text>20 avril 2018</xsl:text>
                        </xsl:element>
                        <xsl:text> par Lucence Ing </xsl:text>
                    </xsl:element>
                </xsl:element>
            </xsl:element>
            <xsl:element name="text">
                <xsl:element name="body">
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:element>
        </xsl:element>
    </xsl:template>

    <!-- on reprend la structure en paragraphe -->
    <xsl:template match="p">
        <xsl:element name="p">
            <xsl:attribute name="n">
                <xsl:value-of select="@n"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="app">
        <xsl:element name="app">
            <!-- si une seule variante, on définit un attribut qui indique qu'il y a une seule variante -->
            <xsl:if test="sum(count(child::rdg)) = 1">
                <xsl:attribute name="type">
                    <xsl:value-of select="concat('only', substring(child::rdg/@xml:id, 1, 2))"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:for-each select="child::rdg[@wit = '#A']">
                <!-- on enregistre dans des variables les valeurs d id et de lemmes des mots -->
                <xsl:variable name="lemme">
                    <xsl:value-of select="@lemma"/>
                </xsl:variable>
                <xsl:variable name="pos">
                    <xsl:value-of select="@type"/>
                </xsl:variable>
                <xsl:variable name="morph">
                    <xsl:value-of select="@ana"/>
                </xsl:variable>
                <xsl:variable name="text">
                    <xsl:value-of select="."/>
                </xsl:variable>

                <xsl:variable name="id">
                    <xsl:value-of select="@xml:id"/>
                </xsl:variable>
                <xsl:choose>
                    <xsl:when test="parent::app/rdg[@wit = '#B']/@lemma = $lemme">
                        <xsl:choose>
                            <xsl:when
                                test="$pos != parent::app/rdg[@wit = '#B'][@lemma = $lemme]/@type">
                                <xsl:attribute name="ana">
                                    <xsl:value-of select="'diffPos'"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:otherwise>
                                <!-- si les types et les lemmes correspondent, on regarde si la MS correspond elle aussi -->
                                <xsl:choose>
                                    <xsl:when
                                        test="$morph != parent::app/rdg[@wit = '#B'][@lemma = $lemme]/@ana">
                                        <xsl:attribute name="ana">
                                            <xsl:value-of select="'diffMorph'"/>
                                        </xsl:attribute>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <!-- on regarde enfin les différences de graphies -->
                                        <xsl:if
                                            test="$text != parent::app/rdg[@wit = '#B'][@lemma = $lemme]/text()">
                                            <xsl:attribute name="ana">
                                                <xsl:value-of select="'diffGraph'"/>
                                            </xsl:attribute>
                                        </xsl:if>
                                    </xsl:otherwise>
                                </xsl:choose>
                                
                            </xsl:otherwise>
                        </xsl:choose>
                        
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:choose>
                            <xsl:when test="parent::app/rdg[@wit = '#B']">
                                <xsl:attribute name="ana">
                                    <xsl:value-of select="'diffLemme'"/>
                                </xsl:attribute>
                            </xsl:when>
                        </xsl:choose>
                       
                    </xsl:otherwise>
                </xsl:choose>
                
            </xsl:for-each>

            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!-- pour chaque rdg, on remplace les valeurs de witness par les sigles de nos témoins -->
    <xsl:template match="rdg">
        <xsl:element name="rdg">
            <xsl:attribute name="wit">
                <xsl:choose>
                    <xsl:when test="@wit = '#A'">
                        <xsl:value-of select="'#Ao'"/>
                    </xsl:when>
                    <xsl:when test="@wit = '#B'">
                        <xsl:value-of select="'#Ez'"/>
                    </xsl:when>
                </xsl:choose>
            </xsl:attribute>
            <xsl:element name="w">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="@xml:id"/>
                </xsl:attribute>
                <xsl:attribute name="lemma">
                    <xsl:value-of select="@lemma"/>
                </xsl:attribute>
                <xsl:attribute name="type">
                    <xsl:value-of select="@type"/>
                </xsl:attribute>
                <xsl:attribute name="ana">
                    <xsl:value-of select="@ana"/>
                </xsl:attribute>
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
