# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import with_statement

import time
from numpy import *
import acq4.pyqtgraph as pg
from acq4.util.Mutex import Mutex
from acq4.devices.Microscope import Microscope
from acq4.util import Qt
from acq4.util.metaarray import MetaArray
import acq4.util.ptime as ptime
from acq4.util.Mutex import Mutex
from acq4.util.debug import printExc, Profiler
from acq4.util import imaging
from acq4.util.imaging.frame import Frame
from acq4.pyqtgraph import Vector, SRTTransform3D
from acq4.devices.DAQGeneric import DAQGeneric, DAQGenericTask
from acq4.devices.OptomechDevice import OptomechDevice

from .taskGUI import CameraTaskGui
from .deviceGUI import CameraDeviceGui
from .acquire_thread import AcquireThread
from .CameraInterface import CameraInterface


class Camera(DAQGeneric, OptomechDevice):
    """Generic camera device class. All cameras should extend from this interface.
     - The class handles acquisition tasks, scope integration, expose/trigger lines
     - Subclasses should handle the connection to the camera driver by overriding
        listParams, getParams, and setParams.
     - Subclasses may need to create their own AcquireThread

    The list/get/setParams functions should implement a few standard items:
    (Note: these number values are just examples, but the data types and strings must be the same.)
        triggerMode:     str, ['Normal', 'TriggerStart', 'Strobe', 'Bulb']
        exposure:        float, (0.0, 10.0)
        binning:         (int,int) , [[1,2,4,8,16], [1,2,4,8,16]]
        region:          (int, int, int, int), [(0, 511), (0, 511), (1, 512), (1, 512)] #[x, y, w, h]
        gain:            float, (0.1, 10.0)

    The configuration for these devices should look like:
    (Note that each subclass will add config options for identifying the camera)
        scopeDevice: 'Microscope'
        scaleFactor: (1.0, 1.0)  ## used for rectangular pixels
        exposeChannel: 'DAQ', '/Dev1/port0/line14'  ## Channel for recording expose signal
        triggerOutChannel: 'DAQ', '/Dev1/PFI5'  ## Channel the DAQ should trigger off of to sync with camera
        triggerInChannel: 'DAQ', '/Dev1/port0/line13'  ## Channel the DAQ should raise to trigger the camera
        params:
            GAIN_INDEX: 2
            CLEAR_MODE: 'CLEAR_PRE_SEQUENCE'  ## Overlap mode for QuantEM
    """

    sigCameraStopped = Qt.Signal()
    sigCameraStarted = Qt.Signal()
    sigShowMessage = Qt.Signal(object)  # (string message)
    sigNewFrame = Qt.Signal(object)  # (frame data)
    sigParamsChanged = Qt.Signal(object)

    def __init__(self, dm, config, name):
        OptomechDevice.__init__(self, dm, config, name)

        self.lock = Mutex(Mutex.Recursive)
        
        # Generate config to use for DAQ 
        daqConfig = {}
        if 'exposeChannel' in config:
            daqConfig['exposure'] = config['exposeChannel']
        if 'triggerInChannel' in config:
            daqConfig['trigger'] = config['triggerInChannel']
        DAQGeneric.__init__(self, dm, daqConfig, name)
        
        self.camConfig = config
        self.stateStack = []
                
        if 'scaleFactor' not in self.camConfig:
            self.camConfig['scaleFactor'] = [1., 1.]
        
        ## Default values for scope state. These will be used if there is no scope defined.
        self.scopeState = {
            'id': 0,
        }

        # Caching for frame metadata
        self._lastFrameState = None
        self._lastFrameInfo = None

        # Watch for state changes from microscope device
        self.scopeDev = None
        p = self
        while p is not None:
            p = p.parentDevice()
            if isinstance(p, Microscope):
                self.scopeDev = p
                self.scopeDev.sigObjectiveChanged.connect(self.objectiveChanged)
                self.scopeDev.sigLightChanged.connect(self._lightChanged)
                break

        # Watch for optical state changes
        self.sigGlobalOpticsChanged.connect(self._opticsChanged)

        # Initialize scope state variables
        self.transformChanged()
        if self.scopeDev is not None:
            self.objectiveChanged()
            self._lightChanged()
        self._opticsChanged()

        # Initialize camera
        self.setupCamera()

        # initialize transform from sensor size
        self.sensorSize = self.getParam('sensorSize')
        tr = pg.SRTTransform3D()
        tr.translate(-self.sensorSize[0]*0.5, -self.sensorSize[1]*0.5)
        self.setDeviceTransform(self.deviceTransform() * tr)
        
        # set up streaming frame acquisition thread
        self.acqThread = AcquireThread(self)
        self.acqThread.finished.connect(self.acqThreadFinished)
        self.acqThread.started.connect(self.acqThreadStarted)
        self.acqThread.sigShowMessage.connect(self.showMessage)
        self.acqThread.sigNewFrame.connect(self.newFrame)
        
        # Watch for transformation state changes
        self.sigGlobalTransformChanged.connect(self.transformChanged)
        
        # Set default camera parameters from config 
        if config != None:
            # look for 'defaults', then 'params' to preserve backward compatibility.
            defaults = config.get('defaults', config.get('params', {}))
            try:
                self.setParams(defaults)
            except:
                printExc("Error default setting camera parameters:")

        # set up preset hotkeys
        for name, preset in self.camConfig.get('presets', {}).items():
            if 'hotkey' not in preset:
                continue
            dev = dm.getDevice(preset['hotkey']['device'])
            key = preset['hotkey']['key']
            dev.addKeyCallback(key, self.presetHotkeyPressed, (name,))

        dm.declareInterface(name, ['camera'], self)
    
    def setupCamera(self):
        """Prepare the camera at least so that get/setParams will function correctly"""
        raise NotImplementedError("Function must be reimplemented in subclass.")
    
    def listParams(self, params=None):
        """Return a dictionary of parameter descriptions. By default, all parameters are listed.
        Each description is a tuple or list: (values, isWritable, isReadable, dependencies)
        
        values may be any of:
          - Tuple of ints or floats indicating minimum and maximum values
          - List of int / float / string values
          - Tuple of strings, indicating that the parameter is made up of multiple sub-parameters
             (eg, 'region' should be ('regionX', 'regionY', 'regionW', 'regionH')
             
        dependencies is a list of other parameters which affect the allowable values of this parameter.
        
        eg:
        {  'paramName': ([list of values], True, False, []) }
        """
        raise NotImplementedError("Function must be reimplemented in subclass.")

    def setParams(self, params, autoRestart=True, autoCorrect=True):
        """Set camera parameters. Options are:
           params: a list or dict of (param, value) pairs to be set. Parameters are set in the order specified.
           autoRestart: If true, restart the camera if required to enact the parameter changes
           autoCorrect: If true, correct values that are out of range to their nearest acceptable value
        
        Return a tuple with: 
           0: dictionary of parameters and the values that were set.
              (note this may differ from requested values if autoCorrect is True)
           1: Boolean value indicating whether a restart is required to enact changes.
              If autoRestart is True, this value indicates whether the camera was restarted."""
        raise NotImplementedError("Function must be reimplemented in subclass.")
        
    def getParams(self, params=None):
        raise NotImplementedError("Function must be reimplemented in subclass.")
        
    def setParam(self, param, val, autoCorrect=True, autoRestart=True):
        return self.setParams([(param, val)], autoCorrect=autoCorrect, autoRestart=autoRestart)[0]
        
    def getParam(self, param):
        return self.getParams([param])[param]

    def listPresets(self):
        """Return a list of all preset names.
        """
        return list(self.camConfig.get('presets', {}).keys())

    def loadPreset(self, preset):
        presets = self.camConfig.get('presets', None)
        if presets is None or preset not in presets:
            raise ValueError("No camera preset named %r" % preset)
        params = presets[preset]['params']
        self.setParams(params)

    def presetHotkeyPressed(self, dev, changes, presetName):
        self.loadPreset(presetName)

    def newFrames(self):
        """Returns a list of all new frames that have arrived since the last call. The list looks like:
            [{'id': 0, 'data': array, 'time': 1234678.3213}, ...]
        id is a unique integer representing the frame number since the start of the program.
        data should be a permanent copy of the image (ie, not directly from a circular buffer)
        time is the time of arrival of the frame. Optionally, 'exposeStartTime' and 'exposeDoneTime' 
            may be specified if they are available.
        """
        raise NotImplementedError("Function must be reimplemented in subclass.")
        
    def startCamera(self):
        """Calls the camera driver to start the camera's acquisition."""
        raise NotImplementedError("Function must be reimplemented in subclass.")
        
    def stopCamera(self):
        """Calls the camera driver to stop the camera's acquisition.
        Note that the acquisition may be _required_ to stop, since other processes
        may be preparing to synchronize with the camera's exposure signal."""
        raise NotImplementedError("Function must be reimplemented in subclass.")

    def noFrameWarning(self, time):
        # display a warning message that no camera frames have arrived.
        # This method is only here to allow PVCam to display some useful information.
        print("Camera acquisition thread has been waiting %02f sec but no new frames have arrived; shutting down." % time)
    
    def pushState(self, name=None, params=None):
        if params is None:
            # push all writeable parameters
            params = [param for param, spec in self.listParams().items() if spec[1] is True]
        
        # print("Camera: pushState", name, params)
        params = self.getParams(params)
        params['isRunning'] = self.isRunning()
        self.stateStack.append((name, params))
        
    def popState(self, name=None):
        #print "Camera: popState", name
        if name is None:
            state = self.stateStack.pop()[1]
        else:
            inds = [i for i in range(len(self.stateStack)) if self.stateStack[i][0] == name]
            if len(inds) == 0:
                raise Exception("Can not find camera state named '%s'" % name)
            state = self.stateStack[inds[-1]][1]
            self.stateStack = self.stateStack[:inds[-1]]
            
        run = state['isRunning']
        del state['isRunning']
        #print "Camera: popState", name, state
        nv, restart = self.setParams(state, autoRestart=False)
        #print "    run:", run, "isRunning:", self.isRunning(), "restart:", restart
        
        if self.isRunning():
            if run:
                if restart:
                    self.restart()
            else:
                self.stop()
        else:
            if run:
                self.start()

    def start(self, block=True):
        """Start camera and acquisition thread"""
        #print "Camera: start"
        #sys.stdout.flush()
        #time.sleep(0.1)
        self.acqThread.start()
        
    def stop(self, block=True):
        """Stop camera and acquisition thread"""
        #print "Camera: stop"
        #sys.stdout.flush()
        #time.sleep(0.1)
        self.acqThread.stop(block=block)
        
    def acquireFrames(self, n=1, stack=True):
        """Immediately acquire and return a specific number of frames.

        This method blocks until all frames are acquired and may not be supported by all camera
        types.

        All frames are returned stacked within a single Frame instance, as a 3D or 4D array.

        If *stack* is False, then the first axis is dropped and the resulting data will instead be
        2D or 3D.
        """
        if n > 1 and not stack:
            raise ValueError("Using stack=False is only allowed when n==1.")

        # TODO: Add a non-blocking mode that returns a Future.
        frames = self._acquireFrames(n)
        now = ptime.time()
        if not stack:
            frames = frames[0]

        info = self._makeFrameInfo()
        info['time'] = now
        return Frame(frames, info)

    def _acquireFrames(self, n):
        # todo: default implementation can use acquisition thread instead..
        raise NotImplementedError("Camera class %s does not implement this method." % self.__class__.__name__)

    def restart(self):
        if self.isRunning():
            self.stop()
            self.start()
    
    def quit(self):
        #print "quit() called from Camera"
        if hasattr(self, 'acqThread') and self.isRunning():
            self.stop()
            if not self.wait(10000):
                raise Exception("Timed out while waiting for thread exit!")
        #self.cam.close()
        DAQGeneric.quit(self)
        #print "Camera device quit."
        
    #@ftrace
    def createTask(self, cmd, parentTask):
        with self.lock:
            return CameraTask(self, cmd, parentTask)
    
    #@ftrace
    def getTriggerChannel(self, daq):
        with self.lock:
            if not 'triggerOutChannel' in self.camConfig:
                return None
            if self.camConfig['triggerOutChannel']['device'] != daq:
                return None
            return self.camConfig['triggerOutChannel']['channel']

    def taskInterface(self, taskRunner):
        return CameraTaskGui(self, taskRunner)

    def deviceInterface(self, win):
        return CameraDeviceGui(self, win)

    def cameraModuleInterface(self, mod):
        return CameraInterface(self, mod)
    
    ### Scope interface functions below
        
    #@ftrace
    def getPixelSize(self):
        """Return the absolute size of 1 pixel"""
        with self.lock:
            return self.scopeState['pixelSize']
        
    #@ftrace
    def getObjective(self):
        with self.lock:
            return self.scopeState['objective']

    def getScopeDevice(self):
        with self.lock:
            return self.scopeDev
            
    def getBoundary(self, globalCoords=True):
        """Return the boundaries of the camera sensor in global coordinates.
        If globalCoords==False, return in local coordinates.
        """
        size = self.getParam('sensorSize')
        bounds = Qt.QPainterPath()
        bounds.addRect(Qt.QRectF(0, 0, *size))
        if globalCoords:
            return pg.SRTTransform(self.globalTransform()).map(bounds)
        else:
            return bounds
        
    def getBoundaries(self):
        """Return a list of camera boundaries for all objectives"""
        objs = self.scopeDev.listObjectives()
        return [self.getBoundary(o) for o in objs]
    
    def mapToSensor(self, pos):
        """Return the sub-pixel location on the sensor that corresponds to global position pos"""
        ss = self.getScopeState()
        boundary = self.getBoundary()
        boundary.translate(*ss['scopePosition'][:2])
        size = self.sensorSize
        x = (pos[0] - boundary.left()) * (float(size[0]) / boundary.width())
        y = (pos[1] - boundary.top()) * (float(size[1]) / boundary.height())
        return (x, y)

    def _getCameraFrameState(self):
        """Return a standard set of camera parameters to be used for constructing Frame metadata.
        """
        params = ['binning', 'exposure', 'region', 'triggerMode']
        return dict(self.getParams(params))

    def _getScopeState(self):
        """Return meta information about microscope state to be included with each frame. 

        This function must be fast.
        """
        with self.lock:
            return self.scopeState

    def _getFrameInfo(self, cameraState=None, scopeState=None):
        """Return metadata to be returned with a recently acquired frame.

        Does not include 'fps' and 'time' keys; these must be setby the caller. 

        This function must be fast.
        """
        if cameraState is None:
            cameraState = self._getCameraFrameState()
        
        if scopeState is None:
            scopeState = self._getScopeState()

        # generate new frame info structure only if necessary  
        frameState = {'ssid': scopeState['id']}
        frameState.update(cameraState)
        if frameState != self._lastFrameState:
            frameInfo = cameraState

            ps = scopeState['pixelSize']  ## size of CCD pixel
            binning = cameraState['binning']

            frameInfo['deviceTransform'] = pg.SRTTransform3D(scopeState['transform'])
            frameInfo['pixelSize'] = [ps[0] * binning[0], ps[1] * binning[1]]
            frameInfo['objective'] = scopeState.get('objective', None)
            frameInfo['illumination'] = scopeState.get('illumination', None)
            frameInfo['optics'] = scopeState.get('optics', None)

            ## make frame transform to map from image coordinates to sensor coordinates.
            ## (these may differ due to binning and region of interest settings)
            tr = self.makeFrameTransform(cameraState['region'], cameraState['binning'])
            frameInfo['frameTransform'] = tr

            self._lastFrameState = frameState
            self._lastFrameInfo = frameInfo

        return self._lastFrameInfo

    def transformChanged(self):  ## called then this device's global transform changes.
        prof = Profiler(disabled=True)
        with self.lock:
            self.scopeState['transform'] = self.globalTransform()
            o = Vector(self.scopeState['transform'].map(Vector(0,0,0)))
            p = Vector(self.scopeState['transform'].map(Vector(1, 1)) - o)
            self.scopeState['centerPosition'] = o
            self.scopeState['pixelSize'] = abs(p)
            self.scopeState['id'] += 1  ## hint to acquisition thread that state has changed
        
    def objectiveChanged(self, obj=None):
        if obj is None:
            obj = self.scopeDev.getObjective()
        else:
            obj, oldObj = obj
        with self.lock:
            self.scopeState['objective'] = obj.name()
            self.scopeState['id'] += 1

    def _opticsChanged(self):
        with self.lock:
            self.scopeState['optics'] = self.listGlobalOptics()
            self.scopeState['id'] += 1

    def _lightChanged(self):
        with self.lock:
            if self.scopeDev.lightSource is None:
                return
            self.scopeState['illumination'] = self.scopeDev.lightSource.describe()
            self.scopeState['id'] += 1

    @staticmethod 
    def makeFrameTransform(region, binning):
        """Make a transform that maps from image coordinates to whole-sensor coordinates,
        given the region-of-interest and binning used to acquire the image."""
        tr = SRTTransform3D()
        tr.translate(*region[:2])
        tr.scale(binning[0], binning[1], 1)
        return tr
        
    ### Proxy signals and functions for acqThread:
    ###############################################
    
    def acqThreadFinished(self):
        self.sigCameraStopped.emit()

    def acqThreadStarted(self):
        self.sigCameraStarted.emit()

    def showMessage(self, msg):
        self.sigShowMessage.emit(msg)

    def newFrame(self, data):
        self.sigNewFrame.emit(data)
        
    def isRunning(self):
        return self.acqThread.isRunning()

    def wait(self, *args, **kargs):
        return self.acqThread.wait(*args, **kargs)
    
        
class CameraTask(DAQGenericTask):
    """Default implementation of camera acquisition task.

    Some of these methods may need to be reimplemented for subclasses.
    """

    def __init__(self, dev, cmd, parentTask):
        #print "Camera task:", cmd
        daqCmd = {}
        if 'channels' in cmd:
            daqCmd = cmd['channels']
        DAQGenericTask.__init__(self, dev, daqCmd, parentTask)
        
        self.__startOrder = [], []
        self.camCmd = cmd
        self.lock = Mutex()
        self.recordHandle = None
        self.stopAfter = False
        self.stoppedCam = False
        self.returnState = {}
        self.frames = []
        self.recording = False
        self.stopRecording = False
        self.resultObj = None
        
    def configure(self):
        ## Merge command into default values:
        prof = Profiler('Camera.CameraTask.configure', disabled=True)
        #print "CameraTask.configure"
        
        ## set default parameters, load params from command
        params = {
            'triggerMode': 'Normal',
        }
        params.update(self.camCmd['params'])
        
        ## If we are sending a one-time trigger to start the camera, then it must be restarted to arm the trigger
        ## (bulb and strobe modes only require a restart if the trigger mode is not already set; this is handled later)
        if params['triggerMode'] == 'TriggerStart':
            restart = True
            
        ## If the DAQ is triggering the camera, then the camera must start before the DAQ
        if params['triggerMode'] != 'Normal':
            daqName = self.dev.camConfig['triggerInChannel']['device']
            self.__startOrder[1].append(daqName)
            
            ## Make sure we haven't requested something stupid..
            if self.camCmd.get('triggerProtocol', False) and self.dev.camConfig['triggerOutChannel']['device'] == daqName:
                raise Exception("Task requested camera to trigger and be triggered by the same device.")

        if 'pushState' in self.camCmd:
            stateName = self.camCmd['pushState']
            self.dev.pushState(stateName, params=list(params.keys()))
        prof.mark('push params onto stack')

        (newParams, paramsNeedRestart) = self.dev.setParams(params, autoCorrect=True, autoRestart=False)  ## we'll restart in a moment if needed..
        restart = restart or paramsNeedRestart
        prof.mark('set params')

        ## If the camera is triggering the daq, stop acquisition now and request that it starts after the DAQ
        ##   (daq must be started first so that it is armed to received the camera trigger)
        name = self.dev.name()
        if self.camCmd.get('triggerProtocol', False):
            restart = True
            daqName = self.dev.camConfig['triggerOutChannel']['device']
            self.__startOrder = [daqName], []
            prof.mark('conf 1')
            
        ## We want to avoid this if at all possible since it may be very expensive
        if restart:
            self.dev.stop(block=True)
        prof.mark('stop')
            
        ## connect using acqThread's connect method because there may be no event loop
        ## to deliver signals here.
        self.dev.acqThread.connectCallback(self.newFrame)
        
        ## Call the DAQ configure
        DAQGenericTask.configure(self)
        prof.mark('DAQ configure')
        prof.finish()
        
    def getStartOrder(self):
        order = DAQGenericTask.getStartOrder(self)
        return order[0]+self.__startOrder[0], order[1]+self.__startOrder[1]
            
    def newFrame(self, frame):
        disconnect = False
        with self.lock:
            if self.recording:
                self.frames.append(frame)
            if self.stopRecording:
                self.recording = False
                disconnect = True
        if disconnect:   ## Must be done only after unlocking mutex
            self.dev.acqThread.disconnectCallback(self.newFrame)

    def start(self):
        ## arm recording
        self.frames = []
        self.stopRecording = False
        self.recording = True
            
        if not self.dev.isRunning():
            self.dev.start(block=True)  ## wait until camera is actually ready to acquire
            
        ## Last I checked, this does nothing. It should be here anyway, though..
        DAQGenericTask.start(self)
    
    def isDone(self):
        ## If camera stopped, then probably there was a problem and we are finished.
        if not self.dev.isRunning():
            return True    
        
        ## should return false if recording is required to run for a specific time.
        if 'minFrames' in self.camCmd:
            with self.lock:
                if len(self.frames) < self.camCmd['minFrames']:
                    return False
        return DAQGenericTask.isDone(self)  ## Should return True.
        
    def stop(self, abort=False):
        ## Stop DAQ first
        #print "Stop camera task"
        DAQGenericTask.stop(self, abort=abort)
        
        with self.lock:
            self.stopRecording = True
        
        if 'popState' in self.camCmd:
            self.dev.popState(self.camCmd['popState'])  ## restores previous settings, stops/restarts camera if needed
                
    def getResult(self):
        if self.resultObj is None:
            daqResult = DAQGenericTask.getResult(self)
            self.resultObj = CameraTaskResult(self, self.frames[:], daqResult)
        return self.resultObj
        
    def storeResult(self, dirHandle):
        result = self.getResult()
        result = {'frames': (result.asMetaArray(), result.info()), 'daqResult': (result.daqResult(), {})}
        dh = dirHandle.mkdir(self.dev.name())
        for k in result:
            data, info = result[k]
            if data is not None:
                dh.writeFile(data, k, info=info)


class CameraTaskResult:
    def __init__(self, task, frames, daqResult):
        self.lock = Mutex(recursive=True)
        self._task = task
        self._frames = frames
        self._daqResult = daqResult
        self._marr = None
        self._arr = None
        self._frameTimes = None
        self._frameTimesPrecise = False
        
    def frames(self):
        """Return a list of Frame instances collected during the task"""
        return self._frames[:]
    
    def info(self):
        """Return meta-info for the first frame recorded or {} if there were no frames."""
        if len(self._frames) == 0:
            return {}
        info = self._frames[0].info().copy()
        info.update({'preciseTiming': self._frameTimesPrecise})
        return info
    
    def asArray(self):
        with self.lock:
            if self._arr is None:
                #data = self._frames
                if len(self._frames) > 0:
                    self._arr = concatenate([f.data()[newaxis,...] for f in self._frames])
        return self._arr
    
    def asMetaArray(self):
        """Return a MetaArray containing all frame and timing data"""
        with self.lock:
            if self._marr is None:
                arr = self.asArray()
                if arr is not None:
                    times, precise = self.frameTimes()
                    times = times[:arr.shape[0]]
                    info = [axis(name='Time', units='s', values=times), axis(name='x'), axis(name='y'), self.info()]
                    #print info
                    self._marr = MetaArray(arr, info=info)
            
        return self._marr
            
    def daqResult(self):
        """Return results of DAQ channel recordings"""
        return self._daqResult

    def frameTimes(self):
        if self._frameTimes is None:
            ## generate MetaArray of images collected during recording
            times = None
            precise = False # becomes True if we are able to determine precise frame times.
            with self.lock:
                if len(self._frames) > 0:  ## extract frame times as reported by camera. This is a first approximation.
                    try:
                        times = array([f.info()['time'] for f in self._frames])
                    except:
                        print(f)
                        raise
                    times -= times[0]
                else:
                    return None
                
                expose = None
                daqResult = self._daqResult
                if daqResult is not None and daqResult.hasColumn('Channel', 'exposure'):
                    expose = daqResult['Channel':'exposure']
                
            ## Correct times for each frame based on data recorded from exposure channel.
            if expose is not None: 
            
                ## Extract times from trace
                ex = expose.view(ndarray).astype(int32)
                exd = ex[1:] - ex[:-1]
                
                timeVals = expose.xvals('Time')
                inds = argwhere(exd > 0.5)[:, 0] + 1
                onTimes = timeVals[inds]
                
                ## If camera triggered DAQ, then it is likely we missed the first 0->1 transition
                if self._task.camCmd.get('triggerProtocol', False) and ex[0] > 0.5:
                    onTimes = array([timeVals[0]] + list(onTimes))
                
                #print "onTimes:", onTimes
                inds = argwhere(exd < 0.5)[:, 0] + 1
                offTimes = timeVals[inds]
                
                ## Determine average frame transfer time
                txLen = (offTimes[:len(times)] - times[:len(offTimes)]).mean()
                
                ## Determine average exposure time (excluding first frame, which is often shorter)
                expLen = (offTimes[1:len(onTimes)] - onTimes[1:len(offTimes)]).mean()
                
                if self._task.camCmd['params'].get('triggerMode', 'Normal') == 'Normal' and not self._task.camCmd.get('triggerProtocol', False):
                    ## Can we make a good guess about frame times even without having triggered the first frame?
                    ## frames are marked with their arrival time. We will assume that a frame most likely 
                    ## corresponds to the last complete exposure signal. 
                    pass
                    
                elif len(onTimes) > 0:
                    ## If we triggered the camera (or if the camera triggered the DAQ), 
                    ## then we know frame 0 occurred at the same time as the first expose signal.
                    ## New times list is onTimes, any extra frames just increment by tx+exp time
                    times[:len(onTimes)] = onTimes[:len(times)]  ## set the times for which we detected an exposure pulse
                    
                    ## Try to determine mean framerate
                    if len(onTimes) > 1:
                        framePeriod = (onTimes[-1] - onTimes[0]) / (len(onTimes) - 1)
                    else:
                        framePeriod = (times[-1] - times[0]) / (len(times) - 1)
                        
                    ## For any extra frames that did not have an exposure signal, just try
                    ## to guess the correct time based on the average framerate.
                    lastTime = onTimes[-1]
                    if framePeriod is not None:
                        for i in range(len(onTimes), len(times)):
                            lastTime += framePeriod
                            times[i] = lastTime
                            
                    precise = True
                
            self._frameTimes = times
            self._frameTimesPrecise = precise
            
        return self._frameTimes, self._frameTimesPrecise
