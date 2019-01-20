
from ..drivers.sensapex.SensapexZeissSDK import SensapexZeiss
import time


class SensapexZeissObjective():

    def __init__(self):
        self.zeiss = SensapexZeiss()
        self.mtbRoot = self.zeiss.Connect()
        self.zeiss.GetObjective().registerEvents(self.objectivePosChanged, self.shutterStateSettled)
        #self.zeiss.GetReflector().registerEvents(None, None)
        #self.zeiss.GetShutter().registerEvents(self.shutterStateChanged, self.shutterStateSettled)
        #self.zeiss.GetShutter().RegisterRLShutterEvents(self.rlShutterStateChanged)

    def objectivePosChanged(self, position):
         print("Objective Changed: "+str(position))

    

    def shutterStateChanged(self, position):
         print("shutter pos settled: "+str(position))

    def shutterStateSettled(self, position):
         print("shutter pos settled: "+str(position))

    def rlShutterStateChanged(self, position):
         print(" RL shutter pos changes: "+str(position))

    def Disconnect(self):
        self.zeiss.Disconnect()

class SensapexZeissShutter():

    def __init__(self):
        self.zeiss = SensapexZeiss()
        self.mtbRoot = self.zeiss.Connect()
        self.zeiss.GetShutter().registerEvents(self.shutterStateChanged, self.shutterStateSettled)
        self.zeiss.GetShutter().RegisterRLShutterEvents(self.rlShutterStateChanged)
        self.zeiss.GetShutter().RegisterTLShutterEvents(self.tlShutterStateChanged)

   
    def shutterStateChanged(self, position):
         print("shutterswitch pos change: "+str(position))

    def shutterStateSettled(self, position):
         print("shutterswitch pos settled: "+str(position))

    def rlShutterStateChanged(self, position):
         print(" RL shutter pos changes: "+str(position))

    def tlShutterStateChanged(self, position):
         print(" TL shutter pos changes: "+str(position))

    def Disconnect(self):
        self.zeiss.Disconnect()

# MAIN
objective = SensapexZeissObjective()
#shutter = SensapexZeissShutter()

#zeiss = SensapexZeiss()
#root = zeiss.Connect()

# devs=[]
# devs = zeiss.GetDevices()
# for d in devs:
#     print d.Name
#     combos = zeiss.GetDeviceComponents(d)
#     for c in combos:
#         print c.Name

# def posChanged(position):
#     # in case, the changer position has changed, the current position is printed
#     # a position of "0" indicates an invalid state
#     print("Oma pos changed "+str(position))


# # define changer position settled event
# def posSettled(position):
#     # in case, the changer position is settled, its current position is printed
#     print("Oma pos settled: "+str(position))

# changer =zeiss.GetObjectiveChanger()
# changer.registerEvents(posChanged, posSettled)

# changer.SetPosition(2)
# print (changer.GetPosition())
# print (changer.GetName())
# focus = zeiss.GetFocus()
# print (focus.Name)
# pos = focus.GetPosition("nm")


# #rlshutter = zeiss.GetShutter("MTBRLShutter")
# #tlshutter = zeiss.GetShutter("MTBTLShutter")
# #rltlSwitch = zeiss.GetShutterSwitch()
# #print (rltlSwitch.Position)

loop=1

while loop:
    print("What would you like to do ?")
    print('(0): to exit')
    inputParam = int(input('Input: '))
    if inputParam == 0:
        loop = 0
    #objective = int(input("Stop with 0, Change objective (1-3), Move focus > 100 (100+1 = 1nm):"))
    #if objective <= 3 and objective >=1:
    #    changer.SetPosition(int(objective),32,2000)
    #if objective > 100:
    #    focus.SetPosition(objective-100,"nm",32,5000)
    # if objective == -1:
    #     rlshutter.Expose(1000,0,1)
    # if objective == -2:
    #     tlshutter.Expose(1000,0,1)

    #if int(objective) == 0:
    #    loop = False
    #    break;
print ("Disconnecting..")
objective.Disconnect()
#shutter.Disconnect()