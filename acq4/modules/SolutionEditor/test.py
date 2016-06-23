import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from acq4.pyqtgraph import QtGui, QtCore
from acq4.modules.SolutionEditor.editor import SolutionEditorWindow

#app = QtGui.QApplication([])

w = SolutionEditorWindow()
w.show()

import pyqtgraph as pg
pg.dbg()

re = w.reagents
re.add(group='Monovalent Ions', name='Sodium Chloride', formula='NaCl', Na=1, Cl=1)
re.add(group='Monovalent Ions', name='Potassium Chloride', formula='KCl', K=1, Cl=1)
re.add(group='Monovalent Ions', name='Sodium Phosphate', formula='NaH2PO4', Na=1, PO4=1)
re.add(group='Buffers', name='Sodium Bicarbonate', formula='NaHCO3', Na=1)
re.add(group='Buffers', name='HEPES')
re.add(group='Divalent Ions', name='MgSO4', Mg=1, SO4=1)
re.add(group='Divalent Ions', name='CaCl2', Ca=1, Cl=2)
w.reagentEditor.updateReagentList()


solns = w.solutions
sol = solns.add('Standard ACSF', group='ACSF - recording')
sol['Sodium Chloride'] = 135
sol['Potassium Chloride'] = 3
sol['Sodium Bicarbonate'] = 22
sol['Magnesium Sulfate'] = 2
sol['Calcium Chloride'] = 1.3

sol = solns.add('Diss. ACSF', group='ACSF - slicing')
sol['Sodium Chloride'] = 135
sol['Potassium Chloride'] = 3
sol['Sodium Bicarbonate'] = 22
sol['Magnesium Sulfate'] = 2
sol['Calcium Chloride'] = 1.3

sol = solns.add('Standard Internal', group='Internal')
sol['Potassium Gluconate'] = 135
sol['Potassium Chloride'] = 3
sol['HEPES'] = 10

w.solutionEditor.updateSolutionList()


