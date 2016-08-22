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
        self.ui.splitter.setStretchFactor(0, 4)
        self.ui.splitter.setStretchFactor(1, 1)

        tree = self.ui.reagentTree
        tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.itemDelegate = ItemDelegate(tree)  # allow items to specify their own editors
        #tree.itemClicked.connect(self.itemClicked)
        tree.itemSelectionChanged.connect(self.selectionChanged)
        self.ui.reagentNotes.textChanged.connect(self.notesChanged)
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
            
        if isinstance(item, ReagentItem):
            self.ui.reagentNotes.setHtml(item.reagent['notes'])
        else:
            self.ui.reagentNotes.setHtml("")

    def notesChanged(self):
        items = self.ui.reagentTree.selectedItems()
        if len(items) == 0:
            return
        item = items[0]
        item.reagent['notes'] = unicode(self.ui.reagentNotes.toHtml())

    def addReagent(self, item):
        names = self.db.reagents.names()
        i = 0
        while True:
            name = 'new_reagent_%d' % i
            if name not in names:
                break
            i += 1
        self.db.reagents.add(name=name, group=item.text(0))
        self.updateReagentList()

    def updateReagentList(self):
        tree = self.ui.reagentTree
        vpos = tree.verticalScrollBar().value()
        hpos = tree.horizontalScrollBar().value()
        
        #items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
        #oldGroups = OrderedDict([(item.text(0), item) for item in items])
        #newGroups = self.reagents.groups()
        tree.clear()

        colNames = {
            'name': 'Reagent',
            'formula': 'Formula',
            'molweight': 'MW (g/mol)',
            'osmconst': 'Osmotic const.',
        }
        cols = [colNames.get(f[0], f[0]) for f in self.db.reagents._dtype if f[0] not in ('group', 'notes')]
        tree.setHeaderLabels(cols)
        
        grpItems = {}
        for reagent in self.reagents:
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
        fields = reagent.fields
        self.fields = OrderedDict([(f,fields[f]) for f in fields if f != 'group'])
        
        strs = [str(reagent[f]) for f in self.fields]
        QtGui.QTreeWidgetItem.__init__(self, strs)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable)

    def createEditor(self, parent, option, col):
        return QtGui.QLineEdit(parent)
    
    def setEditorData(self, editor, col):
        editor.setText(self.text(col))
    
    def setModelData(self, editor, model, col):
        fname, ftype = self.fields.items()[col]

        # string / float types need to be handled differently
        if ftype.kind in 'uif':
            v = float(editor.text())
            self.setText(col, '%0.2f'%v)
        else:
            v = str(editor.text())
            self.setText(col, v)
        self.reagent[fname] = v
        self.sigChanged.emit(self)

