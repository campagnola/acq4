from acq4.modules.Module import Module
import acq4.pyqtgraph as pg
import numpy as np


class STEMDemo(Module):
    def __init__(self, manager, name, config):
        Module.__init__(self, manager, name, config)

        self.pip = manager.getDevice('Sensapex2')
        self.center = np.array([0, 0, 0])
        self.radius = 15e-3
        self.resetCells()
        self.setCenter()
        
        self.buffer = np.zeros(5000)

        self.win = pg.GraphicsLayoutWidget()
        self.plot = self.win.addPlot()
        self.win.show()
        
        self.ctrl = pg.QtGui.QWidget()
        self.layout = pg.QtGui.QGridLayout()
        self.ctrl.setLayout(self.layout)
        
        self.centerBtn = pg.QtGui.QPushButton("set center")
        self.centerBtn.clicked.connect(self.setCenter)
        self.layout.addWidget(self.centerBtn, 0, 0)
        
        self.resetBtn = pg.QtGui.QPushButton("reset cells")
        self.resetBtn.clicked.connect(self.resetCells)
        self.layout.addWidget(self.resetBtn, 1, 0)
        
        self.ctrl.show()
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(30)

    def setCenter(self):
        self.center = np.array(self.pip.globalPosition())

    def resetCells(self):
        vol = self.radius**3
        density = 1. / 1e-3**3  # 1 cell per mm^3
        nCells = int(vol * density)
        pos = (np.random.random(size=(nCells, 3)) * (2 * self.radius)) - self.radius
        dist = ((pos**2).sum(axis=1))**0.5
        mask = dist < self.radius
        pos = pos[mask]
        self.cellPos = pos
        self.vRest = np.random.normal(size=len(pos), loc=-70e-3, scale=4e-3)
        cellType = (np.random.random(size=len(pos)) > 0.5).astype(int)
        self.spikeRate = (4 + cellType*20) * 1.1**np.random.normal(size=len(pos), scale=0.5)
        
    def updatePlot(self):
        pos = np.array(self.pip.globalPosition()) - self.center
        diff = pos[None, :] - self.cellPos
        dist2 = (diff**2).sum(axis=1)
        i = np.argmin(dist2)
        print(dist2[i])
        cellRadius = 0.5e-3
        
        sampleRate = len(self.buffer) / 4.0
        duration = 1/30.
        chunkSize = int(duration * sampleRate)
        if dist2[i] < cellRadius**2:
            chunk = np.empty(chunkSize)
            chunk[:] = self.vRest[i]
            spikes = poissonProcess(self.spikeRate[i], duration)
            spikeInds = (spikes * sampleRate).astype('uint')
            spikeInds = spikeInds[spikeInds < chunkSize]
            chunk[spikeInds] += 120e-3
            chunk[spikeInds+1] -= 20e-3
        else:
            chunk = np.zeros(chunkSize)

        chunk += np.random.normal(size=chunkSize, scale=5e-3)
        buf = np.roll(self.buffer, -chunkSize)
        buf[-chunkSize:] = chunk
        self.buffer = buf
        
        self.plot.plot(self.buffer, clear=True)

        
        
def poissonProcess(rate, tmax=None, n=None):
    """Simulate a poisson process; return a list of event times"""
    events = []
    t = 0
    while True:
        t += np.random.exponential(1./rate)
        if tmax is not None and t > tmax:
            break
        events.append(t)
        if n is not None and len(events) >= n:
            break
    return np.array(events)
