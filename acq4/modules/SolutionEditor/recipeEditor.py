import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .core import RecipeSet, Recipe
from .treeWidget import ItemDelegate, GroupItem
from .recipeEditorTemplate import Ui_recipeEditor


class RecipeEditorWidget(QtGui.QWidget):
    def __init__(self, db, parent=None):
        self.db = db
        self.recipeSet = None
        self.reagentItems = []
        self.solutionGroups = []
        
        self.addSolutionItem = None
        
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_recipeEditor()
        self.ui.setupUi(self)
        self.ui.splitter.setStretchFactor(0, 1)
        self.ui.splitter.setStretchFactor(1, 5)
        table = self.ui.recipeTable
        table.horizontalHeader().hide()
        
        self.ui.recipeSetList.currentRowChanged.connect(self.currentRecipeSetChanged)
        
        self.styleDelegate = StyleDelegate(table)

        self.updateRecipeSetList()
        self.updateRecipeTable()
        
        self.db.solutions.solutionListChanged.connect(self.solutionsChanged)
        self.ui.recipeTable.cellClicked.connect(self.cellClicked)
        self.ui.recipeTable.cellChanged.connect(self.cellChanged)

    def cellClicked(self, r, c):
        item = self.ui.recipeTable.item(r, c)
        if hasattr(item, 'itemClicked'):
            item.itemClicked()
            
    def cellChanged(self, r, c):
        item = self.ui.recipeTable.item(r, c)
        if hasattr(item, 'itemChanged'):
            item.itemChanged()
        
    def solutionsChanged(self):
        # list of all available solutions has changed
        for s in self.solutionGroups:
            s.solutionItem.setAllSolutions(self.db.solutions)
        if self.addSolutionItem is not None:
            self.addSolutionItem.setAllSolutions(self.db.solutions)
        
    def currentRecipeSetChanged(self, row):
        rs = self.db.recipes.recipeSets[row]
        if rs is not self.recipeSet:
            self.recipeSet = rs
            self.updateSolutionGroups()
        
    def updateSolutionGroups(self):
        self.solutionGroups = []
        for recipe in self.recipeSet.recipes:
            grp = SolutionItemGroup(self.ui.recipeTable, recipe, self.db)
            self.solutionGroups.append(grp)
        self.updateRecipeTable()
        
    def updateRecipeTable(self):
        # reset table
        table = self.ui.recipeTable
        table.clear()
        table.clearSpans()
        if self.recipeSet is None:
            return
        table.setColumnCount(sum([s.columns() for s in self.solutionGroups]) + 1)
        
        # generate new reagent list
        solns = [r.solution for r in self.recipeSet.recipes]
        reagents = set()
        for soln in solns:
            reagents |= set(soln.reagents.keys())

        # sort here...
        reagents = list(reagents)
        for sg in self.solutionGroups:
            sg.reagentOrder = reagents
        
        table.setRowCount(2 + len(reagents))
        #self.treeItems['Solution'].setSolutions(solns)
        table.setVerticalHeaderLabels(['', 'Volume'] + reagents)
        
        col = 0
        for grp in self.solutionGroups:
            grp.setupItems(col)
            col += grp.columns()

        self.addSolutionItem = SolutionItem()
        table.setItem(0, col, self.addSolutionItem)

        for col in range(table.columnCount()):
            table.setItemDelegateForColumn(col, self.styleDelegate)
        self.resizeColumns()
        self.solutionsChanged()
        self.addSolutionItem.sigChanged.connect(self.newSolutionSelected)
        #for i in range(len(solns)+1):
            #self.ui.recipeTree.resizeColumnToContents(i)
            
    def updateRecipeSetList(self):
        rsl = self.ui.recipeSetList
        rsl.clear()
        for i, rs in enumerate(self.db.recipes.recipeSets):
            rsl.addItem(rs.name)
            if rs is self.recipeSet:
                rsl.setCurrentItem(i)
            
    def resizeColumns(self):
        i = 0
        table = self.ui.recipeTable
        hh = table.horizontalHeader()
        for sg in self.solutionGroups:
            for j in range(sg.columns()-1):
                table.resizeColumnToContents(i)
                i += 1
            hh.resizeSection(i, 20)
            i += 1
        hh.resizeSection(i, 20)
            
    def newSolutionSelected(self, item, soln):
        soln = self.db.solutions[soln]
        recipe = Recipe(solution=soln, volumes=[100])
        self.recipeSet.recipes.append(recipe)
        grp = SolutionItemGroup(self.ui.recipeTable, recipe, self.db)
        self.solutionGroups.append(grp)
        grp.sigColumnCountChanged.connect(self.updateRecipeTable)
        self.updateRecipeTable()
            
    def renderRecipeSet(self):
        reagents = self.recipeSet.reagentOrder
        firstCol = ["Solution", "Volume (ml)"] + reagents
        
        cols = []
        for recipe in self.recipeSet.recipes:
            col = [recipe.solution]
            v = recipe.volume
            soln = self.db.solutions[recipe.solution]
            col.append(str(recipe.volume))
            for r in reagents:
                if r in soln.reagents:
                    col.append(str(soln.reagents[r] * v))
                else:
                    col.append('')
            cols.append(col)
            
        html = '<table style="border: 1px solid black;">\n'
        for i,row in enumerate(firstCol):
            html += '  <tr>\n    <td style="background-color: #aaaaaa;">%s</td>' % row
            html += ''.join(['<td>%s</td>' % col[i] for col in cols])
            html += '\n  </tr>\n'
        html += '</table>\n'
        self.ui.recipeText.setHtml(html)


class StyleDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, table):
        QtGui.QStyledItemDelegate.__init__(self)
        self.table = table
    
    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        item = self.table.item(index.row(), index.column())
        if hasattr(item, 'paint'):
            item.paint(painter, option)
            

class TableWidgetItem(QtGui.QTableWidgetItem):
    def __init__(self, *args):
        QtGui.QTableWidgetItem.__init__(self, *args)
        self.borders = {}
        
    def paint(self, painter, option):
        for border, pen in self.borders.items():
            painter.setPen(pen)
            if border == 'left':
                a,b = option.rect.topLeft(), option.rect.bottomLeft()
            elif border == 'right':
                a,b = option.rect.topRight(), option.rect.bottomRight()
            elif border == 'bottom':
                a,b = option.rect.bottomRight(), option.rect.bottomLeft()
            elif border == 'top':
                a,b = option.rect.topRight(), option.rect.topLeft()
            painter.drawLine(a, b)


class SolutionItemGroup(QtCore.QObject):
    sigColumnCountChanged = QtCore.Signal(object)  # self
    sigSolutionChanged = QtCore.Signal(object)  # self
    
    def __init__(self, table, recipe, db):
        QtCore.QObject.__init__(self)
        self.db = db
        self.table = table
        self.recipe = recipe
        
    def columns(self):
        return len(self.recipe.volumes) + 1
    
    def setupItems(self, col=None):
        if col is not None:
            self.column = col
        col = self.column
        
        self.solutionItem = SolutionItem(self.recipe.solution.name)
        self.table.setSpan(0, col, 1, len(self.recipe.volumes)+1)
        self.table.setItem(0, col, self.solutionItem)
        self.volumeItems = []
        reagents = self.recipe.solution.reagents
        self.reagentItems = {r:[] for r in self.reagentOrder}
        for j, vol in enumerate(self.recipe.volumes):
            vitem = EditableItem(str(vol))
            vitem.setBackgroundColor(QtGui.QColor(240, 240, 240))
            vitem.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
            self.volumeItems.append(vitem)
            self.table.setItem(1, col+j, vitem)
            vitem.sigChanged.connect(self.volumeChanged)
            for row, reagent in enumerate(self.reagentOrder):
                ritem = TableWidgetItem('')
                self.reagentItems[reagent].append(ritem)
                self.table.setItem(row+2, col+j, ritem)
        self.updateMasses()
            
        self.addVolumeItem = AdderItem()
        self.addVolumeItem.setBackgroundColor(QtGui.QColor(240, 240, 240))
        self.addVolumeItem.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        
        for row in range(self.table.rowCount()):
            self.table.item(row, col).borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        
        self.addVolumeItem.sigClicked.connect(self.addVolumeClicked)
        self.table.setItem(1, col+len(self.recipe.volumes), self.addVolumeItem)    
        
    def updateMasses(self):
        reagents = self.recipe.solution.reagents
        for j, vol in enumerate(self.recipe.volumes):
            for reagent, conc in reagents.items():
                mw = self.db.reagents[reagent]['molweight']
                mass = float((vol * 1e-3) * (conc * 1e-3) * (mw * 1e3))
                self.reagentItems[reagent][j].setText('%0.2f' % mass)
        
    def addVolumeClicked(self):
        self.recipe.volumes.append(100)
        self.sigColumnCountChanged.emit(self)

    def volumeChanged(self):
        vols = []
        for i, item in enumerate(self.volumeItems):
            t = item.text()
            if t == '':
                continue
            else:
                try:
                    v = float(t)
                except:
                    v = self.recipe.volumes[i]
            vols.append(v)

        if len(vols) != self.recipe.volumes:
            self.recipe.volumes = vols
            self.sigColumnCountChanged.emit(self)
        else:
            self.recipe.volumes = vols
            self.updateMasses()
        
    def updateItems(self):
        pass


class SolutionItem(TableWidgetItem):
    def __init__(self, soln='+'):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object, object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        TableWidgetItem.__init__(self, soln)
        self.menu = QtGui.QMenu()
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        self.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        self.borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.setBackgroundColor(QtGui.QColor(230, 230, 230))
        
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
        action = self.tableWidget().sender()
        text = action.text().strip()
        self.sigChanged.emit(self, text)

    def itemClicked(self):
        # popup menu when clicked
        tw = self.tableWidget()
        x = tw.verticalHeader().width() + tw.horizontalHeader().sectionPosition(tw.column(self))
        y = tw.horizontalHeader().height() + tw.visualItemRect(self).bottom()
        self.menu.popup(tw.mapToGlobal(QtCore.QPoint(x, y)))


class AdderItem(TableWidgetItem):
    def __init__(self):
        class SigProxy(QtCore.QObject):
            sigClicked = QtCore.Signal(object)
        self._sigprox = SigProxy()
        self.sigClicked = self._sigprox.sigClicked

        TableWidgetItem.__init__(self, '+')
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        
    def itemClicked(self):
        self.sigClicked.emit(self)


class EditableItem(TableWidgetItem):
    def __init__(self, text):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        TableWidgetItem.__init__(self, text)
        
    def itemChanged(self):
        self.sigChanged.emit(self)
