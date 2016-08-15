from collections import OrderedDict
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .treeWidget import GroupItem, ItemDelegate
from .reagentEditorTemplate import Ui_reagentEditor


class ReagentEditorWidget(QtGui.QWidget):
    def __init__(self, db, parent=None):
        self.db = db
        self.reagents = db.reagents
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_reagentEditor()
        self.ui.setupUi(self)

        tree = self.ui.reagentTree
        tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.itemDelegate = ItemDelegate(tree)  # allow items to specify their own editors
        #tree.itemClicked.connect(self.itemClicked)
        tree.itemSelectionChanged.connect(self.selectionChanged)

        self.updateReagentList()
        
    #def itemClicked(self, item, col):
        #print "item clicked"
        #if hasattr(item, 'itemClicked'):
            #item.itemClicked(col)
        
    def selectionChanged(self):
        tree = self.ui.reagentTree
        selection = tree.selectionModel().selection().indexes()
        if len(selection) != 1:
            return
        item, col = tree.itemFromIndex(selection[0])
        if item.flags() & QtCore.Qt.ItemIsEditable == QtCore.Qt.ItemIsEditable:
            tree.editItem(item, col)

    def addReagent(self, *args):
        print args

    def updateReagentList(self):
        tree = self.ui.reagentTree
        vpos = tree.verticalScrollBar().value()
        hpos = tree.horizontalScrollBar().value()
        
        items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
        oldGroups = OrderedDict([(item.text(0), item) for item in items])
        newGroups = self.reagents.groups()
        tree.clear()
        grpItems = {}
        for reagent in self.reagents.data:
            item = ReagentItem(reagent)
            group = reagent['group']
            if group not in grpItems:
                grpItems[group] = GroupItem(group, adder='add reagent')
                tree.addTopLevelItem(grpItems[group])
                tree.setFirstItemColumnSpanned(grpItems[group], True)
                grpItems[group].sigAddClicked.connect(self.addReagent)
            grpItem = grpItems[group]
            grpItem.addChild(item)

        for i in range(self.ui.reagentTree.columnCount()):
            self.ui.reagentTree.resizeColumnToContents(i)

        tree.verticalScrollBar().setValue(vpos)
        tree.horizontalScrollBar().setValue(hpos)


class ReagentItem(QtGui.QTreeWidgetItem):
    def __init__(self, reagent):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        self.reagent = reagent
        strs = [str(reagent[f]) for f in reagent.dtype.names if f != 'group']
        self.fields = strs
        QtGui.QTreeWidgetItem.__init__(self, strs)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable)

    def createEditor(self, parent, option, col):
        if col == 0:
            return None
        return QtGui.QLineEdit(parent)
    
    def setEditorData(self, editor, col):
        editor.setText(self.text(col))
    
    def setModelData(self, editor, model, col):
        t = editor.text()
        self.setText(col, editor.text())
        field = self.fields[col]
        self.reagent
        self.sigChanged.emit(self)

