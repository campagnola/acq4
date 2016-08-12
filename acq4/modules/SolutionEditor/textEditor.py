from acq4.pyqtgraph.Qt import QtGui, QtCore


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
