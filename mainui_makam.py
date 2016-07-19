#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from ui_files.makam_main_design import Ui_MainWindow
from PyQt4 import QtCore, QtGui

import compmusic.dunya.makam
import time
import os

from ipyparallel import Client

from threading import Thread
from utilities import utilities
from multiprocessing import cpu_count

#from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool
#from multiprocessing.pool import ThreadPool
#from multiprocessing.dummy import Pool

# setting the token
compmusic.dunya.conn.set_token('***REMOVED***')

# gazel and taksim uuids
GAZEL = u'a1d59289-ea72-4050-9253-01ca12bb5556'
TAKSIM = u'b4658cef-f3cd-4ced-a534-1dd0a0d5b2de'


class MainMakam(QtGui.QMainWindow, Ui_MainWindow):
    query_finished = QtCore.pyqtSignal()
    query_step_done = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        # setting the interface
        super(MainMakam, self).__init__(parent)
        # setting the qt-designer design
        self.setupUi(self)

        # title of the window
        self.setWindowTitle('CompMusic')

        # proxy modal
        self.proxy_model = QtGui.QSortFilterProxyModel()

        # setting the table for no edit and row selection
        self.tableView_results.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableView_results.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # creating the table model
        # setting the column and row
        self.recording_model = QtGui.QStandardItemModel()
        self.recording_model.setHorizontalHeaderLabels(['Title', 'Artists'])

        # progress bar
        self.progress_bar = QtGui.QProgressBar()
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.setGeometry(30, 40, 200, 25)

        # fetching makam,usul and form data from dunya
        self.makams = compmusic.dunya.makam.get_makams()
        self.makams = utilities.sort_dictionary(self.makams, 'name')

        self.usuls = compmusic.dunya.makam.get_usuls()
        self.usuls = utilities.sort_dictionary(self.usuls, 'name')

        self.forms = compmusic.dunya.makam.get_forms()
        self.forms = utilities.sort_dictionary(self.forms, 'name')

        # setting the combobox
        self.comboBox_makam = utilities.set_combobox(self.comboBox_makam, self.makams)
        self.comboBox_form = utilities.set_combobox(self.comboBox_form, self.forms)
        self.comboBox_usul = utilities.set_combobox(self.comboBox_usul, self.usuls)

        # query index for progress bar
        self.query_index = 0
        self.query_step_done.connect(self.update_progress_query)

        # setting filter line editer disabled in the beginning
        self.lineEdit_filter.setDisabled(True)

        # signals
        # buttons
        self.toolButton_query.clicked.connect(self.query_thread)
        self.query_finished.connect(self.add_model_to_table)

        # line edit
        self.lineEdit_filter.textChanged.connect(self.filtering_the_table)

    def update_progress_query(self):
        progress = (float(self.query_index) / len(self.work_list)) * 100
        self.progress_bar.setValue(progress)

    def add_model_to_table(self):
        print "Query FINISHED"
        self.tableView_results.setEnabled(True)
        # setting the model
        self.proxy_model.setSourceModel(self.recording_model)
        print "proxy set"

        # filtering affects all columns by setting it as -1
        self.proxy_model.setFilterKeyColumn(-1)
        print "proxy filter"

        # setting the proxy model to the table
        self.tableView_results.setModel(self.proxy_model)
        print "proxy model set"

        # filter line edit is enabled
        self.lineEdit_filter.setEnabled(True)

        # hiding the vertical headers
        self.tableView_results.verticalHeader().hide()

        # arranging the artist column for being multi-line
        self.tableView_results.setWordWrap(True)
        self.tableView_results.setTextElideMode(QtCore.Qt.ElideMiddle)

        # setting the widths of rows and columns
        self.tableView_results.horizontalHeader().setStretchLastSection(True)
        self.tableView_results.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tableView_results.resizeColumnToContents(0)
        self.tableView_results.resizeRowsToContents()

        self.query_index = 0

    def query_thread(self):
        query_thread = Thread(target=self.do_query)
        query_thread.start()

    def download_audio_thread(self):
        thread = Thread(target=self.download_audio)
        thread.start()

    def download_audio(self):
        if not os.path.isdir("audio"):
            os.makedirs("audio")

        for xx, rec in enumerate(self.recording_list):
            print xx, rec['title']
            progress = (float(xx + 1) / len(self.recording_list)) * 100
            print progress
            self.progress_bar.setValue(progress)

            compmusic.dunya.makam.download_mp3(rec['mbid'], "audio")

    def filtering_the_table(self):
        """Insensitive case filter"""
        # setting the case
        reg_exp = QtCore.QRegExp(self.lineEdit_filter.text(), QtCore.Qt.CaseInsensitive)

        self.proxy_model.setFilterRegExp(reg_exp)

    def do_query(self):
        self.tableView_results.setDisabled(True)
        # setting the push button disable
        self.toolButton_query.setDisabled(True)

        # getting the user selections
        makam_id = utilities.get_attribute_id(self.makams, self.comboBox_makam.currentIndex())
        form_id = utilities.get_attribute_id(self.forms, self.comboBox_form.currentIndex())
        usul_id = utilities.get_attribute_id(self.usuls, self.comboBox_usul.currentIndex())

        # arranging the recordings and works for the filtering process
        length_recording_taksims = []
        length_recording_gazels = []
        length_works = []

        # if makam is selected
        if makam_id != -1:
            data = compmusic.dunya.makam.get_makam(makam_id)
            length_works.append([data['works'], len(data['works'])])

            # merging the recordings
            length_recording_taksims.append([data['taksims'], len(data['taksims'])])
            length_recording_gazels.append([data['gazels'], len(data['gazels'])])

        # if usul is selected
        if usul_id != -1:
            data = compmusic.dunya.makam.get_usul(usul_id)
            length_works.append([data['works'], len(data['works'])])

            # merging the recordings
            length_recording_taksims.append([data['taksims'], len(data['taksims'])])
            length_recording_gazels.append([data['gazels'], len(data['gazels'])])

        # if form is selected
        if form_id != -1:
            # TODO: add only taksim or gazel selection
            data = compmusic.dunya.makam.get_form(form_id)
            length_works.append([data['works'], len(data['works'])])

        # sorting the lengths
        length_works = sorted(length_works, key=lambda x: x[1])[::-1]
        length_recording_gazels = sorted(length_recording_gazels, key=lambda x: x[1])[::-1]
        length_recording_taksims = sorted(length_recording_taksims, key=lambda x: x[1])[::-1]

        # filtering
        recording_list = []
        # if all attributes are selected by the user
        if len(length_works) == 3:
            work_list = [common for common in
                         [common for common in length_works[0][0] if common in length_works[1][0]]
                         if common in length_works[2][0]]

            if form_id == TAKSIM:
                recording_list = [common for common in [common for common in length_recording_taksims[0][0]
                                                        if common in length_recording_taksims[1][0]]
                                  if common in length_recording_taksims[2][0]]
            elif form_id == GAZEL:
                recording_list = [common for common in [common for common in length_recording_gazels[0][0]
                                                        if common in length_recording_gazels[1][0]]
                                  if common in length_recording_gazels[2][0]]

        elif len(length_works) == 2:
            work_list = [common for common in length_works[0][0] if common in length_works[1][0]]

            if form_id == -1:
                recording_list = length_recording_taksims[0][0] + length_recording_gazels[0][0]
            elif form_id == TAKSIM:
                recording_list = length_recording_taksims[0][0]
            elif form_id == GAZEL:
                recording_list = length_recording_gazels[0][0]
        else:
            # if form is not selected
            if form_id == -1:
                work_list = length_works[0][0]
                recording_list = length_recording_gazels[0][0] + length_recording_taksims[0][0]

            elif form_id != -1:
                if form_id != GAZEL or form_id != TAKSIM:
                    work_list = length_works[0][0]
                    #recording_list = length_recording_gazels[0][0] + length_recording_taksims[0][0]
                else:
                    # TODO: Add only taksim or gazel selection
                    work_list = length_works[0][0]

        # recording list
        self.recording_list = recording_list
        self.work_list = work_list

        self.set_table(work_list)

        # enabling the query button
        self.toolButton_query.setEnabled(True)

    def set_table(self, score_list):
        #for element in score_list:
        #    work_data = compmusic.dunya.makam.get_work(element['mbid'])
        #    for rec in work_data['recordings']:
        #        self.recording_list.append(rec)

        # creating a pool for multi-processing
        pool = Pool(cpu_count()-1)

        for element in score_list:
            pool.apply_async(self.adding_items_to_table, (element,))
        pool.close()
        # starting the multi-processing
        print "pool closed"
        pool.join()
        print "pool finished"
        # sorting the recording dictionary
        self.recording_list = utilities.sort_dictionary(self.recording_list, 'title')
        # arranging the rows of the model
        self.recording_model.setRowCount(len(self.recording_list))

        print "row count is set "
        # adding items to the model
        for row, item in enumerate(self.recording_list):
            print row, len(self.recording_list)
            # creating an item
            title_item = QtGui.QStandardItem(item['title'])

            # setting the created item checkable
            title_item.setCheckable(True)
            title_item.setCheckState(QtCore.Qt.Checked)

            # creating an item for artists column.
            artists = ''
            # appending all artists in the same item
            for artist in item['artists']:
                artists += artist['name'] + ", "

            artist_item = QtGui.QStandardItem(artists)

            # setting the items in to the model
            self.recording_model.setItem(row, 0, title_item)
            self.recording_model.setItem(row, 1, artist_item)

        print "for loop is finished"
        thread = Thread(target=self.query_finished.emit)
        print "ready to emit"
        thread.start()
        print "emitted"
        #self.query_finished.emit()

    def adding_items_to_table(self, element):
        """This function is used for the multiprocess"""
        try:
            work_data = compmusic.dunya.makam.get_work(element['mbid'])
            for xx, rec in enumerate(work_data['recordings']):
                self.recording_list.append(rec)

        except:
            print('error with item')
        self.query_index += 1
        self.query_step_done.emit()

app = QtGui.QApplication(sys.argv)
dialog = MainMakam()
dialog.show()
app.exec_()
