# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'recipeEditorTemplate.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_recipeEditor(object):
    def setupUi(self, recipeEditor):
        recipeEditor.setObjectName(_fromUtf8("recipeEditor"))
        recipeEditor.resize(619, 242)
        self.gridLayout = QtGui.QGridLayout(recipeEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.showMWCheck = QtGui.QCheckBox(recipeEditor)
        self.showMWCheck.setObjectName(_fromUtf8("showMWCheck"))
        self.horizontalLayout.addWidget(self.showMWCheck)
        self.showConcentrationCheck = QtGui.QCheckBox(recipeEditor)
        self.showConcentrationCheck.setObjectName(_fromUtf8("showConcentrationCheck"))
        self.horizontalLayout.addWidget(self.showConcentrationCheck)
        self.copyHtmlBtn = QtGui.QPushButton(recipeEditor)
        self.copyHtmlBtn.setObjectName(_fromUtf8("copyHtmlBtn"))
        self.horizontalLayout.addWidget(self.copyHtmlBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(recipeEditor)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.recipeSetList = QtGui.QListWidget(self.splitter)
        self.recipeSetList.setObjectName(_fromUtf8("recipeSetList"))
        self.recipeTable = QtGui.QTableWidget(self.splitter)
        self.recipeTable.setObjectName(_fromUtf8("recipeTable"))
        self.recipeTable.setColumnCount(0)
        self.recipeTable.setRowCount(0)
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)

        self.retranslateUi(recipeEditor)
        QtCore.QMetaObject.connectSlotsByName(recipeEditor)

    def retranslateUi(self, recipeEditor):
        recipeEditor.setWindowTitle(_translate("recipeEditor", "Form", None))
        self.showMWCheck.setText(_translate("recipeEditor", "Show molecular weights", None))
        self.showConcentrationCheck.setText(_translate("recipeEditor", "Show concentrations", None))
        self.copyHtmlBtn.setText(_translate("recipeEditor", "Copy HTML", None))

