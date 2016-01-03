#! /usr/bin/python

 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: index.py                                                         #
 #############################################################################

import os
import os.path
import shutil
import re
from structs import *
from database import *

def store_file(src, dst):
    "Copy a file and its metadata from the src to the dst paths"

    shutil.copy2(src, dst)
    return os.path.join(dst, os.path.basename(src))

def parse_file(path, stoplist):
    "Get all the terms from the file in path, along with the document's title"

    with open(path, 'r') as file:

        # The regular expression defining a valid term
        prog = re.compile('[a-z]([a-z0-9])*(-[0-9]([a-z0-9])*)*',
                            re.IGNORECASE)
        terms = {}

        # Set the file's first line as the document's title
        title = file.readline()[:-1]
        if title.endswith('\r'):
            title = title[:-1]
        file.seek(0)
        for line in file:
            it = prog.finditer(line)
            for match in it:
                match = match.group()
                if len(match) <= 32:
                    match = match.lower()
                    if match in terms:
                        terms[match] = terms[match] + 1
                    else:
                        terms[match] = 1
    file.closed

    # Return the title of the document and a dictionary having the valid words
    # in the document (as its keys) as well as the number of instances of each
    # one of them (as its data)
    doc = Document(title = title, text = path, id = None)
    remove_stoplist_terms(terms, stoplist)
    terms = terms.items()
    occurrences = []
    for t in terms:
        occurrences.append(Post(term = t[0], weight = t[1], id = None))
    return doc, occurrences

def remove_stoplist_terms(terms, stoplist):
    "Remove every entry in the terms dictionary whose key (the term itself)"
    "corresponds to any of the terms in the stoplist"

    for t in stoplist:
        if t in terms:
            del terms[d]

def add_db_doc(db, doc, terms):
    "Add the information obtained from the text file to the database via "
    "a connection which must have been previously opened. Title and text "
    "are strings containing the so-called attributes in the database. Terms "
    "is a dictionary data structure containing the valid terms in the document "
    "(as its keys) as well as the weight associated to each one of them "
    "(as its data)"

    cursor = db.cursor()
    sql_sentence = ("INSERT INTO Doc "
                    "(title, text) "
                    "VALUES (%s, %s)")
    sql_data = (doc.title, doc.text);
    cursor.execute(sql_sentence, sql_data)
    
    sql_sentence = ("INSERT INTO Posting "
                    "(term, id_doc, weight) "
                    "VALUES (%s, %s, %s)")
    doc = doc._replace(id = cursor.lastrowid)
    for t in terms:
        sql_data = (t.term, doc.id, t.weight)
        cursor.execute(sql_sentence, sql_data)

    cursor.close()

def get_stoplist(path):
    "Get the stop words from the list in the given file"

    stoplist = []
    file = open(path, 'r')
    for line in file:
        stoplist+=line.split()
    file.close()

    # Return a list containing the stop words
    return stoplist

def index_file(path, output_stream = None, db = None, stoplist = None):
    "Store the file given by path in the application's local directory, "
    "parse it to obtain its title and key terms (from which those contained in "
    "the stoplist are removed), which are handled and indexed in the database"
    "If either the database connection or the stop-words list are not provided "
    "to the function via their corresponding parameters, the function will "
    "initialize them by its own. Once the file has been successfully indexed, "
    "the output_stream variable (if provided) will be updated by appending "
    "a message detailing the accomplishment of such an operation"
    
    inherited_db_connection = db is not None
    if not inherited_db_connection:
        db = connect_db()
    if stoplist is None:
        stoplist = get_stoplist('stoplist.txt')
    file = store_file(path, 'docs/')
    doc, terms = parse_file(file, stoplist)

    if output_stream is not None:
        output_stream.set(output_stream.get() + file + ' indexed\n')

    add_db_doc(db, doc, terms)

    if not inherited_db_connection:
        db.commit()
        disconnect_db(db)

def index_directory(path, output_stream = None):
    "Recursively index (parse and insert into the database) all the files "
    "listed in the given path. If the output_stream variable is provided, it"
    "will be passed to the subsequent function calls in order to show the "
    "completion of the files indexation on as they are completed"

    db = connect_db()
    stoplist = get_stoplist('stoplist.txt')
    files = os.listdir(path)
	
    for f in files:
        f = os.path.join(path, f)
        if not os.path.islink(f):
            if not os.path.isdir(f):
                _, ext = os.path.splitext(f)
                if ext == '.txt':
                    index_file(f, output_stream, db, stoplist)
            else:
                index_directory(f, output_stream)
    db.commit()
    disconnect_db(db)

def update_index():
    "Call a stored procedure in the database which will update the weight field "
    "for every entry in the Dictionary table"
    
    db = connect_db()
    cursor = db.cursor()
    procname = 'update_weight'
    cursor.callproc(procname)
    db.commit()
    cursor.close()
    disconnect_db(db)
