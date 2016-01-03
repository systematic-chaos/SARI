#! /usr/bin/python

 #############################################################################
 # Almacenamiento y Recuperacion de la Informacion - Proyecto de laboratorio #
 # Fco. Javier Fernandez-Bravo Penuela                                       #
 # Escuela Superior de Informatica - UCLM                                    #
 # Archivo: ari.py                                                           #
 #############################################################################

from Tkinter import *
from TkTreectrl import MultiListbox
import tkMessageBox
import tkFileDialog
import threading
import os.path
import index
import question
import feedback
from structs import *

class Ari:

    class ConcurrentIndex(threading.Thread):
        "Class that starts a new execution thread to carry out the operation "
        "of indexing a list of files of directories without blocking the "
        "Tkinter GUI, so it will be able to be updated as the process goes on"

        def __init__(self, output_stream, files = None, directory = None):
            threading.Thread.__init__(self)
            self.output_stream = output_stream
            self.files = files
            self.directory = directory

        def run(self):
            if self.files is not None or self.directory is not None:
                if self.directory is not None:
                    index.index_directory(self.directory, self.output_stream)
                elif self.files is not None:
                    for f in self.files:
                        index.index_file(path = f,
                                            output_stream = self.output_stream)
                index.update_index()
                tkMessageBox.showinfo('Indexacion completada!!!',
                'Indexacion completada! Puede cerrar la ventana de indexacion')

    class ConcurrentSearch(threading.Thread):
        "Class that starts a new execution thread to carry out the operation "
        "of searching the files relevant to a question (provided by the user "
        "or by another file's document vector) without blocking the Tkinter "
        "GUI, so it will be able to be updated as the process goes on"

        def __init__(self, algorithm, results_output, output_stream,
                        question = None, id_doc = None):
            threading.Thread.__init__(self)
            self.algorithm = algorithm
            self.results_output = results_output
            self.output_stream = output_stream
            self.question = question
            self.id_doc = id_doc

        def run(self):
            if self.question is not None or self.id_doc is not None:
                if self.question is not None:
                    self.search_result = question.search_string(self.algorithm,
                                            self.question, self.output_stream)
                elif self.id_doc is not None:
                    self.search_result = feedback.search_similar_docs(self.algorithm,
                                                            self.id_doc,
                                                            self.output_stream)

                for result in self.search_result:
                    self.results_output.insert(END, result.n, result.doc.id,
                                                result.doc.title,
                                                result.relevance,
                                                result.doc.text)
                self.results_output.pack(side = LEFT, fill = BOTH, expand = 1,
                                            padx = 10)


    def index_data(cls, file = None, dir = None):
        "Create a new instance of the ConcurrentIndex class and start the "
        "index process of the files/directory provided. The contents of the "
        "sv variable will be displayed on the message_index widget, and "
        "updated by the thread responsible for carrying out the index operation"

        if file is not None or dir is not None:
            window_index = Toplevel(cls.top, width = 200)
            window_index.title('Indexando...')
            window_index.wm_iconbitmap(bitmap = '@python.xbm')

            sv = StringVar()
            message_index = Message(window_index, textvariable = sv,
                                    aspect = 800)
            message_index.pack(side = LEFT, fill = BOTH, expand = 1)

            t_index = cls.ConcurrentIndex(sv, file, dir)
            t_index.start()

    def index_files(cls, event = None):
        "Show a dialog allowing the user to select multiple files and command "
        "the index process of the files selected to start"

        cls.results_listbox.pack_forget()
        cls.similar_button.pack_forget()
        files = tkFileDialog.askopenfilenames(filetypes = [('text files', '.txt')],
            initialdir = os.path.expanduser('~'), parent = cls.top,
            title = 'Indexar archivos')
        if len(files) > 0:
            cls.index_data(file = files)

    def index_directory(cls, event = None):
        "Show a dialog allowing the user to select a directory and command the "
        "index process of the files (recursively) contained in the selected "
        "directory to start"

        cls.results_listbox.pack_forget()
        cls.similar_button.pack_forget()
        directory = tkFileDialog.askdirectory(initialdir = os.path.expanduser('~'),
                parent = cls.top, title = 'Indexar directorio',
                mustexist = True)
        if len(directory) > 0:
            cls.index_data(dir = directory)


    def search(cls, event = None):
        "Search the text in the search_entry widget by creating a new instance "
        "of the ConcurrentSearch class (after validating it by means of the "
        "validate_question function in the question module), and depict the "
        "results obtained in the results_listbox widget "
        "The contents of the sv variable will be displayed on the "
        "message_index widget, and updated by the thread responsible for "
        "carrying out the index operation"
        
        input = cls.search_entry.get()
        cls.results_listbox.delete(0, END)
        if question.validate_question_string(input):
            cls.similar_button.pack(side = RIGHT, pady = 10)
            window_index = Toplevel(cls.top, width = 200)
            window_index.title('Buscando...')
            window_index.wm_iconbitmap(bitmap = '@python.xbm')

            sv = StringVar()
            message_index = Message(window_index, textvariable = sv,
                                    aspect = 800)
            message_index.pack(side = LEFT, fill = BOTH, expand = 1)

            t_search = cls.ConcurrentSearch(output_stream = sv,
                                        results_output = cls.results_listbox,
                                        algorithm = cls.algorithm.get(),
                                        question = input)
            t_search.start()

        else:
            tkMessageBox.showwarning('Entrada no valida',
                'La pregunta realizada debe cumplir con el formato: (termino peso?)+\n')

    def similar_docs(cls, event = None):
        "Look for documents similar to the one selected in the results_listbox "
        "widget, and show the results on it"
        if len(cls.results_listbox.curselection()) != 1:
            return
        id_doc = cls.results_listbox.get(cls.results_listbox.curselection()[0])[0][1]
        cls.results_listbox.delete(0, END)
        window_index = Toplevel(cls.top, width = 200)
        window_index.title('Buscando...')
        window_index.wm_iconbitmap(bitmap = '@python.xbm')

        sv = StringVar()
        message_index = Message(window_index, textvariable = sv, aspect = 800)
        message_index.pack(side = LEFT, fill = BOTH, expand = 1)

        t_search = cls.ConcurrentSearch(output_stream = sv,
                                        results_output = cls.results_listbox,
                                        algorithm = cls.algorithm.get(),
                                        id_doc = id_doc)
        t_search.start()
    
    def display_doc(cls, event):
        "Create a new window which will contain a Text widget to display the "
        "contents of the file currently selected in the results_listbox widget"

        if len(cls.results_listbox.curselection()) != 1:
            return
        title = cls.results_listbox.get(cls.results_listbox.curselection()[0])[0][4]
        window_text = Toplevel(cls.top)
        window_text.title(title)
        window_text.wm_iconbitmap(bitmap = '@python.xbm')

        text_scrollbar = Scrollbar(window_text, orient = VERTICAL)
        text_scrollbar.pack(side = RIGHT, fill = Y)
        text_doc = Text(window_text, wrap = WORD,
                        yscrollcommand = text_scrollbar.set)

        text_doc = Text(window_text)
        doc = open(title, 'r')
        for line in doc:
            text_doc.insert(INSERT, line)
        doc.close()
        text_doc.config(state = DISABLED)
        text_doc.pack(side = LEFT, fill = BOTH, expand = 1)
        text_scrollbar.config(command = text_doc.yview)

    def __init__(self, master):
        "Initialization and configuration of the visual components in the "
        "system's GUI"

        # Root (master) top window
        self.top = master
        master.title('SARI')
        master.wm_iconbitmap(bitmap = '@python.xbm')

        master.configure(background = 'white', width = 1000, height = 800)

        # Title label
        pi_title = PhotoImage(file = 'sari.gif')
        self.label_title = Label(master, name = '_label_title',
                                    image = pi_title, width = 800,
                                    background = 'white')
        self.label_title.photo = pi_title
        self.label_title.pack(pady = 20)

        # Text search entry
        self.search_entry = Entry(master, width = 60, relief = GROOVE)
        self.search_entry.configure(font = (self.search_entry.cget('font')[0],
                                            10), highlightcolor = 'blue')
        self.search_entry.bind('<Return>', self.search)
        self.search_entry.pack()
        self.search_entry.focus()

        # Search button
        self.search_button = Button(master, text = 'Buscar!',
                                command = self.search, padx = 20)
        self.search_button.bind('<Return>', self.search)
        self.search_button.pack(pady = 10)

        # Information retrieval algorithm option menu
        self.algorithm = StringVar(master)
        self.algorithm.set(question.ComputeSimilarity.list()[0])
        algs = question.ComputeSimilarity.list()
        self.algorithm_option = OptionMenu(master, self.algorithm,
                                        algs[0], algs[1], algs[2], algs[3])
        self.algorithm_option.pack(pady = 10)

        # Index files button
        self.index_files_button = Button(master, text = 'Indexar archivos',
                                        padx = 20, command = self.index_files)
        self.index_files_button.bind('<Return>', self.index_files)
        self.index_files_button.pack(pady = 10)

        # Index directory button
        self.index_dir_button = Button(master, text = 'Indexar directorio',
                                    padx = 20,
                                    command = self.index_directory)
        self.index_dir_button.bind('<Return>', self.index_directory)
        self.index_dir_button.pack(pady = 10)

        # Results listbox and scrollbar
        result_scrollbar = Scrollbar(master, orient = VERTICAL)
        self.results_listbox = MultiListbox(master, selectmode = SINGLE,
                                        yscrollcommand = result_scrollbar.set)
        self.results_listbox.configure(command = self.display_doc,
                                        columns = ('No', 'Id', 'Titulo',
                                                    'Relevancia', 'Documento'),
                                        selectbackground='gray',
                                        selectforeground='black')
        result_scrollbar.config(command = self.results_listbox.yview,
                                relief = FLAT, activerelief = FLAT)
        result_scrollbar.pack(side = RIGHT, fill = Y)

        # Search similar documents button
        self.similar_button = Button(master,
                                    text = 'Buscar documentos similares',
                                    padx = 20,
                                    command = self.similar_docs)
        self.similar_button.bind('<Return>', self.similar_docs)

# Initialization of the Tkinter environment and the System for Information 
# Storage and Retrieval. Start of the Tkinter main loop

root = Tk()

sari = Ari(root)

root.mainloop()
