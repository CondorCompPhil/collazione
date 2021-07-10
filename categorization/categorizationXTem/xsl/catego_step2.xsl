<?xml version="1.0" encoding="UTF-8"?>
<!-- fichier de transformation de l'xml avec des rdg vers une structuration plus conforme-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="tei xsl" version="1.0">
    <!-- génération de la sortie -->
    <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="no" encoding="UTF-8"/>
    
    <!-- python veut pas : peut etre rajouter des app ? -->
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
