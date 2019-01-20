import time
import numpy as np
from acq4.util import Qt
from acq4.modules.Module import Module
from acq4.Manager import getManager
from acq4.util.target import Target
from acq4.util.Thread import Thread
from acq4.util.Mutex import Mutex
import acq4.util.debug as debug
import acq4.pyqtgraph as pg

MainForm = Qt.importTemplate('.main_window')


class VoltageImagingModule(Module):
    """
    """
    moduleDisplayName = "Voltage Imaging"
    moduleCategory = "Acquisition"

    def __init__(self, manager, name, config):

        self.patchAttempts = []
        self.jobQueue = JobQueue()
        self._cammod = None
        self._camdev = None
        self._nextPointID = 0

        Module.__init__(self, manager, name, config)

        self.win = Qt.QWidget()
        self.win.resize(1600, 900)
        self.ui = MainForm()
        self.ui.setupUi(self.win)
        self.win.show()

        self.ui.addPointsBtn.toggled.connect(self.addPointsToggled)
        self.ui.removePointsBtn.clicked.connect(self.removePointsClicked)
        self.ui.startBtn.toggled.connect(self.startBtnToggled)

        cam = self.getCameraDevice()
        cam.sigGlobalTransformChanged.connect(self.cameraTransformChanged)

        self.threads = []
        for pipName in config['patchDevices']:
            pip = manager.getDevice(pipName)
            thread = PatchThread(pip, self.jobQueue)
            self.threads.append(thread)
            thread.start()

    def window(self):
        return self.win

    def addPointsToggled(self):
        cammod = self.getCameraModule()
        if self.ui.addPointsBtn.isChecked():
            cammod.window().getView().scene().sigMouseClicked.connect(self.cameraModuleClicked)
        else:
            Qt.disconnect(cammod.window().getView().scene().sigMouseClicked, self.cameraModuleClicked)

    def getCameraModule(self):
        if self._cammod is None:
            manager = getManager()
            mods = manager.listInterfaces('cameraModule')
            if len(mods) == 0:
                raise Exception("Camera module required")
            self._cammod = manager.getModule(mods[0])
        return self._cammod

    def getCameraDevice(self):
        if self._camdev is None:
            manager = getManager()
            camName = self.config.get('imagingDevice', None)
            if camName is None:
                cams = manager.listInterfaces('camera')
                if len(cams) == 1:
                    camName = cams[0]
                else:
                    raise Exception("Single camera device required (found %d) or 'imagingDevice' key in configuration." % len(cams))
            self._camdev = manager.getDevice(camName)
        return self._camdev
    
    def cameraModuleClicked(self, ev):
        if ev.button() != Qt.Qt.LeftButton:
            return

        camera = self.getCameraDevice()
        cameraPos = camera.mapToGlobal([0, 0, 0])

        globalPos = self._cammod.window().getView().mapSceneToView(ev.scenePos())
        globalPos = [globalPos.x(), globalPos.y(), cameraPos[2]]

        self.addPatchAttempt(globalPos)

    def addPatchAttempt(self, position):
        pid = self._nextPointID
        self._nextPointID += 1

        item = Qt.QTreeWidgetItem([str(pid), "", ""])        
        self.ui.pointTree.addTopLevelItem(item)

        target = Target(movable=False)
        self._cammod.window().addItem(target)
        target.setPos(pg.Point(position[:2]))
        target.setDepth(position[2])
        target.setFocusDepth(position[2])

        pa = PatchAttempt(pid, position, item, target)
        item.patchAttempt = pa
        self.patchAttempts.append(pa)

        self.jobQueue.setJobs(self.patchAttempts)

        pa.statusChanged.connect(self.jobStatusChanged)

        return pa

    def removePointsClicked(self):
        sel = self.ui.pointTree.selectedItems()
        for item in sel:
            self.removePatchAttempt(item.patchAttempt)

    def removePatchAttempt(self, pa):
        self.patchAttempts.remove(pa)

        index = self.ui.pointTree.indexOfTopLevelItem(pa.treeItem)
        self.ui.pointTree.takeTopLevelItem(index)

        pa.targetItem.scene().removeItem(pa.targetItem)

    def cameraTransformChanged(self):
        cam = self.getCameraDevice()
        fdepth = cam.mapToGlobal([0, 0, 0])[2]

        for pa in self.patchAttempts:
            pa.targetItem.setFocusDepth(fdepth)

    def startBtnToggled(self):
        if self.ui.startBtn.isChecked():
            self.ui.startBtn.setText("Stop")
            self.jobQueue.setEnabled(True)
        else:
            self.ui.startBtn.setText("Start")
            self.jobQueue.setEnabled(False)

    def quit(self):
        for thread in self.threads:
            thread.stop()

    def jobStatusChanged(self, job, status):
        item = job.treeItem
        item.setText(1, job.pipette.name())
        item.setText(2, status)

    def deviceStatusChanged(self, device, status):
        # todo: implement per-pipette UI
        print("Device status: %s, %s", (device, status))


class PatchAttempt(Qt.QObject):
    """Stores 3D location, status, and results for a point to be patched.
    """
    statusChanged = Qt.Signal(object, object)  # self, status

    def __init__(self, pid, position, treeItem, targetItem):
        Qt.QObject.__init__(self)
        self.pid = pid
        self.position = position
        self.pipette = None
        self.status = None
        self.result = None
        self.treeItem = treeItem
        self.targetItem = targetItem

    def hasStarted(self):
        return self.status is not None

    def setStatus(self, status):
        self.status = status
        self.statusChanged.emit(self, status)

    def assignPipette(self, pip):
        assert self.pipette is None, "Pipette can only be assigned once"
        self.pipette = pip
        self.setStatus("assigned")


class JobQueue(object):
    """Stores a list of jobs and assigns them by request.
    """
    def __init__(self):
        self.jobs = []
        self.enabled = False
        self.positions = np.empty((0, 3))
        self.lock = Mutex(recursive=True)

    def setEnabled(self, en):
        """If enabled, then requestJob() will attempt to return the next available job.
        If disabled, then requestJob() will return None.
        """
        self.enabled = en

    def setJobs(self, jobs):
        with self.lock:
            self.jobs = [j for j in jobs if not j.hasStarted()]
            self.positions = np.array([job.position for job in jobs])

    def requestJob(self, pipette):
        # Simple 1-pipette implementation: return the job nearest to the current pipette position.
        # For multiple pipettes we need to implement something more clever.
        #  (reference implementation just divides jobs by pipette at the beginning, but perhaps we can do better)
        with self.lock:
            if not self.enabled:
                return None
            
            pos = pipette.globalPosition()
            if len(self.jobs) == 0:
                return None
            
            # simulate request blocking 
            time.sleep(1)
            diff = self.positions - np.array(pos).reshape(1, 3)
            dist = (diff**2).sum(axis=1)**0.5
            closest = np.argmin(dist)
            job = self.jobs.pop(closest)
            self.setJobs(self.jobs)
            job.assignPipette(pipette)
            return job


class PatchThread(Thread):
    """Acquires and runs jobs for a single pipette
    """
    statusChanged = Qt.Signal(object, object)

    def __init__(self, dev, jobQueue):
        Thread.__init__(self)
        self.dev = dev
        self.jobQueue = jobQueue
        self.status = "idle"
        self._stop = False

    def setStatus(self, status):
        self.status = status
        self.statusChanged.emit(self, status)

    def stop(self):
        self._stop = True

    def run(self):
        while self._stop is False:
            self.setStatus("requesting next job")
            pa = self.jobQueue.requestJob(self.dev)
            if pa is None:
                # no jobs right now; sleep and try again.
                time.sleep(1)
                continue

            try:
                self.runPatchAttempt(pa)
            except Exception:
                debug.printExc("Error during patch attempt")
                pa.setStatus("error during %s" % pa.status)

        self.setStatus("stopped")

    def runPatchAttempt(self, pa):
        pa.setStatus("running")
        
        self.setStatus("moving to target")
        self.dev.setTarget(pa.position)
        fut = self.dev.goTarget(speed='fast')
        fut.wait()

        self.setStatus("sleeping at target")
        time.sleep(2.0)

        pa.setStatus("done")
