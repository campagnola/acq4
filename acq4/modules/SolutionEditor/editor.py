from acq4.pyqtgraph.Qt import QtGui, QtCore
from .core import SolutionDatabase
from .reagentEditor import ReagentEditorWidget
from .solutionEditor import SolutionEditorWidget
from .recipeEditor import RecipeEditorWidget
from .constraintEditor import ConstraintEditorWidget


class SolutionEditorWindow(QtGui.QMainWindow):
    def __init__(self):
        self.db = SolutionDatabase()
        self.currentFile = None
        
        QtGui.QMainWindow.__init__(self)
        self.resize(1200, 800)
        self.tabs = QtGui.QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.reagentEditor = ReagentEditorWidget(self.db)
        self.tabs.addTab(self.reagentEditor, 'Reagents')
        
        self.solutionEditor = SolutionEditorWidget(self.db)
        self.tabs.addTab(self.solutionEditor, 'Solutions')
        
        self.recipeEditor = RecipeEditorWidget(self.db)
        self.tabs.addTab(self.recipeEditor, 'Recipes')
        
        self.constraintEditor = ConstraintEditorWidget()
        self.tabs.addTab(self.constraintEditor, 'Constraints')
        self.tabs.setCurrentWidget(self.solutionEditor)

        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction('Open', self.restore)
        self.fileMenu.addAction('Save', self.save)
        self.fileMenu.addAction('Save As', self.saveAs)

    def loadReagents(self, data):
        self.reagents.restore(data)
        self.reagentEditor.updateReagentList()
        
    def save(self):
        if self.currentFile is None:
            self.saveAs()
        else:
            json.dump(self.db.save(), open(self.currentFile, 'wb'), indent=2)
        
    def saveAs(self):
        fname = QtGui.QFileDialog.getSaveFileName()
        if fname is not None:
            self.currentFile = fname
            self.setWindowTitle('Solution Editor: ' + fname)
            self.save()
        
    def restore(self):
        fname = QtGui.QFileDialog.getOpenFileName()
        if fname is None:
            return
        self.currentFile = fname
        self.setWindowTitle('Solution Editor: ' + fname)
        state = json.load(open(fname, 'rb'))
        self.reagents.restore(state['reagents'])
        self.reagentEditor.updateReagentList()
        self.solutions.restore(state['solutions'])
        self.solutionEditor.updateSolutionList()
        self.solutionEditor.updateSolutionTree()
        