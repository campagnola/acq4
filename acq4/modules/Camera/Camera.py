import os

from acq4.modules.Module import Module
from acq4.util import Qt
from .CameraWindow import CameraWindow


class Camera(Module):
    moduleDisplayName = "Camera"
    moduleCategory = "Acquisition"

    def __init__(self, manager, name, config):
        Module.__init__(self, manager, name, config)
        self.ui = CameraWindow(self)
        mp = os.path.dirname(__file__)
        self.ui.setWindowIcon(Qt.QIcon(os.path.join(mp, 'icon.png')))
        manager.declareInterface(name, ['cameraModule'], self)
        
    def displayPinnedFrame(self, frame: "Frame"):
        device_name = frame.info().get('deviceName', 'Camera')
        imaging_ctrl = self.ui.getInterfaceForDevice(device_name).imagingCtrl
        imaging_ctrl.addPinnedFrame(frame.imageItem())

    def window(self):
        return self.ui
        
    def quit(self, fromUi=False):
        if not fromUi:
            self.ui.quit()
        Module.quit(self)
