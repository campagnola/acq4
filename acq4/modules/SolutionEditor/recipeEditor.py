import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .treeWidget import ItemDelegate
from .recipeEditorTemplate import Ui_recipeEditor


class RecipeEditorWidget(QtGui.QWidget):
    def __init__(self, recipes, solutions, parent=None):
        self.recipes = recipes
        self.solutions = solutions
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_recipeEditor()
        self.ui.setupUi(self)
        
        self.ui.recipeTree.clear()
        self.ui.recipeTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.recipeTreeDelegate = ItemDelegate(self.ui.recipeTree)  # allow items to specify their own editors
        self.ui.recipeTree.setHeaderLabels([''])
        self.ui.recipeTree.setColumnCount(2)
        self.treeItems = {}
        item = SolutionItem()
        self.treeItems['Solution'] = item
        self.ui.recipeTree.addTopLevelItem(item)
        names = ['Name', 'Volume', 'Show MW', 'Show Concentration', 'Reagent stocks']
        for n in names:
            item = EditableItem(n)
            self.treeItems[n] = item
            self.ui.recipeTree.addTopLevelItem(item)
            
        self.reagentItems = []
        self.updateRecipeTree()
        
        self.solutions.solutionListChanged.connect(self.solutionsChanged)
        self.ui.recipeTree.itemSelectionChanged.connect(self.selectionChanged)
        self.ui.recipeTree.itemClicked.connect(self.itemClicked)
        self.ui.recipeTree.resizeColumnToContents(0)
        self.treeItems['Solution'].sigChanged.connect(self.solutionItemChanged)

    def selectionChanged(self):
        selection = self.ui.recipeTree.selectionModel().selection().indexes()
        if len(selection) != 1:
            return
        item, col = self.ui.recipeTree.itemFromIndex(selection[0])
        if item.flags() & QtCore.Qt.ItemIsEditable == QtCore.Qt.ItemIsEditable:
            self.ui.recipeTree.editItem(item, col)

    def itemClicked(self, item, col):
        if hasattr(item, 'itemClicked'):
            item.itemClicked(col)
        
    def solutionItemChanged(self, item):
        # selected solutions have changed
        solns = [s for s in item.solutions if s is not None]
        self.ui.recipeTree.setColumnCount(len(solns) + 2)
        item.setSolutions(solns)
        for i in range(len(solns)+1):
            self.ui.recipeTree.resizeColumnToContents(i)
        
    def solutionsChanged(self):
        # list of all available solutions has changed
        self.treeItems['Solution'].setAllSolutions(self.solutions)
        
    def updateRecipeTree(self):
        pass
        #for i in range(1, self.ui.recipeTree.columnCount()):
            #self.treeItems['Solution'].setSolutions
            
            
        
class SolutionItem(pg.TreeWidgetItem):
    def __init__(self):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        self.solutions = []
        pg.TreeWidgetItem.__init__(self, ['Solution', 'add..'])
        self.menu = QtGui.QMenu()
        
    def setSolutions(self, solutions):
        # list of solutions to show in each column
        self.solutions = solutions
        for i,sol in enumerate(solutions):
            self.setText(i+1, sol)
        self.setText(len(solutions)+1, 'add..')
            
    def setAllSolutions(self, solutions):
        # list of solutions to show in dropdown menu
        self.menu.clear()
        self.menu.addAction('[none]', self.selectionChanged)
        grp = None
        for sol in solutions.data:
            if sol.group != grp:
                grp = sol.group
                label = QtGui.QLabel(grp)
                font = label.font()
                font.setWeight(font.Bold)
                label.setFont(font)
                act = QtGui.QWidgetAction(self.menu)
                act.setDefaultWidget(label)
                self.menu.addAction(act)
            self.menu.addAction("  " + sol.name, self.selectionChanged)
            
    def selectionChanged(self):
        action = self.treeWidget().sender()
        text = action.text().strip()
        while self._activeColumn > len(self.solutions):
            self.solutions.append(None)
        self.solutions[self._activeColumn-1] = None if text == '[none]' else text
        self.sigChanged.emit(self)

    def itemClicked(self, col):
        # popup menu when clicked
        tw = self.treeWidget()
        x = tw.header().sectionPosition(col)
        y = tw.header().height() + tw.visualItemRect(self).bottom()
        self.menu.popup(tw.mapToGlobal(QtCore.QPoint(x, y)))
        self._activeColumn = col
        return None


class EditableItem(pg.TreeWidgetItem):
    def __init__(self, name):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        self.name = name
        pg.TreeWidgetItem.__init__(self, [name])
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

    def createEditor(self, parent, option, col):
        if col == 0:
            return None
        return QtGui.QLineEdit(parent)
    
    def setEditorData(self, editor, col):
        editor.setText(self.text(col))
    
    def setModelData(self, editor, model, col):
        self.setText(col, editor.text())
        self.sigChanged.emit(self)

