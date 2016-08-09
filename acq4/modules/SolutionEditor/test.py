import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


from acq4.pyqtgraph import QtGui, QtCore
from acq4.modules.SolutionEditor.editor import SolutionEditorWindow
from acq4.modules.SolutionEditor.core import Solution, Recipe, RecipeSet, SolutionDatabase

#import pyqtgraph as pg
#pg.dbg()


db = SolutionDatabase()

solns = db.solutions
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


r1 = Recipe(solution=solns['Standard ACSF'], volumes=[1000, 500], notes="Here's how you make <i>this</i> recipe...")
r2 = Recipe(solution=solns['Diss. ACSF'], volumes=[1000, 500])
rs = RecipeSet(name='Standard recipes', recipes=[r1, r2])
rs.stocks['hydrochloric acid'] = 5.0
db.recipes.add(rs)
rs = RecipeSet(name='Recording ACSF', recipes=[r1])
db.recipes.add(rs)


w = SolutionEditorWindow(db=db)
w.show()


#w.solutionEditor.updateSolutionList()
#w.tabs.setCurrentIndex(2)

