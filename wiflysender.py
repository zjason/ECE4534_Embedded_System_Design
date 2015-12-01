from datetime import datetime
from serial import Serial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from message import *

# __________________________________________________________________________________

class WiflySender(QObject):
    def __init__(self, serial):
        super(WiflySender, self).__init__()
        self.ser = serial

    @pyqtSlot(tuple)
    def sendMsg(self, msg):
        data = bytearray()
        for b in msg:
            if b == MSG_EXTERNAL_FLAG_START or \
               b == MSG_EXTERNAL_FLAG_END or \
               b == MSG_EXTERNAL_FLAG_ESCAPE:
                data.append(MSG_EXTERNAL_FLAG_ESCAPE)
                data.append(b ^ MSG_EXTERNAL_FLAG_MASK)
            else:
                data.append(b)
        data.append(MSG_EXTERNAL_FLAG_END)
        data.insert(0, len(data))
        data.insert(0, MSG_EXTERNAL_FLAG_START)
        self.ser.write(data)

# __________________________________________________________________________________