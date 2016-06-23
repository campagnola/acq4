from collections import OrderedDict
import numpy as np
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .reagentEditorTemplate import Ui_reagentEditor
from .solutionEditorTemplate import Ui_solutionEditor
from .recipeEditorTemplate import Ui_recipeEditor
from .constraintEditorTemplate import Ui_constraintEditor


IONS = ['Na', 'K', 'Cl', 'Ca', 'Mg', 'SO4', 'PO4', 'Cs']


GROUP_FONT = QtGui.QFont()
GROUP_FONT.setWeight(QtGui.QFont.Bold)



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
        self.reagents = {}
        
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
                grpItems[group] = QtGui.QTreeWidgetItem([group])
                grpItems[group].setFont(0, GROUP_FONT)
                tree.addTopLevelItem(grpItems[group])
                grpItems[group].setExpanded(True)
            grpItem = grpItems[group]
            grpItem.addChild(item)

        for i in range(self.ui.reagentTree.columnCount()):
            self.ui.reagentTree.resizeColumnToContents(i)


class SolutionEditorWidget(QtGui.QWidget):
    def __init__(self, solutions, parent=None):
        self.solutions = solutions
        self.selectedSolutions = []
        
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_solutionEditor()
        self.ui.setupUi(self)
        
        self.ui.solutionTable.setHeaderLabels([''])
        #self.ui.solutionTable.setUniformRowHeights(True)
        self.ui.solutionTable.clear()
        self.solnTreeItems = {}
        names = [
            'Concentrations (mM)',
            'Ion Concentrations (estimated)',
            'Ion Concentrations (measured)',
            'Osmolarity (estimated)',
            'Osmolarity (measured)',
            'Reversal Potentials',
        ]
        for name in names:
            item = QtGui.QTreeWidgetItem([name])
            item.setFont(0, GROUP_FONT)
            self.solnTreeItems[name] = item
            self.ui.solutionTable.addTopLevelItem(item)
            item.setExpanded(True)
            
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
        self.ui.solutionList.itemChanged.connect(self.solutionChanged)
        self.ui.reverseTempSpin.valueChanged.connect(self.updateSolutionTree)
        

    def updateSolutionList(self):
        slist = self.ui.solutionList
        slist.clear()
        
        grpItems = {}
        for soln in self.solutions.data:
            item = QtGui.QTreeWidgetItem([soln.name])
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(0, QtCore.Qt.Unchecked)
            item.solution = soln
            group = soln.group
            if group not in grpItems:
                grpItems[group] = QtGui.QTreeWidgetItem([group])
                grpItems[group].setFont(0, GROUP_FONT)
                slist.addTopLevelItem(grpItems[group])
                grpItems[group].setExpanded(True)
            grpItem = grpItems[group]
            grpItem.addChild(item)
            
        self.addGroupItem = HtmlItem('+ <a href="nowhere">add group</a>')
        slist.addTopLevelItem(self.addGroupItem)
        self.addGroupItem.label.linkActivated.connect(self.addGroup)
        
    def addGroup(self):
        item = pg.TreeWidgetItem(['New Group'])
        self.ui.solutionList.insertTopLevelItem(self.ui.solutionList.topLevelItemCount()-1, item)
        item.setExpanded(True)
        additem = HtmlItem('+ <a href="nowhere">add solution</a>')
        item.addChild(additem)
            
    def solutionChanged(self, item, column):
        checked = item.checkState(0) == QtCore.Qt.Checked
        if checked and item.solution not in self.selectedSolutions:
            self.selectedSolutions.append(item.solution)
        elif not checked and item.solution in self.selectedSolutions:
            self.selectedSolutions.remove(item.solution)
        else:
            item.solution.name = str(item.text(0))
        self.updateSolutionTree()

    def updateSolutionTree(self):
        self.ui.solutionTable.setColumnCount(len(self.selectedSolutions) + 1)
        self.ui.solutionTable.setHeaderLabels([''] + [s.name for s in self.selectedSolutions])
        
        # collect a list of all reagents in all selected solutions
        reagentTree = self.solnTreeItems['Concentrations (mM)']
        while reagentTree.childCount() > 0:
            reagentTree.removeChild(reagentTree.child(0))
        reagents = set()
        for soln in self.selectedSolutions:
            reagents = reagents | set(soln.reagents.keys())
        # check for unknown reagents
        allReagents = self.solutions.reagents.data['name']
        unknown = [r for r in reagents if r not in allReagents]
        # sort
        reagents = [x for x in allReagents if x in reagents] + unknown
        
        # update reagent list
        self.reagentItems = {}
        for reagent in reagents:
            concs = ['%0.1f'%soln.reagents[reagent] if reagent in soln.reagents else '' for soln in self.selectedSolutions]
            item = QtGui.QTreeWidgetItem([reagent] + concs)
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

        for i in range(len(self.selectedSolutions)):
            self.ui.solutionTable.resizeColumnToContents(i)


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
        
        