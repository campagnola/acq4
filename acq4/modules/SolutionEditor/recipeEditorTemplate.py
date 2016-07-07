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
        recipeEditor.resize(827, 441)
        self.gridLayout = QtGui.QGridLayout(recipeEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(recipeEditor)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.recipeTree = TreeWidget(self.splitter)
        self.recipeTree.setHeaderHidden(True)
        self.recipeTree.setObjectName(_fromUtf8("recipeTree"))
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        item_0 = QtGui.QTreeWidgetItem(self.recipeTree)
        self.textBrowser = QtGui.QTextBrowser(self.splitter)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(recipeEditor)
        QtCore.QMetaObject.connectSlotsByName(recipeEditor)

    def retranslateUi(self, recipeEditor):
        recipeEditor.setWindowTitle(_translate("recipeEditor", "Form", None))
        self.recipeTree.headerItem().setText(0, _translate("recipeEditor", "New Column", None))
        __sortingEnabled = self.recipeTree.isSortingEnabled()
        self.recipeTree.setSortingEnabled(False)
        self.recipeTree.topLevelItem(0).setText(0, _translate("recipeEditor", "Solution", None))
        self.recipeTree.topLevelItem(1).setText(0, _translate("recipeEditor", "Name", None))
        self.recipeTree.topLevelItem(2).setText(0, _translate("recipeEditor", "Volume", None))
        self.recipeTree.topLevelItem(3).setText(0, _translate("recipeEditor", "Show MW", None))
        self.recipeTree.topLevelItem(4).setText(0, _translate("recipeEditor", "Show concentration", None))
        self.recipeTree.topLevelItem(5).setText(0, _translate("recipeEditor", "Stocks (mM)", None))
        self.recipeTree.setSortingEnabled(__sortingEnabled)
        self.textBrowser.setHtml(_translate("recipeEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Oxygen-Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))

from acq4.pyqtgraph import TreeWidget
