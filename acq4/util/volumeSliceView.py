
import numpy as np
import acq4.pyqtgraph as pg
from acq4.pyqtgraph.Qt import QtGui, QtCore
from acq4.util.rulerRoi import RulerROI


class VolumeSliceView(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.scale = None
        self.resize(800, 800)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        self.imv1 = pg.ImageView()
        self.imv2 = pg.ImageView()
        self.layout.addWidget(self.imv1, 0, 0)
        self.layout.addWidget(self.imv2, 1, 0)

        self.roi = RulerROI([[10, 64], [120,64]], pen='r')
        self.imv1.addItem(self.roi, ignoreBounds=True)
        self.roi.sigRegionChanged.connect(self.updateSlice)

    def setData(self, data, scale=None):
        if np.isscalar(scale):
            scale = (scale, scale)
        self.data = data
        if self.scale != scale:
            self.scale = scale

            # reset ROI position
            with pg.SignalBlock(self.roi.sigRegionChanged, self.updateSlice):
                h1, h2 = self.roi.getHandles()
                p1 = self.imv1.view.mapViewToScene(pg.Point(0, 0))
                if scale is None:
                    scale = (1, 1)
                p2 = self.imv1.view.mapViewToScene(pg.Point(10*scale[0], 0))
                h1.movePoint([p1.x(), p1.y()])
                h2.movePoint([p2.x(), p2.y()])
            
        self.imv1.setImage(data, scale=scale)
        self.updateSlice()

    def updateSlice(self):
        if self.data is None:
            return
        d2 = self.roi.getArrayRegion(self.data, self.imv1.imageItem, axes=(1,2))
        self.imv2.setImage(d2, scale=self.scale)
        print('repaint')
        self.imv2.ui.graphicsView.repaint()  # repaint immediately to avoid processing more mouse events before repaint

    def closeEvent(self, ev):
        self.imv1.close()
        self.imv2.close()
        self.data = None
