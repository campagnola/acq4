from acq4.pyqtgraph.Qt import QtGui, QtCore
from .constraintEditorTemplate import Ui_constraintEditor


class ConstraintEditorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_constraintEditor()
        self.ui.setupUi(self)
