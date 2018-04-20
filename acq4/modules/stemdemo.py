import time
import pyaudio
import numpy as np
from acq4.modules.Module import Module
import acq4.pyqtgraph as pg


class STEMDemo(Module):
    def __init__(self, manager, name, config):
        Module.__init__(self, manager, name, config)

        self.pip = manager.getDevice('Sensapex2')
        self.center = np.array([0, 0, 0])
        self.radius = 15e-3
        self.cellDensity = 10. / 1e-3**3  # 5 cells per mm^3
        self.cellRadius = 0.4e-3
        self.resetCells()
        self.setCenter()
        
        self.sampleRate = 8000
        self.duration = 8.0
        self.buffer = np.zeros(int(self.duration * self.sampleRate))
        self.timeVals = np.linspace(-self.duration, 0, len(self.buffer))
        self.updateTime = time.time()

        self.win = pg.GraphicsLayoutWidget()
        self.plot = self.win.addPlot(labels={'left': ('Pipette Voltage', 'V'), 'bottom': ('Time', 's')})
        self.plot.setYRange(-100e-3, 50e-3)
        self.plot.setDownsampling(auto=True, mode='peak')
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
        
        self.status = pg.QtGui.QLabel("")
        self.layout.addWidget(self.status, 2, 0)
        
        self.ctrl.show()
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(50)
        
        self.audioWritePtr = 0
        self.audioReadPtr = 0
        self.pyaudio = pyaudio.PyAudio()
        self.bufSize = 256
        self.audioBuffer = np.zeros(self.bufSize*100000, dtype='int16')
        self.stream = self.pyaudio.open(
            format=self.pyaudio.get_format_from_width(2),
            channels=1,
            rate=self.sampleRate,
            output=True,
            stream_callback=self.audioCallback,
            frames_per_buffer=self.bufSize,
        )
        self.stream.start_stream()

    def setCenter(self):
        self.center = np.array(self.pip.globalPosition())

    def resetCells(self):
        vol = self.radius**3
        density = self.cellDensity
        nCells = int(vol * density)
        pos = (np.random.random(size=(nCells, 3)) * (2 * self.radius)) - self.radius
        dist = ((pos**2).sum(axis=1))**0.5
        mask = dist < self.radius
        pos = pos[mask]
        self.cellPos = pos
        self.vRest = np.random.normal(size=len(pos), loc=-70e-3, scale=4e-3)
        cellType = (np.random.random(size=len(pos)) > 0.5).astype(int)
        self.spikeRate = (2 + cellType*20) * 1.1**np.random.normal(size=len(pos), scale=0.5)
        
    def updatePlot(self):
        now = time.time()
        dt = now - self.updateTime
        self.updateTime = now
        
        pos = np.array(self.pip.globalPosition()) - self.center
        centerDist = np.linalg.norm(pos)
        diff = pos[None, :] - self.cellPos
        dist2 = (diff**2).sum(axis=1)
        i = np.argmin(dist2)
        if centerDist < self.radius:
            self.status.setText("%0.2g  %0.2g  IN" % (centerDist, dist2[i]**0.5))
        else:
            self.status.setText("%0.2g  OUT" % centerDist)
        cellRadius = self.cellRadius
        
        sampleRate = self.sampleRate
        duration = dt
        chunkSize = int(duration * sampleRate)
        if dist2[i] < cellRadius**2:
            chunk = np.empty(chunkSize)
            chunk[:] = self.vRest[i]
            spikes = poissonProcess(self.spikeRate[i], duration)
            spikeInds = (spikes * sampleRate).astype('uint')
            spikeInds = spikeInds[spikeInds < chunkSize-1]
            spikeAmps = np.random.normal(size=len(spikeInds), loc=100e-3, scale=5e-3)
            chunk[spikeInds] += spikeAmps
            chunk[spikeInds+1] -= spikeAmps * 0.2
        else:
            chunk = np.zeros(chunkSize)

        chunk += np.random.normal(size=chunkSize, scale=1e-3)
        buf = np.roll(self.buffer, -chunkSize)
        buf[-chunkSize:] = chunk
        self.buffer = buf
        
        audio = chunk * 2**16
        ptr = self.audioWritePtr % len(self.audioBuffer)
        writeSize = min(len(self.audioBuffer) - ptr, len(audio))
        self.audioBuffer[ptr:ptr+writeSize] = audio[:writeSize]
        if writeSize < len(audio):
            self.audioBuffer[:len(audio)-writeSize] = audio[writeSize:]
        self.audioWritePtr += len(audio)
        
        self.plot.plot(self.timeVals, self.buffer, clear=True)

    def audioCallback(self, data, frameCount, timeInfo, status):
        self.audioReadPtr = max(self.audioReadPtr, self.audioWritePtr - frameCount*3)
        readPtr = self.audioReadPtr
        writePtr = self.audioWritePtr
        framesAvailable = writePtr - readPtr
            
        if framesAvailable >= frameCount:
            readPtr = readPtr % len(self.audioBuffer)
            audio = self.audioBuffer[readPtr:readPtr+frameCount]
            self.audioReadPtr += frameCount
        else:
            # underrun; just re-use some older buffer
            readPtr = (writePtr - frameCount) % len(self.audioBuffer)
            audio = self.audioBuffer[readPtr:readPtr+frameCount]
            self.audioReadPtr += framesAvailable
            
        if len(audio) < frameCount:
            audio = np.contatenate([audio, np.zeros(frameCount - len(audio), dtype=audio.dtype)])
            
        return audio, pyaudio.paContinue
        


        
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
