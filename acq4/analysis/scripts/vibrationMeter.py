from PyQt4 import QtCore, QtGui
import numpy as np
import acq4.pyqtgraph as pg
import acq4.Manager
import acq4.util.imageAnalysis as imageAnalysis



class VibrationMeter(QtGui.QWidget):
    def __init__(self, camModule='Camera', roi=0):
        """Plot the intensity across an ROI line over time.
        """
        QtGui.QWidget.__init__(self)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.plot = pg.PlotWidget()
        self.layout.addWidget(self.plot, 0, 0)
        self.wfPlot = pg.PlotWidget()
        self.layout.addWidget(self.wfPlot, 1, 0)
        self.wfImage = pg.ImageItem()
        self.wfPlot.addItem(self.wfImage)
        self.wfData = None

        self.frames = []

        man = acq4.Manager.getManager()
        self.mod = man.getModule(camModule)
        self.roiInd = roi

        self.mod.window().sigNewFrame.connect(self.newFrame)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.replot)
        self.timer.start(30)

        self.show()

    def newFrame(self, mod, iface, frame):
        self.frames.append((iface, frame))

    def replot(self):
        if len(self.frames) == 0:
            return

        rois = self.mod.window().roiWidget.ROIs
        if self.roiInd >= len(rois):
            return
        roi = rois[self.roiInd]['roi']

        lines = []
        while len(self.frames) > 0:
            iface, frame = self.frames.pop(0)
            data = roi.getArrayRegion(frame.data(), iface.getImageItem(), axes=(0, 1))
            lines.append(data)

        self.plot.plot(data, clear=True)

        lines = [l for l in lines if len(l) == len(data)]
        if self.wfData is None or self.wfData.shape[1] != len(data):
            self.wfData = np.zeros((500, len(data)), dtype=data.dtype)
        self.wfData = np.roll(self.wfData, -len(lines), axis=0)
        for i,l in enumerate(lines):
            self.wfData[-len(lines)+i] = l
        self.wfImage.setImage(self.wfData)

    def closeEvent(self, ev):
        self.timer.stop()
        self.wfData = None
        self.lastFrame = None
        self.plot.close()
        self.wfPlot.close()
        return QtGui.QWidget.closeEvent(self, ev)


