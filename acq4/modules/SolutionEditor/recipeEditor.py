import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .core import RecipeSet, Recipe
from .treeWidget import ItemDelegate, GroupItem
from .recipeEditorTemplate import Ui_recipeEditor

"""
TODO:
 - copy HTML
 - fix column widths
 - per-solution notes
 - save/load
 - indicate table units somewhere..
 - highlight row/column headers for selected cell


"""



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
        table.verticalHeader().hide()
        
        self.ui.recipeSetList.currentRowChanged.connect(self.currentRecipeSetChanged)
        
        self.styleDelegate = StyleDelegate(table)

        self.updateRecipeSetList()
        self.updateRecipeTable()
        
        self.db.solutions.solutionListChanged.connect(self.solutionsChanged)
        self.ui.recipeTable.cellClicked.connect(self.cellClicked)
        self.ui.recipeTable.cellChanged.connect(self.cellChanged)
        self.ui.showMWCheck.clicked.connect(self.updateRecipeTable)
        self.ui.showConcentrationCheck.clicked.connect(self.updateSolutionGroups)

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
        
    def mkSolutionGroup(self, recipe):
        showConc = self.ui.showConcentrationCheck.isChecked()
        return SolutionItemGroup(self.ui.recipeTable, self.recipeSet, recipe, self.db, showConc)
        
    def updateSolutionGroups(self):
        self.solutionGroups = []
        for recipe in self.recipeSet.recipes:
            grp = self.mkSolutionGroup(recipe)
            self.solutionGroups.append(grp)
        self.updateRecipeTable()
        
    def updateRecipeTable(self):
        # reset table
        table = self.ui.recipeTable
        try:
            table.cellChanged.disconnect(self.cellChanged)
        except TypeError:
            pass
        table.clear()
        table.clearSpans()
        if self.recipeSet is None:
            return
        showMW = self.ui.showMWCheck.isChecked()
        table.setColumnCount(sum([s.columns() for s in self.solutionGroups]) + 2 + int(showMW))
        
        # generate new reagent list
        solns = [r.solution for r in self.recipeSet.recipes]
        reagents = set()
        for soln in solns:
            reagents |= set(soln.reagents.keys())

        # sort reagents
        reagentOrder = []
        for rec in self.db.reagents.data:
            if rec['name'] in reagents:
                reagentOrder.append(rec['name'])
        
        for sg in self.solutionGroups:
            sg.reagentOrder = reagentOrder
        
        # create first column
        table.setRowCount(2 + len(reagentOrder))
        for row, label in enumerate(['', '']):
            item = TableWidgetItem(label)
            table.setItem(row, 0, item)
        for row, reagent in enumerate(reagentOrder):
            item = ReagentItem(reagent, self.recipeSet.stocks.get(reagent, None))
            table.setItem(row+2, 0, item)
            item.sigStockConcentrationChanged.connect(self.stockConcentrationChanged)
            
        # optional MW column
        col = 1
        if showMW:
            header = TableWidgetItem('MW')
            table.setItem(1, col, header)
            for row, reagent in enumerate(reagentOrder):
                mw = self.db.reagents[reagent]['molweight']
                ritem = TableWidgetItem('%0.1f' % mw)
                table.setItem(row+2, col, ritem)
            col += 1
            
        # let each solution group fill its columns
        for grp in self.solutionGroups:
            grp.setupItems(col)
            col += grp.columns()

        self.addSolutionItem = SolutionItem()
        table.setItem(0, col, self.addSolutionItem)

        # set header background colors
        for col in range(table.columnCount()):
            table.setItemDelegateForColumn(col, self.styleDelegate)
            for row, bg in [(0, (220, 220, 220)), (1, (240, 240, 240))]:
                item = table.item(row, col)
                if item is None:
                    item = TableWidgetItem()
                    table.setItem(row, col, item)
                item.setBackgroundColor(QtGui.QColor(*bg))
                item.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))

        for row in range(2, table.rowCount()):
            item = table.item(row, 0)
            if item is not None:
                item.setBackgroundColor(QtGui.QColor(240, 240, 240))
            
        table.cellChanged.connect(self.cellChanged)
        self.solutionsChanged()
        self.addSolutionItem.sigChanged.connect(self.newSolutionSelected)
        self.resizeColumns()
            
    def updateRecipeSetList(self):
        rsl = self.ui.recipeSetList
        rsl.clear()
        for i, rs in enumerate(self.db.recipes.recipeSets):
            rsl.addItem(rs.name)
            if rs is self.recipeSet:
                rsl.setCurrentItem(i)
            
    def resizeColumns(self):
        table = self.ui.recipeTable
        hh = table.horizontalHeader()
        # temporarily clear header labels to allow correct column resizing
        xlabels = []
        for col in range(table.columnCount()):
            item = table.item(0, col)
            if item is None:
                xlabels.append(None)
            else:
                xlabels.append(item.text())
                item.setText('')
        
        # resize columns
        table.resizeColumnToContents(0)
        i = 1
        if self.ui.showMWCheck.isChecked():
            table.resizeColumnToContents(i)
            i += 1
        for sg in self.solutionGroups:
            for j in range(sg.columns()-1):
                table.resizeColumnToContents(i)
                i += 1
            hh.resizeSection(i, 20)
            i += 1
        hh.resizeSection(i, 20)
        
        # restore header labels
        for col, label in enumerate(xlabels):
            if label is not None:
                table.item(0, col).setText(label)
            
    def newSolutionSelected(self, item, soln):
        soln = self.db.solutions[soln]
        recipe = Recipe(solution=soln, volumes=[100])
        self.recipeSet.recipes.append(recipe)
        grp = self.mkSolutionGroup(recipe)
        self.solutionGroups.append(grp)
        grp.sigColumnCountChanged.connect(self.updateRecipeTable)
        self.updateRecipeTable()
        
    def stockConcentrationChanged(self, item, conc):
        if conc is None:
            self.recipeSet.stocks.pop(item.reagent, None)
        else:
            self.recipeSet.stocks[item.reagent] = conc
        for sg in self.solutionGroups:
            sg.updateMasses()
            
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
    
    def __init__(self, table, recipeSet, recipe, db, showConc=False):
        QtCore.QObject.__init__(self)
        self.db = db
        self.table = table
        self.recipe = recipe
        self.recipeSet = recipeSet
        self.showConc = showConc
        
    def columns(self):
        return len(self.recipe.volumes) + 1 + int(self.showConc)
    
    def setupItems(self, col=None):
        if col is not None:
            self.column = col
        col = self.column
        
        self.solutionItem = SolutionItem(self.recipe.solution.name)
        self.table.setSpan(0, col, 1, self.columns())
        self.table.setItem(0, col, self.solutionItem)
        self.volumeItems = []
        reagents = self.recipe.solution.reagents
        self.reagentItems = {r:[] for r in self.reagentOrder}

        if self.showConc:
            header = TableWidgetItem('Conc.')
            self.table.setItem(1, col, header)
            for row, reagent in enumerate(self.reagentOrder):
                conc = self.recipe.solution.reagents.get(reagent, None)
                conc = '' if conc is None else '%0.1f' % conc
                ritem = TableWidgetItem(conc)
                self.table.setItem(row+2, col, ritem)
            col += 1
            
        for j, vol in enumerate(self.recipe.volumes):
            vitem = EditableItem(str(vol))
            #vitem.setBackgroundColor(QtGui.QColor(240, 240, 240))
            #vitem.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
            self.volumeItems.append(vitem)
            self.table.setItem(1, col+j, vitem)
            vitem.sigChanged.connect(self.volumeChanged)
            for row, reagent in enumerate(self.reagentOrder):
                ritem = TableWidgetItem('')
                self.reagentItems[reagent].append(ritem)
                self.table.setItem(row+2, col+j, ritem)
        
        self.updateMasses()
            
        self.addVolumeItem = AdderItem()
        #self.addVolumeItem.setBackgroundColor(QtGui.QColor(240, 240, 240))
        #self.addVolumeItem.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        
        for row in range(self.table.rowCount()):
            self.table.item(row, self.column).borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        
        self.addVolumeItem.sigClicked.connect(self.addVolumeClicked)
        self.table.setItem(1, col+len(self.recipe.volumes), self.addVolumeItem)    
        
    def updateMasses(self):
        reagents = self.recipe.solution.reagents
        for j, vol in enumerate(self.recipe.volumes):
            for reagent, conc in reagents.items():
                stock = self.recipeSet.stocks.get(reagent, None)
                item = self.reagentItems[reagent][j]
                if stock is None:
                    mw = self.db.reagents[reagent]['molweight']
                    mass = float((vol * 1e-3) * (conc * 1e-3) * (mw * 1e3))
                    item.setText('%d' % mass)
                    item.setForeground(QtGui.QColor(0, 0, 0))
                else:
                    rvol = float((vol * 1e-3) * (conc * 1e-3) / (stock * 1e-3))
                    item.setText('%0.2g' % rvol)
                    item.setForeground(QtGui.QColor(0, 0, 150))
        
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
        #self.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        self.borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        #self.setBackgroundColor(QtGui.QColor(230, 230, 230))
        
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
        self.__sigprox = SigProxy()
        self.sigClicked = self.__sigprox.sigClicked

        TableWidgetItem.__init__(self, '+')
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        
    def itemClicked(self):
        self.sigClicked.emit(self)


class EditableItem(TableWidgetItem):
    def __init__(self, text):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object)
        self.__sigprox = SigProxy()
        self.sigChanged = self.__sigprox.sigChanged

        TableWidgetItem.__init__(self, text)
        
    def itemChanged(self):
        self.sigChanged.emit(self)


class LabeledLineEdit(QtGui.QWidget):
    def __init__(self, label, parent):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.label = QtGui.QLabel(label)
        self.layout.addWidget(self.label, 0, 0)
        self.text = QtGui.QLineEdit()
        self.layout.addWidget(self.text, 1, 0)
        
        self.editingFinished = self.text.editingFinished


class ReagentItem(TableWidgetItem):
    def __init__(self, reagent, stock):
        class SigProxy(QtCore.QObject):
            sigStockConcentrationChanged = QtCore.Signal(object, object)
        self.__sigprox = SigProxy()
        self.sigStockConcentrationChanged = self.__sigprox.sigStockConcentrationChanged

        TableWidgetItem.__init__(self, '')
        self.reagent = reagent
        
        self.menu = QtGui.QMenu()
        self.action = QtGui.QWidgetAction(self.menu)
        self.concEdit = LabeledLineEdit('Stock concentration:', self.menu)
        self.concEdit.text.setPlaceholderText('[ none ]')
        if stock is not None:
            self.concEdit.text.setText('%0.2f' % stock)
        self.action.setDefaultWidget(self.concEdit)
        self.menu.addAction(self.action)
        self.concEdit.editingFinished.connect(self.stockTextChanged)
        
        self.updateText(stock)
        
    def updateText(self, stock):
        text = self.reagent + ('' if stock is None else ' (%0.2fM)'%stock)
        self.setText(text)
        
    def itemClicked(self):
        tw = self.tableWidget()
        x = tw.verticalHeader().width() + tw.horizontalHeader().sectionPosition(tw.column(self))
        y = tw.horizontalHeader().height() + tw.visualItemRect(self).bottom()
        self.menu.popup(tw.mapToGlobal(QtCore.QPoint(x, y)))
        
    def stockTextChanged(self):
        t = self.concEdit.text.text()
        if t == '':
            conc = None
        else:
            conc = float(t)
        self.updateText(conc)
        self.sigStockConcentrationChanged.emit(self, conc)
        self.menu.hide()
