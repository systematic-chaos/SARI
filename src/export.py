 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: export.py                                                        #
 #############################################################################

from lxml import etree as ET
import StringIO
from structs import *

def style(xml):
    "Set the header to the received XML element tree, so that it will be "
    "enabled to validation against its DTD, and formatted according to its XSLT"
    "Return the obtained XML in an Unicode string"

    s = '<?xml version = \"1.0\" encoding = \"UTF-8\"?>'
    s += '<!DOCTYPE Resultado SYSTEM \"Resultados.dtd\">'
    s += '<?xml-stylesheet type = \"text/xsl\" href = \"Resultados.xsl\"?>'
    s+='<Resultado></Resultado>'
    tree = ET.parse(StringIO.StringIO(s))
    root = tree.getroot()
    root[:] = xml
    root.text, root.tail = xml.text, xml.tail
    #xslt_root = ET.parse('results/Resultados.xsl')
    #transform = ET.XSLT(xslt_root)
    #resultXML = transform(xml)
    return ET.tostring(tree, xml_declaration = True, encoding = 'UTF-8',
                        pretty_print = True)

def export_xml(question, results):
    "Generate a XML file (according to the DTD and XSLT files provided) "
    "containing the answer asked by the user and the results of the search "
    "carried out"

    root = ET.Element('Resultado')
    pregunta = ET.SubElement(root, 'Pregunta')
    for q in question:
        item = ET.SubElement(pregunta, 'Item')
        termino = ET.SubElement(item, 'Termino')
        termino.text = q.term
        peso = ET.SubElement(item, 'Peso')
        peso.text = str(q.weight)
    for r in results:
        documento = ET.SubElement(root, 'Documento', ID = r.doc.id)
        titulo = ET.SubElement(documento, 'Titulo')
        titulo.text = r.doc.title
        relevancia = ET.SubElement(documento, 'Relevancia')
        relevancia.text = r.relevance
        texto = ET.SubElement(documento, 'Texto')
        texto.text = r.doc.text
    prettyXML = style(root)
    file = open('results/Resultados.xml', 'w')
    file.write(prettyXML)
    file.close()
