from __future__ import print_function
from acq4.util import Qt
from acq4.util.Mutex import Mutex
from acq4.devices.Device import Device
from acq4.drivers.sensapex.SensapexZeissSDK import SensapexZeiss


class ZeissObjectiveSwitch(Device):

    sigSwitchChanged = Qt.Signal(object, object)  # self, {switch_name: value, ...}

    def __init__(self, dm, config, name):
        Device.__init__(self, dm, config, name)
        self.lock = Mutex(Qt.QMutex.Recursive)

        self.zeiss = SensapexZeiss()
        self.mtbRoot = self.zeiss.Connect()
        self.zeiss.GetObjective().registerEvents(self.onObjectivePosChanged, self.onObjectivePosSettled)
        self.currentIndex = self.zeiss.GetObjective().GetPosition()
        print ("Started Zeiss Objective Switch:" + str(self.currentIndex) )
        # used to emit signal when position passes a threshold
        

    def onObjectivePosChanged(self, position):
        print ("Objective changed: " + str(position))

    def onObjectivePosSettled(self, position):
        changes = {'objective':position-1}
        print ("Objective settled to: " + str(position))
        self.sigSwitchChanged.emit(self, changes)
    
    def quit(self):
        print ("Disconnecting Zeiss")
        self.zeiss.Disconnect()
    
    def getSwitch(self, name):
        self.currentIndex = self.zeiss.GetObjective().GetPosition()
        return self.currentIndex-1

    def setSwitch(self, newPosition):
        if self.currentIndex != int(newPosition)+1:
            self.zeiss.GetObjective().SetPosition(int(newPosition)+1)
            self.currentIndex = int(newPosition)+1



        
