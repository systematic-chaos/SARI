 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: feedback.py                                                      #
 #############################################################################

from structs import *
from database import *
import question

def get_document_vector(id_doc):
    "Calculate the weight vector for the analyzed document"

    sql = 'SELECT term, weight FROM Posting WHERE id_doc = %s'
    document = []
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(sql, (id_doc, ))
    d = cursor.fetchall()
    for term, weight in d:
        document.append(Question(term, weight))
    cursor.close()
    disconnect_db(db)
    return document

def search_similar_docs(algorithm, id_doc, output_stream = None):
    "Look for documents similar to the one provided, by getting the vector of "
    "such a document and asking the system a question composed of the "
    "individual terms and weights in the vector"

    return question.search_question(question.ComputeSimilarity.value(algorithm),
                                    get_document_vector(id_doc), output_stream)
