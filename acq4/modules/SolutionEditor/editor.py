from collections import OrderedDict
import numpy as np
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .reagentEditorTemplate import Ui_reagentEditor
from .solutionEditorTemplate import Ui_solutionEditor
from .recipeEditorTemplate import Ui_recipeEditor
from .constraintEditorTemplate import Ui_constraintEditor


IONS = ['Na', 'K', 'Cl', 'Ca', 'Mg', 'SO4', 'PO4', 'Cs']


class Reagents(object):
    def __init__(self):
        self._dtype = [
            ('group', object),
            ('name', object),
            ('formula', object),
            ('molweight', float),
            ('osmolarity', float),
            ('cost', float),
        ] + [(ion, float) for ion in IONS] + [('notes', object)]
        self._null = (None, None, None, 0, 0, 0) + (0,)*len(IONS) + (None,)
        self.data = np.empty(0, dtype=self._dtype)

    def add(self, **kwds):
        assert kwds['name'] not in self.data['name'], 'Reagent with this name already exists.'
        self.data = np.resize(self.data, len(self.data)+1)
        self.data[-1] = self._null
        #if 'ions' in kwds:
            #for k,v in kwds.pop('ions').items():
                #self.data[-1]['ions'][k] = v
        for k,v in kwds.items():
            self.data[-1][k] = v

    def remove(self, name):
        try:
            i = np.argwhere(self.data['name'] == name)[0, 0]
        except IndexError:
            raise KeyError('No reagent named "%s"' % name)
        mask = np.ones(len(self.data), dtype=bool)
        mask[i] = False
        self.data = self.data[mask]

    def save(self):
        return _saveArray(self.data)
    
    def restore(self, data):
        self.data = _loadArray(data)

    def groups(self):
        return np.unique(self.data['group'])

    def __getitem__(self, names):
        inds = []
        for n in names:
            r = np.argwhere(self.data['name'] == n)[:,0]
            if r.shape[0] == 0:
                continue
            inds.append(r[0])
        return self.data[inds]


class Solutions(object):
    def __init__(self, reagents):
        self.reagents = reagents
        self.data = []
        self.groups = []

    def add(self, name, group):
        for s in self.data:
            if s.name == name:
                raise NameError("Solution with this name already exists.")
        self.data.append(Solution(name, group))
        return self.data[-1]
    
    def restore(self, data):
        self.data = []
        for d in data:
            sol = self.add(d['name'], d['group'])
            sol.restore(d['reagents'])

    def save(self):
        state = []
        for sol in self.data:
            state.append({'name': sol.name, 'group': sol.group, 'reagents': sol.reagents})
        return state

    
class Solution(object):
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.type = 'internal' if 'internal' in group.lower() else 'external'
        self.compareAgainst = None
        self.reagents = {}
        
        # empirically determined values:
        self.ionConcentrations = {}
        self.osmolarity = None
        
    def __setitem__(self, name, concentration):
        """Set the concentration of a particular reagent.
        """
        if concentration in (0,  None):
            self.reagents.pop(name, None)
        else:
            self.reagents[name] = concentration
        
    def ___getitem__(self, name):
        """Return the concentration of a reagent.
        """
        return self.reagents[name]
    
    def restore(self, reagents):
        self.reagents.clear()
        self.reagents.update(reagents)
    
    
def _saveArray(data):
    return [_recToDict(rec) for rec in data]
    
def _recToDict(rec):
    od = OrderedDict()
    for field in rec.dtype.names:
        if rec.dtype.fields[field][0].names is None:
            od[field] = rec[field]
        else:
            od[field] = _recToDict(rec[field])
    return od
    

def _loadArray(data, dtype):
    arr = np.empty(len(data), dtype=dtype)
    for i,rec in enumerate(data):
        _loadRec(arr[i], rec)
        
def _loadRec(arr, rec):
    for field in arr.dtype.names:
        if arr.dtype.fields[field][0].names is None:
            arr[field] = rec[field]
        else:
            _loadRec(arr[field], rec[field])
        



class ReagentEditorWidget(QtGui.QWidget):
    def __init__(self, reagents, parent=None):
        self.reagents = reagents
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_reagentEditor()
        self.ui.setupUi(self)
        
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


class SolutionEditorWidget(QtGui.QWidget):
    def __init__(self, solutions, parent=None):
        self.solutions = solutions
        self.selectedSolutions = []
        self.showAllReagents = False
        
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_solutionEditor()
        self.ui.setupUi(self)
        
        self.ui.solutionList.setEditTriggers(QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked)

        self.addGroupItem = HtmlItem('+ <a href="/">add group</a>')
        self.ui.solutionList.addTopLevelItem(self.addGroupItem)
        self.addGroupItem.label.linkActivated.connect(self.addGroup)
        
        self.ui.solutionTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.solnTableDelegate = ItemDelegate(self.ui.solutionTable)  # allow items to specify their own editors
        self.ui.solutionTable.setHeaderLabels([''])
        #self.ui.solutionTable.setUniformRowHeights(True)
        self.ui.solutionTable.clear()
        self.solnTreeItems = {}

        item = GroupItem('Concentrations (mM)', adder='show all reagents')
        self.solnTreeItems[str(item.text(0))] = item
        self.ui.solutionTable.addTopLevelItem(item)
        item.sigAddClicked.connect(self.showReagentsClicked)
        
        names = [
            'Ion Concentrations (estimated)',
            'Ion Concentrations (measured)',
            'Osmolarity (estimated)',
            'Osmolarity (measured)',
            'Reversal Potentials',
        ]
        for name in names:
            item = GroupItem(name)
            self.solnTreeItems[name] = item
            self.ui.solutionTable.addTopLevelItem(item)
            
        self.solutionTypeItem = SolutionTypeItem()
        self.solnTreeItems['Reversal Potentials'].addChild(self.solutionTypeItem)
        
        self.estIonConcItems = {}
        self.measIonConcItems = {}
        self.ionReversalItems = {}
        for ion in IONS:
            item = QtGui.QTreeWidgetItem([ion])
            self.solnTreeItems['Ion Concentrations (estimated)'].addChild(item)
            self.estIonConcItems[ion] = item
            item = QtGui.QTreeWidgetItem([ion])
            self.solnTreeItems['Ion Concentrations (measured)'].addChild(item)
            self.measIonConcItems[ion] = item
            item = QtGui.QTreeWidgetItem([ion])
            self.solnTreeItems['Reversal Potentials'].addChild(item)
            self.ionReversalItems[ion] = item

        self.ui.splitter_2.setStretchFactor(0, 1)
        self.ui.splitter_2.setStretchFactor(1, 3)
        self.ui.splitter.setStretchFactor(0, 2)
        self.ui.splitter.setStretchFactor(1, 1)
        self.ui.solutionList.sigItemTextChanged.connect(self.solutionListTextChanged)
        self.ui.solutionList.sigItemCheckStateChanged.connect(self.solutionListCheckStateChanged)
        self.ui.reverseTempSpin.valueChanged.connect(self.updateSolutionTree)

        self.ui.solutionTable.itemSelectionChanged.connect(self.selectionChanged)

    #def updateReagentList(self):
        #rlist = []
        #groups = OrderedDict()
        #for r in self.solutions.reagents.data:
            #groups.setdefault(r['group'], [])
            #groups[r['group']].append(r['name'])
        #for grp, reagents in groups.items():
            #rlist.append('__- '+grp+' -')
            #for r in reagents:
                #rlist.append('    '+r)
        #self.solnTreeItems['Concentrations (mM)'].setAddList(rlist)

    def selectionChanged(self):
        selection = self.ui.solutionTable.selectionModel().selection().indexes()
        if len(selection) != 1:
            return
        item, col = self.ui.solutionTable.itemFromIndex(selection[0])
        if item.flags() & QtCore.Qt.ItemIsEditable == QtCore.Qt.ItemIsEditable:
            self.ui.solutionTable.editItem(item, col)

    def updateSolutionList(self):
        slist = self.ui.solutionList
        for item in slist.topLevelItems():
            if item is not self.addGroupItem:
                slist.removeTopLevelItem(item)
        
        grpItems = {}
        for soln in self.solutions.data:
            item = pg.TreeWidgetItem([soln.name])
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(0, QtCore.Qt.Unchecked)
            item.solution = soln
            group = soln.group
            if group not in grpItems:
                grpItems[group] = self.addGroup(group)
            grpItem = grpItems[group]
            grpItem.addChild(item)
        
        # should probably do this whenever reagent changes are detected
        #self.updateReagentList()
            
        
    def addGroup(self, name):
        item = GroupItem(name, adder='add solution', editable=True, checkable=True)
        self.ui.solutionList.insertTopLevelItem(self.ui.solutionList.topLevelItemCount()-1, item)
        item.sigAddClicked.connect(self.addSolutionClicked)
        return item
            
    def solutionListCheckStateChanged(self, item, column):
        checked = item.isChecked(0)
        if isinstance(item, GroupItem):
            for child in item.childItems():
                child.setChecked(0, checked)
        else:
            selected = item.solution in self.selectedSolutions
            if checked and not selected:
                self.selectedSolutions.append(item.solution)
            elif not checked and selected:
                self.selectedSolutions.remove(item.solution)
        self.updateSolutionTree()

    def solutionListTextChanged(self, item, column):
        if isinstance(item, GroupItem):
            for child in item.childItems():
                child.solution.group = str(item.text(0))
        else:
            item.solution.name = str(item.text(0))
            
    def addSolutionClicked(self, item):
        basename = 'New Solution'
        name = basename
        count = 2
        while True:
            try:
                self.solutions.add(name=name, group=item.text(0))
                break
            except NameError:
                name = basename + '%d'%count
                count += 1
        self.updateSolutionList()
        
    def showReagentsClicked(self, item, name):
        if self.showAllReagents:
            self.solnTreeItems['Concentrations (mM)'].addItem.setText('show all reagents')
        else:
            self.solnTreeItems['Concentrations (mM)'].addItem.setText('hide unused reagents')
        self.showAllReagents = not self.showAllReagents
        self.updateSolutionTree()

    def updateSolutionTree(self):
        self.ui.solutionTable.setColumnCount(len(self.selectedSolutions) + 1)
        self.ui.solutionTable.setHeaderLabels([''] + [s.name for s in self.selectedSolutions])
        
        # collect a list of all reagents in all selected solutions
        reagentTree = self.solnTreeItems['Concentrations (mM)']
        reagentTree.clear()
        reagents = set()
        for soln in self.selectedSolutions:
            reagents = reagents | set(soln.reagents.keys())
        # check for unknown reagents
        allReagents = self.solutions.reagents.data['name']
        unknown = [r for r in reagents if r not in allReagents]
        # sort
        if self.showAllReagents:
            reagents = list(allReagents) + unknown
        else:
            reagents = [x for x in allReagents if x in reagents] + unknown
        
        # update reagent list
        self.reagentItems = {}
        for reagent in reagents:
            #concs = ['%0.1f'%soln.reagents[reagent] if reagent in soln.reagents else '' for soln in self.selectedSolutions]
            #item = QtGui.QTreeWidgetItem([reagent] + concs)
            item = ReagentItem(reagent, self.selectedSolutions)
            reagentTree.addChild(item)
            self.reagentItems[reagent] = item
            if reagent in unknown:
                item.setForeground(0, QtGui.QColor(200, 0, 0))

        for i, soln in enumerate(self.selectedSolutions):
                # Calculate ion concentrations
            reagents = self.solutions.reagents[soln.reagents.keys()]
            concs = np.array([soln.reagents[n] for n in reagents['name']])
            for ion in IONS:
                tot = np.sum(reagents[ion] * concs)
                self.estIonConcItems[ion].setText(i+1, '%0.1f'%tot)
                
            # Set measured ion concentration values
            # (todo)
            self.solnTreeItems['Ion Concentrations (measured)'].setExpanded(False)
            
            # Calculate osmolarity
            osm = np.sum(concs * reagents['osmolarity'])
            self.solnTreeItems['Osmolarity (estimated)'].setText(i+1, '%0.1f'%osm)
        
        # resize columns
        for i in range(len(self.selectedSolutions)):
            self.ui.solutionTable.resizeColumnToContents(i)

        # update reversal potential special fields
        self.solutionTypeItem.setSolutions(self.selectedSolutions)


class ReagentItem(pg.TreeWidgetItem):
    def __init__(self, name, solutions):
        self.name = name
        self.solutions = solutions
        pg.TreeWidgetItem.__init__(self, [name] + ['%0.1f'%sol.reagents[name] if name in sol.reagents else '' for sol in solutions])
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

    def createEditor(self, parent, option, col):
        if col == 0:
            return None
        return QtGui.QLineEdit(parent)
    
    def setEditorData(self, editor, col):
        editor.setText(self.text(col))
    
    def setModelData(self, editor, model, col):
        sol = self.solutions[col-1]
        t = editor.text()
        if t == '':
            sol.reagents.pop(self.name, None)
        else:
            sol.reagents[self.name] = float(t)
        self.setText(col, editor.text())


class SolutionTypeItem(pg.TreeWidgetItem):
    def __init__(self):
        self.solutions = []
        pg.TreeWidgetItem.__init__(self, ['Solution type'])
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        
    def setSolutions(self, solutions):
        self.solutions = solutions
        for i,sol in enumerate(solutions):
            self.setText(i+1, sol.type)
            
    
            

class ItemDelegate(QtGui.QItemDelegate):
    """Delegate that allows tree items to create their own per-column editors.
    """
    def __init__(self, tree):
        QtGui.QItemDelegate.__init__(self, tree)
        self.tree = tree
        tree.setItemDelegate(self)
        
    def createEditor(self, parent, option, index):
        item, col = self.tree.itemFromIndex(index)
        if hasattr(item, 'createEditor'):
            return item.createEditor(parent, option, col)
        else:
            return None
    
    def setEditorData(self, editor, index):
        item, col = self.tree.itemFromIndex(index)
        return item.setEditorData(editor, col)
        
    def setModelData(self, editor, model, index):
        item, col = self.tree.itemFromIndex(index)
        return item.setModelData(editor, model, col)


class LabeledWidget(QtGui.QWidget):
    def __init__(self, text, widget):
        QtGui.QWidget.__init__(self)
        self.widget = widget
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QtGui.QLabel(text)
        self.label.setFixedWidth(100)
        self.layout.addWidget(self.label)
        self.layout.addWidget(widget)


class HtmlItem(pg.TreeWidgetItem):
    def __init__(self, text):
        pg.TreeWidgetItem.__init__(self)
        self.label = QtGui.QLabel(text)
        self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.setWidget(0, self.label)


class GroupItem(pg.TreeWidgetItem):
    def __init__(self, name, adder=None, editable=False, checkable=False, addList=None):
        class SigProxy(QtCore.QObject):
            sigAddClicked = QtCore.Signal(object, object)
        self._sigprox = SigProxy()
        self.sigAddClicked = self._sigprox.sigAddClicked
            
        pg.TreeWidgetItem.__init__(self, [name])
        font = QtGui.QFont()
        font.setWeight(QtGui.QFont.Bold)
        self.setFont(0, font)
        self.setExpanded(True)
        if editable:
            self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        if checkable:
            self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.setChecked(0, False)
        
        if adder is None:
            self.addItem = None
        else:
            self.addItem = AdderItem(adder, addList=addList)
            pg.TreeWidgetItem.addChild(self, self.addItem)
            self.addItem.clicked.connect(self.addClicked)

    def addChild(self, item):
        if self.addItem is None:
            pg.TreeWidgetItem.addChild(self, item)
        else:
            self.insertChild(self.childCount()-1, item)

    def addClicked(self, item, val):
        self.sigAddClicked.emit(self, val)

    def childItems(self):
        items = pg.TreeWidgetItem.childItems(self)
        if self.addItem is not None:
            items.remove(self.addItem)
        return items
    
    def clear(self):
        for item in self.childItems():
            self.removeChild(item)

    def setAddList(self, l):
        self.addItem.setAddList(l)


class AdderItem(pg.TreeWidgetItem):
    def __init__(self, text, addList=None):
        class SigProxy(QtCore.QObject):
            clicked = QtCore.Signal(object, object)  # self, value
        self._sigproxy = SigProxy()
        self.clicked = self._sigproxy.clicked
        
        pg.TreeWidgetItem.__init__(self)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.label = QtGui.QLabel()
        self.setText(text)
        self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label.linkActivated.connect(self.labelClicked)
        self.setWidget(0, self.label)
        
        self.addListPopup = QtGui.QMenu(self.label)
        self.addListPopup.triggered.connect(self.addSelected)
        
        self.setAddList(addList)

    def setText(self, col, text=None):
        if text is None:
            text = '+ <a href="/">%s</a>' % col
            self.label.setText(text)
        else:
            pg.TreeWidgetItem.setText(self, col, text)
        
    def setAddList(self, addList):
        self.addList = addList
        if addList is not None:
            w = self.addListPopup
            w.clear()
            for item in self.addList:
                if item.startswith('__'):
                    # secret code for adding non-interactive labels
                    l = QtGui.QLabel(item[2:])
                    f = l.font()
                    f.setWeight(f.Bold)
                    l.setFont(f)
                    a = QtGui.QWidgetAction(w)
                    a.setDefaultWidget(l)
                    w.addAction(a)
                else:
                    w.addAction(item)
        
    def labelClicked(self):
        if self.addList is None:
            self.clicked.emit(self, None)
        else:
            w = self.addListPopup
            pt = self.label.mapToGlobal(QtCore.QPoint(15, self.label.height()))
            w.popup(pt)
        
    def addSelected(self, action):
        self.clicked.emit(self, action.text())
        
        

class RecipeEditorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_recipeEditor()
        self.ui.setupUi(self)
        

class ConstraintEditorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_constraintEditor()
        self.ui.setupUi(self)


class SolutionEditorWindow(QtGui.QMainWindow):
    def __init__(self):
        self.reagents = Reagents()
        self.solutions = Solutions(self.reagents)
        
        QtGui.QMainWindow.__init__(self)
        self.resize(1200, 800)
        self.tabs = QtGui.QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.reagentEditor = ReagentEditorWidget(self.reagents)
        self.tabs.addTab(self.reagentEditor, 'Reagents')
        
        self.solutionEditor = SolutionEditorWidget(self.solutions)
        self.tabs.addTab(self.solutionEditor, 'Solutions')
        
        self.recipeEditor = RecipeEditorWidget()
        self.tabs.addTab(self.recipeEditor, 'Recipes')
        
        self.constraintEditor = ConstraintEditorWidget()
        self.tabs.addTab(self.constraintEditor, 'Constraints')
        self.tabs.setCurrentWidget(self.solutionEditor)

    def loadReagents(self, data):
        self.reagents.restore(data)
        self.reagentEditor.updateReagentList()
        
        