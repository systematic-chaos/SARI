<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:template match="Resultado">
		<html>
			<head>
				<title>Resultados de la busqueda</title>
			</head>
			<body>
				<h1>
					<p align="center">Resultados de la Búsqueda</p>
				</h1>
				<xsl:apply-templates select="Pregunta"/>&#010;----&#013;
				<p>
					<b>Documentos relevantes: </b>
					<xsl:apply-templates select="Documento"/>
				</p>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="Pregunta">
		<p>
			<b>Pregunta: </b>
			<xsl:apply-templates select="Item"/>
		</p>
	</xsl:template>
	<xsl:template match="Item">
		<p>
			<b>
				<i>
					<xsl:apply-templates select="Termino"/>
				</i>
			</b>&#032;-&#032;
			<i>
				<xsl:apply-templates select="Peso"/>
			</i>
		</p>
	</xsl:template>
	<xsl:template match="Termino">
		<i>
			<xsl:apply-templates/>&#032;
		</i>
	</xsl:template>
	<xsl:template match="Peso">
		<i>
			<xsl:apply-templates/>&#032;
		</i>
	</xsl:template>
	<xsl:template match="Documento">
		<p>
			<b>
				<xsl:value-of select="@ID"/>
			</b>
			&#032;-&#032;
			<b>
				<i>
					<xsl:apply-templates select="Titulo"/>
				</i>
			</b>&#009;-&#009;
			<xsl:apply-templates select="Relevancia"/>&#009;-&#009;
			<a>
				<xsl:attribute name="href">
					<xsl:apply-templates select="Texto"/>
				</xsl:attribute>
				Documento
			</a>
		</p>
	</xsl:template>
</xsl:stylesheet>
