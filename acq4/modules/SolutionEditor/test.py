import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from acq4.pyqtgraph import QtGui, QtCore
from acq4.modules.SolutionEditor.editor import SolutionEditorWindow
from acq4.modules.SolutionEditor.core import Solution

#app = QtGui.QApplication([])

w = SolutionEditorWindow()
w.show()

import pyqtgraph as pg
#pg.dbg()


#re = w.reagents
#re.add(group='Monovalent Ions', name='Sodium Chloride', formula='NaCl', molweight=58.44, osmolaritry=1.84, Na=1, Cl=1)
#re.add(group='Monovalent Ions', name='Potassium Chloride', formula='KCl', K=1, Cl=1)
#re.add(group='Monovalent Ions', name='Sodium Phosphate', formula='NaH2PO4', Na=1, PO4=1)
#re.add(group='Buffers', name='Sodium Bicarbonate', formula='NaHCO3', Na=1)
#re.add(group='Buffers', name='HEPES')
#re.add(group='Divalent Ions', name='MgSO4', Mg=1, SO4=1)
#re.add(group='Divalent Ions', name='CaCl2', Ca=1, Cl=2)
#w.reagentEditor.updateReagentList()


solns = w.db.solutions
sol = Solution(name='Standard ACSF', group='ACSF', against='Standard Internal')
sol['sodium chloride'] = 123
sol['potassium chloride'] = 3
sol['potassium phosphate monobasic'] = 1.25
sol['sodium bicarbonate'] = 25
sol['glucose'] = 10
sol['magnesium sulfate'] = 2
sol['calcium chloride'] = 1.3
solns.add(sol)

sol = Solution('Diss. ACSF', group='ACSF', against='Standard Internal')
sol['n-methyl-d-glucamine'] = 123
sol['potassium chloride'] = 3
sol['potassium phosphate monobasic'] = 1.25
sol['sodium bicarbonate'] = 25
sol['glucose'] = 10
sol['magnesium sulfate'] = 4
sol['calcium chloride'] = 0.5
sol['hydrochloric acid'] = 123
solns.add(sol)

sol = Solution('Standard Internal', group='Internal', against='Standard ACSF')
sol['potassium gluconate'] = 130
sol['potassium chloride'] = 4
sol['HEPES'] = 10
sol['EGTA'] = 0.3
sol['phosphocreatine bg'] = 10
sol['magnesium ATP'] = 4
sol['GTP sodium hydrate'] = 0.3
solns.add(sol)


w.solutionEditor.updateSolutionList()
w.tabs.setCurrentIndex(2)

