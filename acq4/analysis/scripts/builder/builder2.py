import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import numpy as np
import acq4.pyqtgraph as pg
import acq4.util.metaarray as metaarray

from acq4.pyqtgraph.Qt import QtGui, QtCore
# from acq4.util.volumeSliceView import VolumeSliceView
from acq4.util.rulerRoi import RulerROI
from builder2Template import Ui_MainWindow

class AtlasBuilder(QtGui.QMainWindow):
    def __init__(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)




class AtlasViewer(QtGui.QWidget):
    def __init__(self, parent=None):
        self.atlas = None
        self.label = None

        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.splitter = QtGui.QSplitter()
        self.layout.addWidget(self.splitter)

        self.view = VolumeSliceView()
        self.splitter.addWidget(self.view)

        self.ctrl = QtGui.QWidget(parent=self)
        self.splitter.addWidget(self.ctrl)
        self.ctrlLayout = QtGui.QVBoxLayout()
        self.ctrl.setLayout(self.ctrlLayout)

        self.axisSelector = AxisSelector(self)
        self.axisSelector.axisChanged.connect(self.updateImage)
        self.ctrlLayout.addWidget(self.axisSelector)

        self.labelTree = LabelTree(self)
        self.ctrlLayout.addWidget(self.labelTree)

    def setLabels(self, label):
        self.label = label
        for id in np.unique(label[1000])[:10]:
            self.labelTree.addLabel(id, str(id), pg.mkColor((id, 100)))
        self.updateImage()

    def setAtlas(self, atlas):
        self.atlas = atlas
        self.updateImage()

    def updateImage(self):
        if self.atlas is None or self.label is None:
            return
        axis = self.axisSelector.axis
        axes = [
            ('right', 'anterior', 'dorsal'),
            ('dorsal', 'right', 'anterior'),
            ('anterior', 'right', 'dorsal')
        ][axis]
        self.displayAtlas = self.atlas.transpose(axes)
        self.displayLabel = self.label.transpose(axes)
        print "scale:", self.atlas._info[-1]['vxsize']
        self.view.setData(self.displayAtlas.view(np.ndarray), self.displayLabel.view(np.ndarray), scale=self.atlas._info[-1]['vxsize'])

    def labelsChanged(self):
        labels = self.labelTree.activeLabels()
        # self.lut = np.zeros((2**(self.label.itemsize*8)


class AxisSelector(QtGui.QWidget):

    axisChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.radios = []
        for ax in ('right', 'dorsal', 'anterior'):
            r = QtGui.QRadioButton(ax, parent=self)
            self.radios.append(r)
            self.layout.addWidget(r)
            r.toggled.connect(self.radioToggled)

        self.radios[0].setChecked(True)

    def radioToggled(self, b):
        if b:
            for i in range(3):
                if self.radios[i].isChecked():
                    self.axis = i
                    break
            self.axisChanged.emit(self.axis)



class LabelTree(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.headerItem().setText(0, "id")
        self.headerItem().setText(1, "name")
        self.headerItem().setText(2, "color")
        self.labels = {}
        self.checked = set()
        self.itemChanged.connect(self.itemChange)

    def addLabel(self, id, name, color):
        item = QtGui.QTreeWidgetItem([str(id), str(name), ''])
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)

        btn = pg.ColorButton(color=color)
        self.addTopLevelItem(item)
        self.setItemWidget(item, 2, btn)
        self.labels[id] = {'item': item, 'btn': btn}
        item.id = id

        # btn.sigColorChanged.connect(self.itemChanged)
        # btn.sigColorChanging.connect(self.imageChanged)

    def itemChange(self, item, col):
        checked = item.checkState() == QtCore.Qt.Checked
        if checked:
            self.checked.add(item.id)
        else:
            self.checked.remove(item.id)


class VolumeView(QtGui.QSplitter):
    # 3 orthogonal views
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.scale = None
        # anterior, dorsal, right
        self.axes = [(2, 1), (0, 1), (2, 0)]

        self.widgets = []
        self.views = []
        self.images = []
        self.lines = []
        for i in range(3):
            w = pg.GraphicsLayoutWidget()
            v = w.addViewBox()
            v.invertY(False)
            self.addWidget(w)
            self.widgets.append(w)
            self.views.append(v)
            img = LabelImageItem()
            v.addItem(img)
            self.images.append(img)
            l1 = pg.InfiniteLine(angle=0)
            l2 = pg.InfiniteLine(angle=90)
            v.addItem(l1)
            v.addItem(l2)
            l1.axis = i, 0
            l2.axis = i, 1
            self.lines.append((l1, l2))
            l1.sigValueChanging.connect(self.lineMoved)
            l2.sigValueChanging.connect(self.lineMoved)

    def setData(self, atlas, label, scale):
        self.atlas = atlas
        self.label = label
        self.scale = scale

        # re-center lines:
        for ax in range(3):
            l1, l2 = self.lines[ax]
            with pg.SignalBlocker(l1.sigValueChanging, self.lineMoved):
                l1.setValue(atlas.shape[self.axes[ax][0]] * 0.5 * scale)
            with pg.SignalBlocker(l2.sigValueChanging, self.lineMoved):
                l2.setValue(atlas.shape[self.axes[ax][1]] * 0.5 * scale)

        self.updateImages()

    def lineMoved(self, line):
        print line

    def updateImages(self):
        for i in range(3):
            ax = self.axes[i]
            self.images[i]


class VolumeSliceView(QtGui.QWidget):
    def __init__(self, parent=None):
        self.atlas = None
        self.label = None

        QtGui.QWidget.__init__(self, parent)
        self.scale = None
        self.resize(800, 800)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.w1 = pg.GraphicsLayoutWidget()
        self.w2 = pg.GraphicsLayoutWidget()
        self.view1 = self.w1.addViewBox()
        self.view2 = self.w2.addViewBox()
        self.view1.setAspectLocked()
        self.view2.setAspectLocked()
        self.view1.invertY(False)
        self.view2.invertY(False)
        self.layout.addWidget(self.w1, 0, 0)
        self.layout.addWidget(self.w2, 1, 0)

        self.img1 = LabelImageItem()
        self.img2 = LabelImageItem()
        self.view1.addItem(self.img1)
        self.view2.addItem(self.img2)

        self.roi = RulerROI([[10, 64], [120,64]], pen='r')
        self.view1.addItem(self.roi, ignoreBounds=True)
        self.roi.sigRegionChanged.connect(self.updateSlice)

        self.zslider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.zslider.valueChanged.connect(self.updateImage)
        self.layout.addWidget(self.zslider, 2, 0)

        self.lut = pg.HistogramLUTWidget()
        self.layout.addWidget(self.lut, 0, 1, 3, 1)

    def setData(self, atlas, label, scale=None):
        if np.isscalar(scale):
            scale = (scale, scale)
        self.atlas = atlas
        self.label = label
        if self.scale != scale:
            self.scale = scale

            # reset ROI position
            with pg.SignalBlock(self.roi.sigRegionChanged, self.updateSlice):
                h1, h2 = self.roi.getHandles()
                p1 = self.view1.mapViewToScene(pg.Point(0, 0))
                if scale is None:
                    scale = (1, 1)
                p2 = self.view1.mapViewToScene(pg.Point(10*scale[0], 0))
                h1.movePoint([p1.x(), p1.y()])
                h2.movePoint([p2.x(), p2.y()])
            
        self.zslider.setMaximum(atlas.shape[0])
        self.updateImage(autoRange=True)
        self.updateSlice()

    def updateImage(self, autoRange=False):
        z = self.zslider.value()
        self.img1.setData(self.atlas[z], self.label[z], scale=self.scale)
        if autoRange:
            self.view1.autoRange(items=[self.img1.atlasImg])

    def updateSlice(self):
        if self.atlas is None:
            return
        atlas = self.roi.getArrayRegion(self.atlas, self.img1.atlasImg, axes=(1,2))
        label = self.roi.getArrayRegion(self.label, self.img1.atlasImg, axes=(1,2), order=0)
        if atlas.size == 0:
            return
        self.img2.setData(atlas, label, scale=self.scale)
        self.view2.autoRange(items=[self.img2.atlasImg])
        self.w1.viewport().repaint()  # repaint immediately to avoid processing more mouse events before next repaint
        self.w2.viewport().repaint()

    def closeEvent(self, ev):
        self.imv1.close()
        self.imv2.close()
        self.data = None


class LabelImageItem(QtGui.QGraphicsItemGroup):
    def __init__(self):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.atlasImg = pg.ImageItem()
        self.labelImg = pg.ImageItem()
        self.atlasImg.setParentItem(self)
        self.labelImg.setParentItem(self)
        self.labelImg.setZValue(10)
        self.labelImg.setOpacity(0.5)
        self.setOverlay(False)
       
        self.labelColors = {}

    def setData(self, atlas, label, scale=None):
        self.labelData = label
        self.atlasData = atlas
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        self.updateImage()

    def setOverlay(self, overlay):
        return
        if overlay:
            self.labelImg.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        else:
            self.labelImg.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

    def updateImage(self):
        self.atlasImg.setImage(self.atlasData, autoLevels=True)
        self.labelImg.setImage(self.makeLabelImage(self.labelData), autoLevels=False)

    def setLabelColors(self, colors):
        self.labelColors = colors

    def makeLabelImage(self, label):
        img = np.zeros(label.shape + (4,), dtype=np.ubyte)




def readNRRDAtlas(nrrdFile=None):
    """
    Download atlas files from:
      http://help.brain-map.org/display/mouseconnectivity/API#API-DownloadAtlas
    """
    import nrrd
    if nrrdFile is None:
        nrrdFile = QtGui.QFileDialog.getOpenFileName(None, "Select NRRD atlas file")

    with pg.BusyCursor():
        data, header = nrrd.read(nrrdFile)

    # convert to ubyte to compress a bit
    np.multiply(data, 255./data.max(), out=data, casting='unsafe')
    data = data.astype('ubyte')

    # data must have axes (anterior, dorsal, right)
    # rearrange axes to fit -- CCF data comes in (posterior, inferior, right) order.
    data = data[::-1, ::-1, :]

    # voxel size in um
    vxsize = 1e-6 * float(header['space directions'][0][0])

    info = [
        {'name': 'anterior', 'values': np.arange(data.shape[0]) * vxsize, 'units': 'm'},
        {'name': 'dorsal', 'values': np.arange(data.shape[1]) * vxsize, 'units': 'm'},
        {'name': 'right', 'values': np.arange(data.shape[2]) * vxsize, 'units': 'm'},
        {'vxsize': vxsize}
    ]
    ma = metaarray.MetaArray(data, info=info)
    return ma


def readNRRDLabels(nrrdFile=None, ontologyFile=None):
    """
    Download label files from:
      http://help.brain-map.org/display/mouseconnectivity/API#API-DownloadAtlas

    Download ontology files from:
      http://api.brain-map.org/api/v2/structure_graph_download/1.json

      see:
      http://help.brain-map.org/display/api/Downloading+an+Ontology%27s+Structure+Graph
      http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies#AtlasDrawingsandOntologies-StructuresAndOntologies

    """

    import nrrd
    if nrrdFile is None:
        nrrdFile = QtGui.QFileDialog.getOpenFileName(None, "Select NRRD label file")

    if ontologyFile is None:
        ontoFile = QtGui.QFileDialog.getOpenFileName(None, "Select ontology label file")


    with pg.BusyCursor():
        data, header = nrrd.read(nrrdFile)

    # data must have axes (anterior, dorsal, right)
    # rearrange axes to fit -- CCF data comes in (posterior, inferior, right) order.
    data = data[::-1, ::-1, :]

    # compress down to uint16
    print "Compressing.."
    d2 = data.view(dtype='int32')
    shift = -d2.min()
    d2 += shift
    data = d2.astype('uint16')

    # voxel size in um
    vxsize = 1e-6 * float(header['space directions'][0][0])

    info = [
        {'name': 'anterior', 'values': np.arange(data.shape[0]) * vxsize, 'units': 'm'},
        {'name': 'dorsal', 'values': np.arange(data.shape[1]) * vxsize, 'units': 'm'},
        {'name': 'right', 'values': np.arange(data.shape[2]) * vxsize, 'units': 'm'},
        {'vxsize': vxsize}
    ]
    ma = metaarray.MetaArray(data, info=info, chunk=(100, 100, 100))
    return ma


def writeFile(data, file):
    dataDir = os.path.dirname(file)
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    data.write(file)


if __name__ == '__main__':

    app = pg.mkQApp()

    v = AtlasViewer()
    v.show()

    atlasFile = "acq4/analysis/atlas/AI_CCF/images/ccf.ma"
    labelFile = "acq4/analysis/atlas/AI_CCF/images/ccf_label.ma"

    if os.path.isfile(atlasFile):
        atlas = metaarray.MetaArray(file=atlasFile)
    else:
        atlas = readNRRDAtlas()
        writeFile(atlas, atlasFile)

    if os.path.isfile(labelFile):
        label = metaarray.MetaArray(file=labelFile)
    else:
        label = readNRRDLabels()
        writeFile(label, labelFile)

    v.setAtlas(atlas)
    v.setLabels(label)
