# Sensapex Seizz SDK Python Wrapper
# All Rights Reserved. Copyright (c) Sensapex Oy 2019
# Author: Ari Salmi
# Version: 0.3
# Date: 20-01-2019

# REQUIREMENTS:
# pywin32 (conda install pywin32)
# pip install pythonnet
# pip uninstall clr (as it is coming from pythonnet)
# Zeiss RDK package + Zeiss MTB Service needs to run as windows service


# Importing MTB.Api generated with makepy
import threading
from threading import Thread, Lock
import time


# import the the common language runtime
# it is needed to use the MTB API dll
# in order to import clr, it is required to install python for .Net (pip install pythonnet) under windows
# running under linux has not been tested yet
import clr
# the reference to the current MTB version needs to be set (possibly to the GAC)
clr.AddReference(r"C:\Program Files\Carl Zeiss\MTB 2011 - 2.12.0.7\MTBApi\MTBApi.dll")

from ZEISS import MTB

# Global instance pointers
SensapexZeissSDKInstance = None
MTBRoot = None
MTBID = ""

# Thread lock for device change info
SensapexZeissDeviceThreadLock = None

## Triggered Event Placeholders

# define changer position changed event
def onChangerPositionChanged(position):
    # in case, the changer position has changed, the current position is printed
    # a position of "0" indicates an invalid state
    print("Changer moved, current position: "+str(position))

# define changer position settled event
def onChangerPositionSettled(position):
    # in case, the changer position is settled, its current position is printed
    print("Changer settled on position: "+str(position))
    
# Continual HW Limit Reached
def onContinualHWLimitReachedFunc(state, limit):
    print ("Continual HW limit reached (state, limit): %1,%2", str(state), str(limit))

# Main 
class SensapexZeiss:
    def __init__(self):
        # Initialization
        self.m_MTBConnection = None
        self.m_MTBRoot = None
        self.m_MTBDevice = None
        self.m_ID = ""
        self.m_MTBBaseEvents = None
        self.m_MTBChangerEvents = None
        self.m_devices = []
        self.m_components=[]  
        self.m_reflector = None
        self.m_objective = None
        self.m_focus = None
        self.m_shutter = None
        self.m_shutter_switch = None
        #By default selected device is first
        self.m_selected_device_index=0
        self.m_selected_component_index=0
        self.m_selected_element_index=0
        self.device_busy = threading.Event()
        self.mainLoopRunning = 0
        

    def mainLoop(self):
        self.mainLoopRunning = 1;
        while(self.mainLoopRunning==1): 
            time.sleep(0.1) 

    def OnMTBServerLoggerEvent(self, logMessage):
        print (logMessage)

    def Connect(self):
        global SensapexZeissDeviceThreadLock
        self.m_MTBConnection = MTB.Api.MTBConnection()
        self.m_ID = self.m_MTBConnection.Login("en", "")
        self.m_MTBRoot = self.m_MTBConnection.GetRoot(self.m_ID)
        self.GetDevices()
        self.GetObjective()
        self.GetReflector()
        self.GetShutter()

        SensapexZeissDeviceThreadLock = Lock();
        self.m_deviceThread = Thread(target=self.mainLoop)

        # start the thread
        self.m_deviceThread.start();
        
        return self.m_MTBRoot

    def getID(self):
        return self.m_ID

    def getMTB(self):
        return MTB

    def Disconnect(self):
        self.m_reflector.Disconnect()
        self.m_objective.Disconnect()
        self.m_shutter.Disconnect()

        print ("Logging out..")
        self.m_MTBConnection.Logout(self.m_ID)
        self.mainLoopRunning = 0
        self.m_deviceThread.join();
        
    def GetDevices(self):
        self.m_devices = []
        count = self.m_MTBRoot.GetDeviceCount()  
        for i in range(0,count):
            zdevice = self.m_MTBRoot.GetDevice(i) #ZeissDevice(self.m_MTBRoot, i)
            self.m_devices.append(zdevice)

        return self.m_devices

    def GetDeviceComponents(self, device):
        if self.m_components == 0:    
            for x in range(0,device.GetComponentCount()):

                self.m_components.append(device.GetComponentFullConfig(x))
        return self.m_components

    def GetReflector(self):
        if self.m_reflector == None:    
            #self.m_devices[self.m_selected_device_index]
            self.m_reflector  = SensapexZeissReflector(self.m_MTBRoot,self.m_ID)
        
        return self.m_reflector


    def GetObjective(self):
        if self.m_objective == None:   
            #self.m_devices[self.m_selected_device_index]
            self.m_objective  = SensapexZeissObjective(self.m_MTBRoot,self.m_ID) 
        
        return self.m_objective
    
    def GetFocus(self):
        if self.m_focus == None:
            self.m_focus = self.m_MTBRoot.GetComponent("MTBFocus")
        return self.m_focus

    def GetShutter(self):
        if self.m_shutter == None:
            self.m_shutter = SensapexZeissShutter(self.m_MTBRoot,self.m_ID)
        return self.m_shutter


class SensapexZeissCommon:
    def __init__(self, ZeissClass):
        # To extend makepy COM class's internal variables,
        # variables need to be defined into __dict__ in order
        # to be able to use then with self.attr
        self.m_zeissclass = ZeissClass
        try:
            self.m_name = ZeissClass.Name
        except:
            print ("Error: Noname")
            self.m_name = "Noname"

    def GetName(self):
        if self.m_name == "":
            self.m_name = self.m_zeissclass.Name
        return self.m_name

class SensapexZeissComponent (SensapexZeissCommon):
    def __init__(self, component):
        
        self.m_component = MTB.Api.IMTBComponent()
        SensapexZeissCommon.__init__(self, self.m_component)
        #MTB.Api.IMTBComponent.__init__(self, component)

#------- ZEISS CHANGER BASE CLASS ------
class SensapexZeissChanger(SensapexZeissCommon):
    def __init__(self, root, mtbId, changerName):
        self.m_MTBRoot = root
        self.m_changer  = root.GetComponent(changerName); 
        self.m_changerName = changerName
        self.m_ID = mtbId
        self.m_changerEvents = None
        SensapexZeissCommon.__init__(self, self.m_changer)

    def GetChanger(self):
        return self.m_changer
          
    def registerEvents(self, changeEventFunc, positionSettledFunc):
        if self.m_changer == None:
            return
            
        # Register to Changer events
        
        if self.m_changerEvents == None:
            self.m_changerEvents = MTB.Api.MTBChangerEventSink()
        else:
            self.Disconnect()
            self.m_changerEvents = MTB.Api.MTBChangerEventSink()

        # add the default events for changing position of changers
        if changeEventFunc == None:
            changeEventFunc = onChangerPositionChanged
        if positionSettledFunc == None:
            positionSettledFunc = onChangerPositionSettled

        self.onChangerPositionChanged = changeEventFunc
        self.onChangerPositionSettled = positionSettledFunc
        
        
        self.m_changerEvents.MTBPositionChangedEvent += MTB.Api.MTBChangerPositionChangedHandler(changeEventFunc)
        self.m_changerEvents.MTBPositionSettledEvent += MTB.Api.MTBChangerPositionSettledHandler(positionSettledFunc)

        self.m_changerEvents.ClientID = self.m_ID
        self.m_changerEvents.Advise(self.m_changer)   

    def Disconnect(self):
        print ("Deregistering changer events")
        try:
            self.m_changerEvents.Unadvise(self.m_changer);
            self.m_changerEvents.MTBPositionChangedEvent -= MTB.Api.MTBChangerPositionChangedHandler(self.onChangerPositionChanged)
            self.m_changerEvents.MTBPositionSettledEvent -= MTB.Api.MTBChangerPositionSettledHandler(self.onChangerPositionSettled)
        except:
            pass

        self.m_changerEvents = None

    def GetElement(self, position):
        return self.m_changer.GetElement(position)

    def GetPosition(self):
        return self.m_changer.Position

    def SetPosition(self, newposition):
        SensapexZeissDeviceThreadLock.acquire()
        self.m_changer.SetPosition(newposition, MTB.Api.MTBCmdSetModes.Default)
        SensapexZeissDeviceThreadLock.release()
   
#------- ZEISS CONTINUAL BASE CLASS ------
class SensapexZeissContinual(SensapexZeissCommon):
    def __init__(self, root, mtbId, changerName):
        print ("Trying to find component: " + changerName)
        self.m_MTBRoot = root
        self.m_continual  = root.GetComponent(changerName); 
        self.m_continualName = changerName
        self.m_ID = mtbId
        self.m_continualEvents = None
        SensapexZeissCommon.__init__(self, self.m_changer)

    def GetContinual(self):
        return self.m_changer
          
    def registerEvents(self, changeEventFunc, positionSettledFunc, hwLimitReachedFunc):
        if self.m_changer == None:
            return
            
        # Register to Changer events
  
        if self.m_continualEvents == None:
            self.m_continualEvents = MTB.Api.MTBContinualEventSink()
        else:
            self.Disconnect()
            self.m_continualEvents = MTB.Api.MTBContinualEventSink()

        # add the default events for changing position of changers
        if changeEventFunc == None:
            changeEventFunc = onContinualPositionChanged
        if positionSettledFunc == None:
            positionSettledFunc = onContinualPositionSettled
        
        if hwLimitReachedFunc == None:
            hwLimitReachedFunc = onContinualHWLimitReachedFunc

        self.onContinualPositionChanged = changeEventFunc
        self.onContinualPositionSettled = positionSettledFunc
        self.onContinualHWLimitReached = hwLimitReachedFunc
        
        self.m_continualEvents.MTBPositionChangedEvent += MTB.Api.MTBContinualPositionChangedHandler(changeEventFunc)
        self.m_continualEvents.MTBPositionSettledEvent += MTB.Api.MTBContinualPositionSettledHandler(positionSettledFunc)
        self.m_continualEvents.MTBPHWLimitReachedEvent += MTB.Api.MTBContinualHWLimitReachedHandler(hwLimitReachedFunc)

        self.m_continualEvents.ClientID = self.m_ID
        self.m_continualEvents.Advise(self.m_continual)   

    def Disconnect(self):
        print ("Deregistering changer events")
        try:
            self.m_continualEvents.Unadvise(self.m_continual);
            self.m_continualEvents.MTBPositionChangedEvent -= MTB.Api.MTBContinualPositionChangedHandler(self.onContinualPositionChanged)
            self.m_continualEvents.MTBPositionSettledEvent -= MTB.Api.MTBContinualPositionSettledHandler(self.onContinualPositionSettled)
            self.m_continualEvents.MTBPHWLimitReachedEvent -= MTB.Api.MTBContinualHWLimitReachedHandler(self.onContinualHWLimitReached)
        except:
            pass

        self.m_continualEvents = None

    def GetElement(self, position):
        return self.m_continual.GetElement(position)

    def GetPosition(self):
        return self.m_continual.Position

    def SetPosition(self, newposition):
        SensapexZeissDeviceThreadLock.acquire()
        self.m_continual.SetPosition(newposition, MTB.Api.MTBCmdSetModes.Default)
        SensapexZeissDeviceThreadLock.release()
 
class SensapexZeissFocus(SensapexZeissCommon):
    def __init__(self, root):
       
        self.m_component = root.GetComponent("MTBFocus")     
        SensapexZeissCommon.__init__(self, self.m_component)   

#------- ZEISS OBJECTIVE ------
class SensapexZeissObjective(SensapexZeissChanger):
    def __init__(self, root, mtbId):
        self.m_MTBRoot = root
        self.m_objective  = root.GetComponent("IMTBObjective"); 
        self.m_ID = mtbId
        SensapexZeissChanger.__init__(self, root, mtbId, "MTBObjectiveChanger")
        self.registerEvents(self.onObjectivePositionChanged, self.onObjectivePositionSettled)
         
    def onObjectivePositionChanged(self,position):
        print (" Objective position changed to " + position)

    def onObjectivePositionSettled(self,position):
        print (" Objective position settled to " + position)
  
    def Magnification(self):
        return self.m_objective.Magnification
    
    def Aperture(self):
        return self.m_objective.Aperture
    
    def ContrastMethod(self):
        return self.m_objective.ContrastMethod
    
    def Features(self):
        return self.m_objective.Features
    
    def WorkingDistance(self):
        return self.m_objective.WorkingDistance

#---- ZEISS SHUTTER ----
class SensapexZeissShutter(SensapexZeissChanger):
    # MTBRLShutter
    # MTBTLShutter 
    def __init__(self, root, mtbId):
        self.m_MTBRoot = root
        self.m_rlShutter = SensapexZeissChanger(root,mtbId, "MTBRLShutter")
        #self.m_tlShutter = SensapexZeissChanger(root,mtbId, "MTBTLShutter")
        #self.m_shutterSwitch = root.GetComponent("IMTBRLTLSwitchState")
        self.m_ID = mtbId

        SensapexZeissChanger.__init__(self, root, mtbId, "MTBRLShutter")
        self.registerEvents(self.onShutterPositionChanged, self.onShutterPositionSettled)
    
    def RegisterRLShutterEvents(self,positionChanged):
        if self.m_rlShutter:
            self.m_rlShutter.registerEvents(None, positionChanged)

    def RegisterTLShutterEvents(self,positionChanged):
        if self.m_tlShutter:
            self.m_tlShutter.registerEvents(None, positionChanged)   

    def SetRLShutter(self, state):
        self.m_rlShutter.SetPosition(state)
    
    def SetTLShutter(self, state):
        self.m_tlShutter.SetPosition(state) 

    def SetRLTLSwitch(self, state):
        self.SetPosition(state)

    def onShutterPositionChanged(self,position):
        print ("%1 shutter position changed to %2", self.m_shutterName, position)

    def onShutterPositionSettled(self,position):
        print ("%1 shutter position settled to %2", self.m_shutterName, position)
  
    def State(self):
        # ReflectedLight = 1,
        # TransmittedLight = 2,
        # Observation = 4,
        # Left = 8,
        # Right = 16
        return self.m_shutterSwitch.State

class SensapexZeissLamp(SensapexZeissContinual):
    def __init__(self, root, mtbId, lightPath):
        self.m_MTBRoot = root
        self.m_lamp= root.GetComponent("IMTBLamp")
        self.m_ID = mtbId
        self.m_lampEvents = None

        SensapexZeissContinual.__init__(self, root, mtbId, "IMTBLamp")
        self.registerEvents(self.onShutterPositionChanged, self.onShutterPositionSettled)

    def registerLampEvents(self):
        if self.m_lamp == None:
            return
            
        # Register to Changer events
   
        if self.m_lampEvents == None:
            self.m_lampEvents = MTB.Api.MTBLampEventSink()
        else:
            self.Disconnect()
            self.m_lampEvents = MTB.Api.MTBLampEventSink()

        # add the default events for changing position of changers
    

        self.onMTB3200KChangedEvent = self.nMTB3200KChangedEvent
        self.onMTBActiveChangedEvent  = self.MTBLampActiveChangedHandler
        self.onMTBOnOffChangedEvent  = self.MTBOnOffChangedEvent
        self.onMTBRemoteChangedEvent = self.MTBRemoteChangedEvent
        self.m_lampEvents.MTBOnOffChangedEvent += MTB.Api.MTBOnOffChangedHandler(self.onMTBOnOffChangedEvent)
        self.m_lampEvents.MTBLampActiveChangedEvent += MTB.Api.MTBLampActiveChangedHandler(self.onMTBActiveChangedEvent)
        self.m_lampEvents.MTBPHWLimitReachedEvent += MTB.Api.MTBContinualHWLimitReachedHandler(hwLimitReachedFunc)

        self.m_continualEvents.ClientID = self.m_ID
        self.m_continualEvents.Advise(self.m_continual)   

    def MTBLampActiveChangedHandler (self,position):
        print ("MTBLampActiveChangedHandler", self.m_shutterName, position)
  
    def MTBOnOffChangedEvent (self,onoff):
        print ("MTBOnOffChangedEvent:", onoff)

    def onShwLimitReachedFunc(self,position):
        print ("%1 shutter position settled to %2", self.m_shutterName, position)

#------- ZEISS REFLEFCTOR ------
class SensapexZeissReflector(SensapexZeissChanger):
    def __init__(self, root, mtbId):
        self.m_MTBRoot = root
        self.m_reflector  = root.GetComponent("IMTBReflector"); 
        self.m_ID = mtbId
        SensapexZeissChanger.__init__(self, root, mtbId, "MTBReflectorChanger")
        self.registerEvents(self.onReflectorPositionChanged, self.onReflectorPositionSettled)
         
    def onReflectorPositionChanged(self,position):
        print (" Reflector position changed to " + position)

    def onReflectorPositionSettled(self,position):
        print (" Reflector position settled to " + position)
  
    def GetWavelengthArea(self, index):
        return self.m_reflector.GetWavelengthArea(index)
    
    def GetWavelengthAreaCount(self):
        return self.m_reflector.GetWavelengthAreaCount()
    
    def ContrastMethod(self):
        return self.m_reflector.ContrastMethod
    
    def Features(self):
        return self.m_reflector.Features
    


class ZeissDevice(SensapexZeissCommon):
    def __init__(self, root, index): 
        self.m_device =  root.GetDevice(index)
        SensapexZeissCommon.__init__(self, self.m_device)

    def GetDevice(self):
        return self.m_device



# EVENT HANDLERS
# Not functional yet
""" class SensapexZeissChangerEventSink (SensapexZeissCommon):

    def __init__(self, clientID, changer):
        SensapexZeissCommon.__init__(self)
        #MTB.Api.IMTBChangerEvents.__init__(self, changer)
        self.__dict__["m_changer"] =  changer
        self.__dict__["clientID"] = clientID
        self.m_sink = MTB.Api.MTBChangerEventSink()
        self.m_sink.ClientID = clientID; 
        self.m_sink.OnMTBPositionChangedEvent = self.OnMTBPositionChangedEvent
        self.m_sink.OnMTBElementConfigurationChangedEvent = self.OnMTBElementConfigurationChangedEvent
        self.m_sink.OnMTBElementConfigurationFinishedEvent = self.OnMTBElementConfigurationFinishedEvent
        self.m_sink.OnMTBPositionChangedEvent = self.OnMTBPositionChangedEvent
        #self.m_sink.Advise(changer)
        
    def Disconnect(self):
        self.m_sink.Unadvise(self.m_changer)

    def OnMTBPositionChangedEvent(self, Position):
        print ("Position changed: " + Position)

    def OnMTBTargetPositionChangedEvent(self, targetPosition):
        print (targetPosition)

    def OnMTBPositionSettledEvent(self, Position):
        print ("Position changed: " + Position)

    def OnMTBElementConfigurationChangedEvent(self):
        print ("config changed")


    def OnMTBElementConfigurationFinishedEvent(self):
        print ("config finished") """

# 
