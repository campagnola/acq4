from collections import OrderedDict
import numpy as np
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .editorTemplate import Ui_Form


class Reagents(object):
    def __init__(self):
        self._dtype = [
            ('group', object),
            ('name', object),
            ('formula', object),
            ('molweight', float),
            ('osmolarity', float),
            ('cost', float),
            ('ions', [
                ('Na', float),
                ('K', float),
                ('Cl', float),
                ('Ca', float),
                ('Mg', float),
                ('SO4', float),
                ('PO4', float),
                ('Cs', float),
            ]),
            ('notes', object),
        ]
        self._null = (None, None, None, 0, 0, 0, (0, 0, 0, 0, 0, 0, 0, 0), None)
        self.data = np.empty(0, dtype=self._dtype)

    def add(self, **kwds):
        assert kwds['name'] not in self.data['name'], 'Reagent with this name already exists.'
        self.data = np.resize(self.data, len(self.data)+1)
        self.data[-1] = self._null
        if 'ions' in kwds:
            for k,v in kwds.pop('ions').items():
                self.data[-1]['ions'][k] = v
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
        



class SolutionEditorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.reagents = Reagents()
        
    def loadReagents(self, data):
        self.reagents.restore(data)
        self.updateReagentList()
        
    def updateReagentList(self):
        tree = self.ui.reagentTree
        items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
        oldGroups = OrderedDict([(item.text(0), item) for item in items])
        newGroups = self.reagents.groups()
        tree.clear()
        grpItems = {}
        for reagent in self.reagents.data:
            item = QtGui.QTreeWidgetItem([reagent['name']])
            group = reagent['group']
            if group not in grpItems:
                grpItems[group] = QtGui.QTreeWidgetItem([group])
                tree.addTopLevelItem(grpItems[group])
                grpItems[group].setExpanded(True)
            grpItem = grpItems[group]
            grpItem.addChild(item)