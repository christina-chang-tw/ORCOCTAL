
from ctypes import WinDLL, pointer

class TektronixAPT(object):

    def __init__(self, serial: float=83863567):
        aptdll = WinDLL.LoadLibrary("APT.dll")
        aptdll.EnableEventDlg(True)
        aptdll.APTInit()
        aptdll.InitHWDevice(serial)
        self._aptdll = aptdll
        self.serial = serial

    def MOT_GetPosition(self, pos):
        return self._aptdll.MOT_GetPosition(self.serial, pointer(pos))

    def MOT_MoveAbsoluteEx(self, abs_pos):
       self._aptdll.MOT_MoveAbsoluteEx(self.serial, abs_pos, True)

    @property
    def aptdll(self):
        return self._aptdll