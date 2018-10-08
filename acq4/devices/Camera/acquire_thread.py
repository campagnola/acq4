from __future__ import print_function
from __future__ import with_statement

import time
from acq4.util.Thread import Thread
from acq4.util.Mutex import Mutex
from acq4.util import Qt
import acq4.util.ptime as ptime
from acq4.util.debug import printExc, Profiler
from acq4.util.imaging import Frame


class AcquireThread(Thread):
    """Thread used to collect frames as they arrive from the camera
    and redistribute them as Frame instances. 
    """
    sigNewFrame = Qt.Signal(object)
    sigShowMessage = Qt.Signal(object)
    
    def __init__(self, dev):
        Thread.__init__(self)
        self.dev = dev
        self.camLock = self.dev.camLock
        self.stopThread = False
        self.lock = Mutex()
        self.acqBuffer = None
        self.bufferTime = 5.0
        self.tasks = []
        
        ## This thread does not run an event loop,
        ## so we may need to deliver frames manually to some places
        self.connections = set()
        self.connectMutex = Mutex()
    
    def __del__(self):
        if hasattr(self, 'cam'):
            self.dev.stopCamera()
    
    def start(self, *args):
        self.lock.lock()
        self.stopThread = False
        self.lock.unlock()
        Thread.start(self, *args)
    
    def connectCallback(self, method):
        with self.connectMutex:
            self.connections.add(method)
    
    def disconnectCallback(self, method):
        with self.connectMutex:
            if method in self.connections:
                self.connections.remove(method)
    
    def run(self):
        lastFrameTime = None
        lastFrameId = None

        camState = self.dev._getCameraFrameState()
        exposure = camState['exposure']
        mode = camState['triggerMode']
        
        try:
            self.dev.startCamera()
            
            lastFrameTime = lastStopCheck = ptime.time()
            frameInfo = {}

            while True:
                now = ptime.time()
                frames = self.dev.newFrames()
                
                ## If a new frame is available, process it and inform other threads
                if len(frames) > 0:
                    if lastFrameId is not None:
                        drop = frames[0]['id'] - lastFrameId - 1
                        if drop > 0:
                            print("WARNING: Camera dropped %d frames" % drop)
                        
                    # Get metadata structure to include with this frame
                    info = self.dev._getFrameInfo(cameraState=camState)
                    
                    ## Process all waiting frames. If there is more than one frame waiting, guess the frame times.
                    dt = (now - lastFrameTime) / len(frames)
                    if dt > 0:
                        info['fps'] = 1.0/dt
                    else:
                        info['fps'] = None
                    
                    for frame in frames:
                        frameInfo = info.copy()
                        data = frame.pop('data')
                        frameInfo.update(frame)  # copies 'time' key supplied by camera
                        out = Frame(data, frameInfo)
                        with self.connectMutex:
                            conn = list(self.connections)
                        for c in conn:
                            c(out)
                        self.sigNewFrame.emit(out)
                        
                    lastFrameTime = now
                    lastFrameId = frames[-1]['id']
                    loopCount = 0
                        
                time.sleep(1e-3)
                
                ## check for stop request every 10ms
                if now - lastStopCheck > 10e-3: 
                    lastStopCheck = now
                    
                    ## If no frame has arrived yet, do NOT allow the camera to stop (this can hang the driver)   << bug should be fixed in pvcam driver, not here.
                    self.lock.lock()
                    if self.stopThread:
                        self.stopThread = False
                        self.lock.unlock()
                        break
                    self.lock.unlock()
                    
                    diff = ptime.time()-lastFrameTime
                    if diff > (10 + exposure):
                        if mode == 'Normal':
                            self.dev.noFrameWarning(diff)
                            break
                        else:
                            pass  ## do not exit loop if there is a possibility we are waiting for a trigger
                                
                
            #from debug import Profiler
            #prof = Profiler()
            with self.camLock:
                #self.cam.stop()
                self.dev.stopCamera()
            #prof.mark('      camera stop:')
        except:
            printExc("Error starting camera acquisition:")
            try:
                with self.camLock:
                    #self.cam.stop()
                    self.dev.stopCamera()
            except:
                pass
            self.sigShowMessage.emit("ERROR starting acquisition (see console output)")
        finally:
            pass
        
    def stop(self, block=False):
        #print "AcquireThread.stop: Requesting thread stop, acquiring lock first.."
        with self.lock:
            self.stopThread = True
        #print "AcquireThread.stop: got lock, requested stop."
        #print "AcquireThread.stop: Unlocked, waiting for thread exit (%s)" % block
        if block:
            if not self.wait(10000):
                raise Exception("Timed out waiting for thread exit!")
        #print "AcquireThread.stop: thread exited"

    def reset(self):
        if self.isRunning():
            self.stop()
            if not self.wait(10000):
                raise Exception("Timed out while waiting for thread exit!")
            self.start()
