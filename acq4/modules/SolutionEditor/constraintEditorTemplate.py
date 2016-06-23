# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'constraintEditorTemplate.ui'
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

class Ui_constraintEditor(object):
    def setupUi(self, constraintEditor):
        constraintEditor.setObjectName(_fromUtf8("constraintEditor"))
        constraintEditor.resize(788, 372)
        self.gridLayout = QtGui.QGridLayout(constraintEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.constraintTree = QtGui.QTreeWidget(constraintEditor)
        self.constraintTree.setObjectName(_fromUtf8("constraintTree"))
        item_0 = QtGui.QTreeWidgetItem(self.constraintTree)
        self.gridLayout.addWidget(self.constraintTree, 0, 0, 1, 1)

        self.retranslateUi(constraintEditor)
        QtCore.QMetaObject.connectSlotsByName(constraintEditor)

    def retranslateUi(self, constraintEditor):
        constraintEditor.setWindowTitle(_translate("constraintEditor", "constraintEditor", None))
        self.constraintTree.headerItem().setText(0, _translate("constraintEditor", "Property", None))
        self.constraintTree.headerItem().setText(1, _translate("constraintEditor", "Constraint", None))
        self.constraintTree.headerItem().setText(2, _translate("constraintEditor", "Value", None))
        __sortingEnabled = self.constraintTree.isSortingEnabled()
        self.constraintTree.setSortingEnabled(False)
        self.constraintTree.topLevelItem(0).setText(0, _translate("constraintEditor", "[K+]", None))
        self.constraintTree.topLevelItem(0).setText(1, _translate("constraintEditor", "Range", None))
        self.constraintTree.topLevelItem(0).setText(2, _translate("constraintEditor", "2.5 <= x <= 3", None))
        self.constraintTree.setSortingEnabled(__sortingEnabled)

