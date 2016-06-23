# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reagentEditorTemplate.ui'
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

class Ui_reagentEditor(object):
    def setupUi(self, reagentEditor):
        reagentEditor.setObjectName(_fromUtf8("reagentEditor"))
        reagentEditor.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(reagentEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.reagentTree = TreeWidget(reagentEditor)
        self.reagentTree.setAlternatingRowColors(True)
        self.reagentTree.setObjectName(_fromUtf8("reagentTree"))
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        item_0 = QtGui.QTreeWidgetItem(self.reagentTree)
        self.gridLayout.addWidget(self.reagentTree, 0, 0, 1, 1)

        self.retranslateUi(reagentEditor)
        QtCore.QMetaObject.connectSlotsByName(reagentEditor)

    def retranslateUi(self, reagentEditor):
        reagentEditor.setWindowTitle(_translate("reagentEditor", "Form", None))
        self.reagentTree.headerItem().setText(0, _translate("reagentEditor", "Reagent", None))
        self.reagentTree.headerItem().setText(1, _translate("reagentEditor", "Formula", None))
        self.reagentTree.headerItem().setText(2, _translate("reagentEditor", "MW (g/mol)", None))
        self.reagentTree.headerItem().setText(3, _translate("reagentEditor", "Osmolarity (mOsm)", None))
        self.reagentTree.headerItem().setText(4, _translate("reagentEditor", "Cost (per g)", None))
        self.reagentTree.headerItem().setText(5, _translate("reagentEditor", "Na", None))
        self.reagentTree.headerItem().setText(6, _translate("reagentEditor", "K", None))
        self.reagentTree.headerItem().setText(7, _translate("reagentEditor", "Cl", None))
        self.reagentTree.headerItem().setText(8, _translate("reagentEditor", "Ca", None))
        self.reagentTree.headerItem().setText(9, _translate("reagentEditor", "Mg", None))
        self.reagentTree.headerItem().setText(10, _translate("reagentEditor", "SO4", None))
        self.reagentTree.headerItem().setText(11, _translate("reagentEditor", "PO4", None))
        self.reagentTree.headerItem().setText(12, _translate("reagentEditor", "Cs", None))
        __sortingEnabled = self.reagentTree.isSortingEnabled()
        self.reagentTree.setSortingEnabled(False)
        self.reagentTree.topLevelItem(0).setText(0, _translate("reagentEditor", "Ions", None))
        self.reagentTree.topLevelItem(1).setText(0, _translate("reagentEditor", "pH Buffers", None))
        self.reagentTree.topLevelItem(2).setText(0, _translate("reagentEditor", "Metabolites", None))
        self.reagentTree.topLevelItem(3).setText(0, _translate("reagentEditor", "Antioxidants", None))
        self.reagentTree.topLevelItem(4).setText(0, _translate("reagentEditor", "Toxins", None))
        self.reagentTree.topLevelItem(5).setText(0, _translate("reagentEditor", "Markers", None))
        self.reagentTree.setSortingEnabled(__sortingEnabled)

from acq4.pyqtgraph import TreeWidget
