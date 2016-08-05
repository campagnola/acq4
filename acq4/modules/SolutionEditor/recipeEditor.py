import re
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from .core import RecipeSet, Recipe
from .treeWidget import AdderItem
from .recipeEditorTemplate import Ui_recipeEditor

"""
TODO:
 - highlight row/column headers for selected cell
 - pretty-formatted formula names
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
        self.ui.hsplitter.setStretchFactor(0, 1)
        self.ui.hsplitter.setStretchFactor(1, 5)
        self.ui.vsplitter.setStretchFactor(0, 3)
        self.ui.vsplitter.setStretchFactor(1, 1)
        table = self.ui.recipeTable
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        
        rsl = self.ui.recipeSetList
        rsl.currentItemChanged.connect(self.currentRecipeSetChanged)
        rsl.setEditTriggers(rsl.SelectedClicked | rsl.DoubleClicked)
        rsl.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.styleDelegate = StyleDelegate(table)
        
        self.updateRecipeSetList()
        self.updateRecipeTable()
        
        self.db.solutions.solutionListChanged.connect(self.solutionsChanged)
        self.db.recipes.sigRecipeSetListChanged.connect(self.updateRecipeSetList)
        self.ui.recipeTable.cellClicked.connect(self.cellClicked)
        self.ui.recipeTable.cellChanged.connect(self.cellChanged)
        self.ui.showMWCheck.clicked.connect(self.updateRecipeTable)
        self.ui.showFormulaeCheck.clicked.connect(self.updateRecipeTable)
        self.ui.showConcentrationCheck.clicked.connect(self.updateSolutionGroups)
        self.ui.copyHtmlBtn.clicked.connect(self.copyHtml)
        rsl.itemChanged.connect(self.recipeSetItemChanged)
        rsl.customContextMenuRequested.connect(self.recipeSetMenuRequested)

    def recipeSetMenuRequested(self, point):
        item = self.ui.recipeSetList.itemAt(point)
        item.showContextMenu(point)

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
        
    def currentRecipeSetChanged(self, item):
        row = self.ui.recipeSetList.indexOfTopLevelItem(item)
        if row >= len(self.db.recipes):
            return
        rs = self.db.recipes[row]
        if rs is not self.recipeSet:
            self.recipeSet = rs
            self.updateSolutionGroups()
        
    def mkSolutionGroup(self, recipe):
        showConc = self.ui.showConcentrationCheck.isChecked()
        grp = SolutionItemGroup(self.ui.recipeTable, self.recipeSet, recipe, self.db, showConc)
        grp.sigSolutionChanged.connect(self.solutionChanged)
        grp.sigColumnCountChanged.connect(self.updateRecipeTable)
        return grp
    
    def solutionChanged(self, grp, soln):
        # user selected a new solution for an existing column
        i = self.solutionGroups.index(grp)
        if soln == '[remove]':
            self.recipeSet.remove(grp.recipe)
        else:
            self.recipeSet[i].solution = self.db.solutions[soln]
        self.updateSolutionGroups()
        
    def updateSolutionGroups(self):
        self.solutionGroups = []
        for recipe in self.recipeSet:
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
        solns = [r.solution for r in self.recipeSet]
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
        table.setRowCount(3 + len(reagentOrder))
        for row, label in enumerate(['', '']):
            item = TableWidgetItem(label)
            table.setItem(row, 0, item)
        showFormulae = self.ui.showFormulaeCheck.isChecked()
        for row, reagent in enumerate(reagentOrder):
            name = reagent
            if showFormulae:
                formula = self.db.reagents[reagent]['formula']
                name = reagent if formula == '' else formula
            item = ReagentItem(name, self.recipeSet.stocks.get(reagent, None))
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

        # Extra column for adding solutions
        self.addSolutionItem = SolutionItem(removable=False)
        table.setItem(0, col, self.addSolutionItem)

        # Add a row for units
        label = QtGui.QLabel('masses in mg, <span style="color: #0000c8">stock volumes in ml</span>')
        label.setAlignment(QtCore.Qt.AlignRight)
        f = label.font()
        f.setPointSize(8)
        label.setFont(f)
        row = len(reagentOrder) + 2
        table.setSpan(row, 0, 1, table.columnCount())
        table.setCellWidget(row, 0, label)
            
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
        
        # update notes table
        self.ui.notesTree.clear()
        for recipe in self.recipeSet:
            item = RecipeNoteItem(recipe)
            self.ui.notesTree.addTopLevelItem(item)
        
            
    def updateRecipeSetList(self):
        rsl = self.ui.recipeSetList
        rsl.clear()
        for i, rs in enumerate(self.db.recipes):
            item = RecipeSetItem(rs)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.sigCopyClicked.connect(self.recipeSetCopyClicked)
            item.sigRemoveClicked.connect(self.recipeSetRemoveClicked)
            rsl.addTopLevelItem(item)
            if rs is self.recipeSet:
                rsl.setCurrentItem(item)
        self.recipeSetAdder = AdderItem('Add recipe set')
        rsl.addTopLevelItem(self.recipeSetAdder)
        self.recipeSetAdder.clicked.connect(self.addRecipeSet)
        
    def addRecipeSet(self):
        i = 1
        rsnames = [rs.name for rs in self.db.recipes]
        while True:
            name = 'RecipeSet_%d' % i
            if name not in rsnames:
                break
            i += 1
        rs = RecipeSet(name)
        self.db.recipes.add(rs)
        
        # select new item
        rsl = self.ui.recipeSetList
        item = rsl.topLevelItem(rsl.topLevelItemCount()-2)
        rsl.setCurrentItem(item, 0, QtGui.QItemSelectionModel.SelectCurrent)
            
    def recipeSetItemChanged(self, item, col):
        item.recipeSet.name = item.text(0)

    def recipeSetCopyClicked(self, rsetItem):
        names = [rs.name for rs in self.db.recipes]
        i = 0
        while True:
            name = rsetItem.recipeSet.name + '_copy_%d' % i
            if name not in names:
                break
            i += 1
        rset = rsetItem.recipeSet.copy(name)
        self.db.recipes.add(rset)

    def recipeSetRemoveClicked(self, rsetItem):
        self.db.recipes.remove(rsetItem.recipeSet)
            
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
        self.recipeSet.add(recipe)
        grp = self.mkSolutionGroup(recipe)
        self.solutionGroups.append(grp)
        self.updateRecipeTable()
        
    def stockConcentrationChanged(self, item, conc):
        if conc is None:
            self.recipeSet.stocks.pop(item.reagent, None)
        else:
            self.recipeSet.stocks[item.reagent] = conc
        for sg in self.solutionGroups:
            sg.updateMasses()

    def copyHtml(self):
        table = self.ui.recipeTable
        
        # decide which columns to skip
        skip = []
        for col in range(table.columnCount()):
            s = False
            for row in (0, 1):
                item = table.item(row, col)
                if item is not None and item.text() == '+':
                    s = True
                    break
            skip.append(s)
            
        # generate HTML table
        txt = '<div style="font-family: sans-serif"><h2>%s</h2><table>\n' % self.recipeSet.name
        for row in range(table.rowCount()):
            txt += '  <tr>\n'
            spanskip = 0
            for col in range(table.columnCount()):
                # skip cell if a previous cell has wide span
                if spanskip > 0:
                    spanskip -= 1
                    continue
                # skip column if it was a placeholder / adder column
                if skip[col]:
                    continue
                
                item = table.item(row, col)
                span = table.columnSpan(row, col)
                spanskip = span - 1
                for c in range(col+1, col+span):
                    if skip[c]:
                        span -= 1
                width = table.horizontalHeader().sectionSize(col)
                
                if item is None:
                    w = table.cellWidget(row, col)
                    if w is None:
                        t = ''
                        style = ''
                    else:
                        t = w.text()
                        fs = w.font().pointSize()
                        a = w.alignment()
                        if a & QtCore.Qt.AlignRight > 0:
                            align = 'right'
                        elif a & QtCore.Qt.AlignLeftt > 0:
                            align = 'left'
                        elif a & QtCore.Qt.AlignCenter > 0:
                            align = 'center'
                        style = 'font-size: %dpt; text-align: %s' % (fs, align)
                else:
                    t = str(item.text())
                    bg = item.background().color().name()
                    fg = item.foreground().color().name()
                    
                    style = 'color: %s; background-color: %s;' % (fg, bg)
                    if hasattr(item, 'borders'):
                        for k,v in item.borders.items():
                            style += ' border-%s: 1px solid %s;' % (k, v.color().name())
                    
                    
                txt += '    <td style="font-family: sans-serif; font-size: 10pt; vertical-align: middle; width: %dpx; %s" colspan="%s">%s</td>\n' % (width, style, span, t)
            txt += '  </tr>\n'
        txt += '</table>\n'

        # copy notes
        txt += '<span style="font-size: 10pt;">\n'
        for i in range(self.ui.notesTree.topLevelItemCount()):
            item = self.ui.notesTree.topLevelItem(i)
            note = item.noteHtml()
            if note != '':
                txt += '\n<br><br>' + note
        txt += '</span>\n'

        txt += '\n</div>'
        
        # copy to clipboard
        md = QtCore.QMimeData()
        md.setHtml(txt)
        QtGui.QApplication.clipboard().setMimeData(md)


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
        # need this because cells report their background incorrectly
        # if it hasn't been set
        self.setBackground(QtGui.QColor(255, 255, 255))
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
    sigSolutionChanged = QtCore.Signal(object, object)  # self, soln
    
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
        self.solutionItem.sigChanged.connect(self.solutionChanged)
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
            vitem = EditableItem('%d' % vol)
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
            
        self.addVolumeItem = TableAdderItem()
        #self.addVolumeItem.setBackgroundColor(QtGui.QColor(240, 240, 240))
        #self.addVolumeItem.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        
        for row in range(len(self.reagentOrder) + 2):
            item = self.table.item(row, self.column)
            if item is not None:
                item.borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        
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
                    item.setText('%.4g' % rvol)
                    item.setForeground(QtGui.QColor(0, 0, 200))
        
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
        
    def solutionChanged(self, item, soln):
        self.sigSolutionChanged.emit(self, soln)
        

class SolutionItem(TableWidgetItem):
    def __init__(self, soln='+', removable=True):
        class SigProxy(QtCore.QObject):
            sigChanged = QtCore.Signal(object, object)
        self._sigprox = SigProxy()
        self.sigChanged = self._sigprox.sigChanged

        self.removable = removable
        TableWidgetItem.__init__(self, soln)
        self.menu = QtGui.QMenu()
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        #self.borders['bottom'] = QtGui.QPen(QtGui.QColor(50, 50, 50))
        self.borders['left'] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        #self.setBackgroundColor(QtGui.QColor(230, 230, 230))
        
    def setAllSolutions(self, solutions):
        # list of solutions to show in dropdown menu
        self.menu.clear()
        if self.removable:
            self.menu.addAction('[remove]', self.selectionChanged)
        grp = None
        for sol in solutions:
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


class TableAdderItem(TableWidgetItem):
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


class RecipeSetItem(QtGui.QTreeWidgetItem):
    def __init__(self, rset):
        class SigProxy(QtCore.QObject):
            sigCopyClicked = QtCore.Signal(object)
            sigRemoveClicked = QtCore.Signal(object)
        self.__sigprox = SigProxy()
        self.sigCopyClicked = self.__sigprox.sigCopyClicked
        self.sigRemoveClicked = self.__sigprox.sigRemoveClicked

        self.recipeSet = rset
        QtGui.QTreeWidgetItem.__init__(self, [rset.name])
        self.menu = QtGui.QMenu()
        self.menu.addAction('Copy', self.copyClicked)
        self.menu.addAction('Remove', self.removeClicked)
        
    def showContextMenu(self, point):
        pt = self.treeWidget().mapToGlobal(point)
        self.menu.popup(pt)
        
    def copyClicked(self):
        self.sigCopyClicked.emit(self)
        
    def removeClicked(self):
        self.sigRemoveClicked.emit(self)


class RecipeNoteItem(pg.TreeWidgetItem):
    def __init__(self, recipe):
        self.recipe = recipe
        pg.TreeWidgetItem.__init__(self, [recipe.solution.name])
        self.textItem = pg.TreeWidgetItem()
        self.addChild(self.textItem)
        self.editor = RichTextEdit()
        self.textItem.setWidget(0, self.editor)
        self.editor.setHtml(recipe.notes)
        self.editor.textChanged.connect(self.textChanged)
        
    def textChanged(self):
        if self.editor.toPlainText().strip() == '':
            self.recipe.notes = None
        else:
            self.recipe.notes = self.editor.toHtml()
    
    def noteHtml(self):
        if self.editor.toPlainText().strip() == '':
            return ''
        note = self.editor.toHtml()
        return "<b>%s</b><br>\n%s" % (self.recipe.solution.name, note) 
    
    
class RichTextEdit(QtGui.QTextEdit):
    def __init__(self, *args):
        QtGui.QTextEdit.__init__(self, *args)
        self.setToolTip('Formatting keys:<br><b>bold: ctrl-b</b><br><i>italic: ctrl-i</i><br><span style="text-decoration: underline">underline: ctrl-u</span>')
        
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_B and ev.modifiers() == QtCore.Qt.ControlModifier:
            if self.fontWeight() == QtGui.QFont.Normal:
                self.setFontWeight(QtGui.QFont.Bold)
            else:
                self.setFontWeight(QtGui.QFont.Normal)
        elif ev.key() == QtCore.Qt.Key_I and ev.modifiers() == QtCore.Qt.ControlModifier:
            self.setFontItalic(not self.fontItalic())
        elif ev.key() == QtCore.Qt.Key_U and ev.modifiers() == QtCore.Qt.ControlModifier:
            self.setFontUnderline(not self.fontUnderline())
        else:
            return QtGui.QTextEdit.keyPressEvent(self, ev)
