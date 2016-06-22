from collections import OrderedDict
import numpy as np
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .reagentEditorTemplate import Ui_reagentEditor
from .solutionEditorTemplate import Ui_solutionEditor


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


class Solutions(object):
    def __init__(self, reagents):
        self.reagents = reagents
        self.data = []

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
                tree.addTopLevelItem(grpItems[group])
                grpItems[group].setExpanded(True)
            grpItem = grpItems[group]
            grpItem.addChild(item)


class SolutionEditorWidget(QtGui.QWidget):
    def __init__(self, solutions, parent=None):
        self.solutions = solutions
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_solutionEditor()
        self.ui.setupUi(self)

    def updateSolutionList(self):
        slist = self.ui.solutionList
        
        slist.clear()
        grpItems = {}
        for soln in self.solutions.data:
            item = QtGui.QTreeWidgetItem([soln.name])
            item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
            group = soln.group
            if group not in grpItems:
                grpItems[group] = QtGui.QTreeWidgetItem([group])
                slist.addTopLevelItem(grpItems[group])
                grpItems[group].setExpanded(True)
            grpItem = grpItems[group]
            grpItem.addChild(item)
            

class SolutionEditorWindow(QtGui.QMainWindow):
    def __init__(self):
        self.reagents = Reagents()
        self.solutions = Solutions(self.reagents)
        
        QtGui.QMainWindow.__init__(self)
        self.resize(1000, 800)
        self.tabs = QtGui.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.reagentEditor = ReagentEditorWidget(self.reagents)
        self.tabs.addTab(self.reagentEditor, 'Reagents')
        self.solutionEditor = SolutionEditorWidget(self.solutions)
        self.tabs.addTab(self.solutionEditor, 'Solutions')

    def loadReagents(self, data):
        self.reagents.restore(data)
        self.reagentEditor.updateReagentList()
        
        