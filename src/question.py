 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: question.py                                                      #
 #############################################################################

from __future__ import division
import re
import math
from operator import attrgetter
from structs import *
from database import *
from export import export_xml

def parse_question(question, stoplist):
    "Split an user's question in (term, weight) pairs. Where the term's weight "
    "is omitted by the user, a default value of 1 will be assigned"
    "Those elements whose related terms are contained into the stoplist will "
    "not be computed"
    "A list of Question tuples will be returned"

    term_re = '[a-z]([a-z0-9])*(-[0-9]([a-z0-9])*)*'
    weight_re = '0\.[0-9]+'
    question_re = term_re + '( ' + weight_re + ')?'
    if re.match('^(' + question_re + ' )+$', question + ' ', re.I) != None:
        matches = re.finditer(question_re, question, re.I)
        question_terms = []
        for m in matches:
            term = m.group().split()
            term[0] = term[0].lower()
            if term[0] not in stoplist and len(term[0]) <= 32:
                if len(term) == 1:
                    term += '1'
                question_terms.append(Question(term[0], float(term[1])))
    else:
        question_terms = None
    return question_terms

def get_stoplist(path):
    "Get the stop words from the list in the given file"

    stoplist = []
    file = open(path, 'r')
    for line in file:
        stoplist += line.split()
    file.close()

    # Return a list containing the stop words
    return stoplist

def get_related_documents(question, db):
    "Return a list containing all the IDs of all the documents matching any "
    "of the terms in the question"

    id_docs = []
    cursor = db.cursor()
    sql_sentence = 'SELECT id_doc FROM Posting WHERE term = %s'
    for q in question:
        cursor.execute(sql_sentence, (q.term, ))
        fetch = cursor.fetchall()
        for f in fetch:
            if f[0] not in id_docs:
                id_docs.append(f[0])
    cursor.close()
    return id_docs

def vectorial_model(question, id_doc, db):
    "Calculate the similarity between the question and the provided document, "
    "attending to the vectorial model for information retrieval"

    modd = 0
    modq = 0
    dxq = 0
    cursor = db.cursor()
    sql = 'SELECT term, weight FROM Posting WHERE id_doc = %s'

    # Calculate the weight vector for the analyzed document along with its
    # module
    document = {}
    cursor.execute(sql, (id_doc, ))
    d = cursor.fetchall()
    for term, weight in d:
        document[term] = weight
        modd += math.pow(weight, 2)
    modd = math.sqrt(modd)
    cursor.close()

    # Calculate the dot product of the document and question's vector,
    # along with the question's vector module
    for term, weight in question:
        modq += math.pow(weight, 2)
        if term in document:
            dxq += weight * document[term]
    modq = math.sqrt(modq)
    
    # Calculate the similarity of the vectors referring the provided question
    # and document
    sem = dxq / (modq * modd)
    return sem * 100

def boolean_model(question, id_doc, db):
    "Calculate the similarity between the question and the provided document, "
    "attending to the boolean model for information retrieval"
    "This implementation is based on the assumption of being called after "
    "upon the results of get_related_documents, which filters the documents "
    "matching any of the terms in the question"

    return 100

def probabilistic_model(question, id_doc, db):
    "Calculate the similarity between the question and the provided document, "
    "attending to the probabilistic model for information retrieval"

    sem = 0
    qj = 0.5
    cursor = db.cursor()
    sql_fdj = 'SELECT COUNT(id_doc) FROM Posting WHERE term = %s'
    sql_n = 'SELECT COUNT(id_doc) FROM Doc'
    sql_w = 'SELECT term, weight FROM Posting WHERE id_doc = %s'

    cursor.execute(sql_n)
    n = cursor.fetchone()[0]

    # Calculate the weight vector for the analyzed document
    document = {}
    cursor.execute(sql_w, (id_doc, ))
    d = cursor.fetchall()
    for term, weight in d:
        document[term] = weight

    # Calculate the qj (fixed to 0.5) and sj probabilities, regarding the
    # probability of the term being in the set of relevant documents (for 
    # every term appearing on both question and document), and use them to
    # compute the similarity among the question and document's vectors
    for term, weight in question:
        if term in document:
            cursor.execute(sql_fdj, (term, ))
            sj = cursor.fetchone()[0] / n
            if sj * (1 - qj) != 0:
                log = math.log((qj * (1 - sj)) / ((sj * (1 - qj))), 2)
                if log > 0:
                    sem += weight * document[term] * log
    cursor.close()

    return sem * 100


def extended_boolean_model(question, id_doc, db):
    "Calculate the similarity between the question and the provided document, "
    "attending to the extended boolean model for information retrieval"
    "A standard weight of 2 is given to the operator used (OR)"

    d2xq2 = 0
    modq = 0

    cursor = db.cursor()
    sql = 'SELECT term, weight FROM Posting WHERE id_doc = %s'

    # Calculate the weight vector for the analyzed document
    document2 = {}
    cursor.execute(sql, (id_doc, ))
    d = cursor.fetchall()
    for term, weight in d:
        document2[term] = math.pow(weight, 2)
    cursor.close()

    # Calculate the dot product of the question and document vectors,
    # along with the module of the question vector
    for term, weight in question:
        wq2 = math.pow(weight, 2)
        modq += wq2
        if term in document2:
            d2xq2 += wq2 * document2[term]

    # Calculate the similarity of the vectors referring the provided question
    # and document
    sem = math.sqrt(d2xq2 / modq)
    return sem * 100

def generate_output(results, db):
    "Turn results in a list of Result tuples containing the results of the "
    "search process. The relevancy order, every data from the document (its "
    "id, title and text) and its computed relevance are provided"
    "Such a list is returned"

    sql_sentence = 'SELECT title, text FROM Doc WHERE id_doc = %s'
    cursor = db.cursor()
    for d in range(len(results)):
        id = results[d].doc
        relevance = results[d].relevance
        cursor.execute(sql_sentence, (id, ))
        title, text = cursor.fetchone()
        results[d] = Result(str(d + 1), Document(str(id), title, text),
                            str(relevance))
    cursor.close()

def search_question(algorithm, question, output_stream = None):
    "Ask (search) the question provided against the system's database. "
    "Compute the similarity degree for the relevant documents according to the "
    "selected algorithm, sort them in decreasing order, and export the search "
    "results as a XML document, as well as returning them in a list of result "
    "tuples"
    "As the documents' similarity values are computed, the output_stream "
    "variable, if provided, will be updated with a message detailing the last "
    "analyzed document's identifier and its similarity degree"

    db = connect_db()
    if output_stream is not None:
        output_stream.set('Buscando...')
    id_docs = get_related_documents(question, db)
    docs = []
    for d in id_docs:
        similarity = algorithm(question, d, db)
        if similarity > 0:
            docs.append(Result(doc = d, relevance = similarity, n = None))
            if output_stream is not None:
                output_stream.set('Procesado documento ' + str(d))
                output_stream.set(output_stream.get() + '\nRelevancia: ' + str(similarity) + '%\n')
    docs = sorted(docs, key = attrgetter('relevance'), reverse = True)
    generate_output(docs, db)
    disconnect_db(db)
    return docs

def validate_question_string(search_input):
    "Validate the provided string against the regular expression defining a "
    "valid question syntax"
    "Return if a match is found"

    term_re = '[a-z]([a-z0-9])*(-[0-9]([a-z0-9])*)*'
    weight_re = '0\.[0-9]+'
    question_re = term_re + '( ' + weight_re + ')?'
    return re.match('^(' + question_re + ' )+$', search_input + ' ',
                    re.I) != None

def search_string(algorithm, search_input, output_stream = None):
    "Validate and parse the provided string to obtain a list of Question "
    "tuples, that will be asked to the system, which will be return its "
    "results in the form of a list of Result tuples"

    algorithm = ComputeSimilarity.value(algorithm)
    question = parse_question(search_input, get_stoplist('stoplist.txt'))
    if algorithm is not None and question is not None:
        docs = search_question(algorithm, question, output_stream)
        export_xml(question, docs)
    else:
        docs = None
    return docs

class ComputeSimilarity:
    vectorial = vectorial_model
    boolean = boolean_model
    probabilistic = probabilistic_model
    extended_boolean = extended_boolean_model

    algorithms = {'Modelo vectorial': vectorial, 'Modelo booleano': boolean,
                    'Modelo probabilistico': probabilistic,
                    'Modelo booleano extendido': extended_boolean}

    @staticmethod
    def value(name):
        return ComputeSimilarity.algorithms[name]

    @staticmethod
    def list():
        return ComputeSimilarity.algorithms.keys()
