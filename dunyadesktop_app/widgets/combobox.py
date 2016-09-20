from __future__ import absolute_import
from __future__ import print_function
import os

from PyQt4 import QtGui, QtCore

from .filteringdialog import FilteringDialog

CSS_PATH = os.path.join(os.path.dirname(__file__), '..', 'ui_files', 'css',
                        'combobox.css')


class ComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.setInsertPolicy(QtGui.QComboBox.NoInsert)

        self._set_css()

        self.cancel_button = QtGui.QToolButton(self)
        self.cancel_button.setStyleSheet('border: 0px; padding: 0px;')
        self.cancel_button.setIcon(QtGui.QIcon('/home/hsercanatli/Codes/dunya-desktop/dunyadesktop_app/ui_files/icons/cancel-music.svg'))

        self.dialog_filtering = FilteringDialog()
        self.dialog_filtering.table_attribute.doubleClicked.connect(
                                                            self.set_selection)
        self.dialog_filtering.ok_button_clicked.connect(
            lambda: self.set_selection(self.dialog_filtering.selection))
    def _set_css(self):
        with open(CSS_PATH) as f:
            css = f.read()
        self.setStyleSheet(css)

    def resizeEvent(self, QResizeEvent):
        button_size = self.cancel_button.sizeHint()
        frame_width = self.lineEdit().style().pixelMetric(
                                            QtGui.QStyle.PM_DefaultFrameWidth)
        self.cancel_button.move(self.rect().right()-9*frame_width-button_size.width(),
                         (self.rect().bottom()-button_size.height() + 1) / 2)
        super(ComboBox, self).resizeEvent(QResizeEvent)
        self.cancel_button.setVisible(False)

    def wheelEvent(self, QWheelEvent):
        pass

    def mousePressEvent(self, QMouseEvent):
        self.dialog_filtering.attribute = self.attribute
        self.dialog_filtering.setWindowTitle("")
        self.dialog_filtering.filtering_model.add_items(self.attribute)
        self.dialog_filtering.exec_()

    def set_placeholder_text(self, text):
        font = QtGui.QFont()
        font.setPointSize(10)

        self.lineEdit().setPlaceholderText(text)
        self.lineEdit().setFont(font)

    def add_items(self, attribute):
        self.attribute = attribute
        for att in self.attribute:
            self.addItem(att['name'])
        self.setCurrentIndex(-1)

    def get_attribute_id(self):
        index = self.currentIndex()
        if index is not -1:
            try:
                return self.attribute[index]['uuid']
            except:
                return self.attribute[index]['mbid']

        else:
            return ''

    def set_selection(self, index):
        try:
            index_row = index.row()
        except:
            index_row = index
        print(index_row)
        self.setCurrentIndex(index_row)
        self.lineEdit().setText(self.attribute[index_row]['name'])
