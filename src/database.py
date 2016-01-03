 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: database.py                                                      #
 #############################################################################

import mysql.connector

def connect_db():
    "Connect to the MySQL database via the predetermined parameters. "
    "Return the opened connection"

    return mysql.connector.connect(user = 'thanatos', password = 'bushido',
                                    host = 'localhost', database = 'ari')

def disconnect_db(db):
    "Close a previously opened connection to the database"

    db.close()
    