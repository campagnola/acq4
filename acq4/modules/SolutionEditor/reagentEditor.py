from collections import OrderedDict
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .treeWidget import GroupItem
from .reagentEditorTemplate import Ui_reagentEditor


class ReagentEditorWidget(QtGui.QWidget):
    def __init__(self, reagents, parent=None):
        self.reagents = reagents
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_reagentEditor()
        self.ui.setupUi(self)
        self.updateReagentList()
        
    def updateReagentList(self):
        tree = self.ui.reagentTree
        items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
        oldGroups = OrderedDict([(item.text(0), item) for item in items])
        newGroups = self.reagents.groups()
        tree.clear()
        grpItems = {}
        for reagent in self.reagents.data:
            strs = [str(reagent[f[0]]) for f in self.reagents._dtype if f[0] != 'group']
            item = QtGui.QTreeWidgetItem(strs)
            item.setFlags(QtCore.Qt.ItemIsEditable)
            group = reagent['group']
            if group not in grpItems:
                grpItems[group] = GroupItem(group, adder='add reagent')
                tree.addTopLevelItem(grpItems[group])
            grpItem = grpItems[group]
            grpItem.addChild(item)

        for i in range(self.ui.reagentTree.columnCount()):
            self.ui.reagentTree.resizeColumnToContents(i)


