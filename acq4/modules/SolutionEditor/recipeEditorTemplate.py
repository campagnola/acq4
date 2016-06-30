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
        self.treeWidget_2 = QtGui.QTreeWidget(self.splitter)
        self.treeWidget_2.setObjectName(_fromUtf8("treeWidget_2"))
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget_2)
        self.textBrowser = QtGui.QTextBrowser(self.splitter)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(recipeEditor)
        QtCore.QMetaObject.connectSlotsByName(recipeEditor)

    def retranslateUi(self, recipeEditor):
        recipeEditor.setWindowTitle(_translate("recipeEditor", "Form", None))
        self.treeWidget_2.headerItem().setText(0, _translate("recipeEditor", "New Column", None))
        __sortingEnabled = self.treeWidget_2.isSortingEnabled()
        self.treeWidget_2.setSortingEnabled(False)
        self.treeWidget_2.topLevelItem(0).setText(0, _translate("recipeEditor", "Solution", None))
        self.treeWidget_2.topLevelItem(1).setText(0, _translate("recipeEditor", "Name", None))
        self.treeWidget_2.topLevelItem(2).setText(0, _translate("recipeEditor", "Volume", None))
        self.treeWidget_2.topLevelItem(3).setText(0, _translate("recipeEditor", "Show MW", None))
        self.treeWidget_2.topLevelItem(4).setText(0, _translate("recipeEditor", "Show concentration", None))
        self.treeWidget_2.topLevelItem(5).setText(0, _translate("recipeEditor", "Stocks (mM)", None))
        self.treeWidget_2.setSortingEnabled(__sortingEnabled)
        self.textBrowser.setHtml(_translate("recipeEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Oxygen-Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))

