import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import numpy as np
import json
import acq4.pyqtgraph as pg
import acq4.util.metaarray as metaarray
from collections import OrderedDict
from acq4.pyqtgraph.Qt import QtGui, QtCore
# from acq4.util.volumeSliceView import VolumeSliceView
from acq4.util.rulerRoi import RulerROI
#from builder2Template import Ui_MainWindow

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

        self.displayCtrl = LabelDisplayCtrl(parent=self)
        self.ctrlLayout.addWidget(self.displayCtrl)
        self.displayCtrl.params.sigTreeStateChanged.connect(self.displayCtrlChanged)

        self.labelTree = LabelTree(self)
        self.labelTree.labelsChanged.connect(self.labelsChanged)
        self.ctrlLayout.addWidget(self.labelTree)

    def setLabels(self, label):
        self.label = label
        with pg.SignalBlock(self.labelTree.labelsChanged, self.labelsChanged):
            for rec in label._info[-1]['ontology']:
                self.labelTree.addLabel(*rec)
        self.updateImage()
        self.labelsChanged()

    def setAtlas(self, atlas):
        self.atlas = atlas
        self.updateImage()

    def updateImage(self):
        if self.atlas is None or self.label is None:
            return
        axis = self.displayCtrl.params['Orientation']
        axes = {
            'right': ('right', 'anterior', 'dorsal'),
            'dorsal': ('dorsal', 'right', 'anterior'),
            'anterior': ('anterior', 'right', 'dorsal')
        }[axis]
        order = [self.atlas._interpretAxis(ax) for ax in axes]
        self.displayAtlas = self.atlas.view(np.ndarray).transpose(order)
        self.displayLabel = self.label.view(np.ndarray).transpose(order)
        self.view.setData(self.displayAtlas, self.displayLabel, scale=self.atlas._info[-1]['vxsize'])

    def labelsChanged(self):
        lut = self.labelTree.lookupTable()
        self.view.setLabelLUT(lut)        
        
    def displayCtrlChanged(self, param, changes):
        for param, change, value in changes:
            if param.name() == 'Composition':
                self.view.setOverlay(value == 'Overlay')
            elif param.name() == 'Opacity':
                self.view.setLabelOpacity(value)
        self.updateImage()


class LabelDisplayCtrl(pg.parametertree.ParameterTree):
    def __init__(self, parent=None):
        pg.parametertree.ParameterTree.__init__(self, parent=parent)
        params = [
            {'name': 'Orientation', 'type': 'list', 'values': ['right', 'anterior', 'dorsal']},
            {'name': 'Opacity', 'type': 'float', 'limits': [0, 1], 'value': 0.5, 'step': 0.1},
            {'name': 'Composition', 'type': 'list', 'values': ['Overlay', 'SourceOver']},
        ]
        self.params = pg.parametertree.Parameter(name='params', type='group', children=params)
        self.setParameters(self.params)


class LabelTree(QtGui.QWidget):
    labelsChanged = QtCore.Signal()
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.tree = QtGui.QTreeWidget(self)
        self.layout.addWidget(self.tree, 0, 0)
        self.tree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tree.headerItem().setText(0, "id")
        self.tree.headerItem().setText(1, "name")
        self.tree.headerItem().setText(2, "color")
        self.labelsById = {}
        self.labelsByAcronym = {}
        self.checked = set()
        self.tree.itemChanged.connect(self.itemChange)
        
        self.layerBtn = QtGui.QPushButton('Color by cortical layer')
        self.layout.addWidget(self.layerBtn, 1, 0)
        self.layerBtn.clicked.connect(self.colorByLayer)
        
        self.resetBtn = QtGui.QPushButton('Reset colors')
        self.layout.addWidget(self.resetBtn, 2, 0)
        self.resetBtn.clicked.connect(self.resetColors)

    def addLabel(self, id, parent, name, acronym, color):
        item = QtGui.QTreeWidgetItem([acronym, name, ''])
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)

        if parent in self.labelsById:
            root = self.labelsById[parent]['item']
        else:
            root = self.tree.invisibleRootItem()
            
        root.addChild(item)
        
        btn = pg.ColorButton(color=pg.mkColor(color))
        btn.defaultColor = color
        self.tree.setItemWidget(item, 2, btn)
        
        self.labelsById[id] = {'item': item, 'btn': btn}
        item.id = id
        self.labelsByAcronym[acronym] = self.labelsById[id]

        btn.sigColorChanged.connect(self.itemColorChanged)
        # btn.sigColorChanging.connect(self.imageChanged)

    def itemChange(self, item, col):
        checked = item.checkState(0) == QtCore.Qt.Checked
        if checked:
            self.checked.add(item.id)
        else:
            self.checked.remove(item.id)
        self.labelsChanged.emit()

    def itemColorChanged(self, *args):
        self.labelsChanged.emit()

    def lookupTable(self):
        lut = np.zeros((2**16, 4), dtype=np.ubyte)
        for id in self.checked:
            if id >= lut.shape[0]:
                continue
            lut[id] = self.labelsById[id]['btn'].color(mode='byte')
        return lut
    
    def colorByLayer(self, root=None):
        try:
            unblock = False
            if not isinstance(root, pg.QtGui.QTreeWidgetItem):
                self.blockSignals(True)
                unblock = True
                root = self.labelsByAcronym['Isocortex']['item']
                
            name = str(root.text(1))
            if ', layer' in name.lower():
                layer = name.split(' ')[-1]
                layer = {'1': 0, '2': 1, '2/3': 2, '4': 3, '5': 4, '6a': 5, '6b': 6}[layer]
                btn = self.labelsById[root.id]['btn']
                btn.setColor(pg.intColor(layer, 10))
                root.setCheckState(0, QtCore.Qt.Checked)
                
            for i in range(root.childCount()):
                self.colorByLayer(root.child(i))
        finally:
            if unblock:
                self.blockSignals(False)
                self.labelsChanged.emit()

    def resetColors(self):
        try:
            self.blockSignals(True)
            for k,v in self.labelsById.items():
                v['btn'].setColor(pg.mkColor(v['btn'].defaultColor))
                v['item'].setCheckState(0, QtCore.Qt.Unchecked)
        finally:
            self.blockSignals(False)
            self.labelsChanged.emit()


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
        self.lut.setImageItem(self.img1.atlasImg)
        self.lut.sigLookupTableChanged.connect(self.histlutChanged)
        self.lut.sigLevelsChanged.connect(self.histlutChanged)
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

    def setLabelLUT(self, lut):
        self.img1.setLUT(lut)
        self.img2.setLUT(lut)

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

    def histlutChanged(self):
        self.img2.atlasImg.setLookupTable(self.lut.getLookupTable(n=256))
        self.img2.atlasImg.setLevels(self.lut.getLevels())

    def setOverlay(self, o):
        self.img1.setOverlay(o)
        self.img2.setOverlay(o)
        
    def setLabelOpacity(self, o):
        self.img1.setLabelOpacity(o)
        self.img2.setLabelOpacity(o)


class LabelImageItem(QtGui.QGraphicsItemGroup):
    def __init__(self):
        QtGui.QGraphicsItemGroup.__init__(self)
        self.atlasImg = pg.ImageItem()
        self.labelImg = pg.ImageItem()
        self.atlasImg.setParentItem(self)
        self.labelImg.setParentItem(self)
        self.labelImg.setZValue(10)
        self.labelImg.setOpacity(0.5)
        self.setOverlay(True)
       
        self.labelColors = {}

    def setData(self, atlas, label, scale=None):
        self.labelData = label
        self.atlasData = atlas
        if scale is not None:
            self.resetTransform()
            self.scale(*scale)
        self.atlasImg.setImage(self.atlasData, autoLevels=True)
        self.labelImg.setImage(self.labelData, autoLevels=False)

    def setLUT(self, lut):
        self.labelImg.setLookupTable(lut)

    def setOverlay(self, overlay):
        if overlay:
            self.labelImg.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        else:
            self.labelImg.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

    def setLabelOpacity(self, o):
        self.labelImg.setOpacity(o)

    def setLabelColors(self, colors):
        self.labelColors = colors


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
    global onto, ontology, data, mapping, inds, vxsize, info, ma
    
    import nrrd
    if nrrdFile is None:
        nrrdFile = QtGui.QFileDialog.getOpenFileName(None, "Select NRRD annotation file")

    if ontologyFile is None:
        ontoFile = QtGui.QFileDialog.getOpenFileName(None, "Select ontology file (json)")

    # Read ontology and convert to flat table
    onto = json.load(open(ontoFile, 'rb'))
    onto = parseOntology(onto['msg'][0])
    l1 = max([len(row[2]) for row in onto])
    l2 = max([len(row[3]) for row in onto])
    ontology = np.array(onto, dtype=[('id', 'int32'), ('parent', 'int32'), ('name', 'S%d'%l1), ('acronym', 'S%d'%l2), ('color', 'S6')])    

    # read annotation data
    with pg.BusyCursor():
        data, header = nrrd.read(nrrdFile)

    # data must have axes (anterior, dorsal, right)
    # rearrange axes to fit -- CCF data comes in (posterior, inferior, right) order.
    data = data[::-1, ::-1, :]

    # compress down to uint16
    print "Compressing.."
    u = np.unique(data)
    next_id = 2**16-1
    mapping = OrderedDict()
    inds = set()
    for i in u[u<=2**16-1]:
        mapping[i] = i
        inds.add(i)
   
    with pg.ProgressDialog("Remapping annotations to 16-bit...", 0, (u>2**16-1).sum()) as dlg:
        for i in u[u>2**16-1]:
            while next_id in inds:
                next_id -= 1
            mapping[i] = next_id
            inds.add(next_id)
            data[data == i] = next_id
            ontology['id'][ontology['id'] == i] = next_id
            ontology['parent'][ontology['parent'] == i] = next_id
        dlg += 1
    data = data.astype('uint16')
    mapping = np.array(list(mapping.items()))    
    
 
    # voxel size in um
    vxsize = 1e-6 * float(header['space directions'][0][0])

    info = [
        {'name': 'anterior', 'values': np.arange(data.shape[0]) * vxsize, 'units': 'm'},
        {'name': 'dorsal', 'values': np.arange(data.shape[1]) * vxsize, 'units': 'm'},
        {'name': 'right', 'values': np.arange(data.shape[2]) * vxsize, 'units': 'm'},
        {'vxsize': vxsize, 'ai_ontology_map': mapping, 'ontology': ontology}
    ]
    ma = metaarray.MetaArray(data, info=info)
    return ma


def parseOntology(root, parent=-1):
    ont = [(root['id'], parent, root['name'], root['acronym'], root['color_hex_triplet'])]
    for child in root['children']:
        ont += parseOntology(child, root['id'])
    return ont


def writeFile(data, file, **kwds):
    dataDir = os.path.dirname(file)
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    data.write(file, **kwds)


if __name__ == '__main__':

    app = pg.mkQApp()

    v = AtlasViewer()
    v.show()

    atlasFile = "acq4/analysis/atlas/AI_CCF/images/ccf.ma"
    labelFile = "acq4/analysis/atlas/AI_CCF/images/ccf_label.ma"

    if os.path.isfile(atlasFile):
        atlas = metaarray.MetaArray(file=atlasFile, readAllData=True)
    else:
        atlas = readNRRDAtlas()
        writeFile(atlas, atlasFile)

    if os.path.isfile(labelFile):
        label = metaarray.MetaArray(file=labelFile, readAllData=True)
    else:
        label = readNRRDLabels()
        writeFile(label, labelFile, chunks=(200,200,200))

    v.setAtlas(atlas)
    v.setLabels(label)
