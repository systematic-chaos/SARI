 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: structs.py                                                       #
 #############################################################################

from collections import namedtuple

# Data types for the System for Information Storage and Retrieval

Document = namedtuple('Document', 'id, title, text')
Term = namedtuple('Term', 'term, weight')
Post = namedtuple('Post', 'id, term, weight')
Question = namedtuple('Question', 'term, weight')
Result = namedtuple('Result', 'n, doc, relevance')
