<?xml version="1.0" encoding="UTF-8"?>
<!-- fichier de transformation vers l xml issu de collatex vers un xml plus conforme, étape 1-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="tei xsl" version="1.0">

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
