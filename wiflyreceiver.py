from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from serial import Serial
from message import *

# __________________________________________________________________________________

class WiflyReceiver(QObject):
    msgReceived = pyqtSignal(tuple)

    def __init__(self, serial):
        super(WiflyReceiver, self).__init__()
        self.ser = serial

    @pyqtSlot()
    def processMsg(self):
        while True:
            value = ord(self.ser.read()[0])
            if value == MSG_EXTERNAL_FLAG_START:
                msg = []
                value = ord(self.ser.read()[0])
                while value != MSG_EXTERNAL_FLAG_END:
                    if value == MSG_EXTERNAL_FLAG_ESCAPE:
                        value = ord(self.ser.read()[0])
                        msg.append(value ^ MSG_EXTERNAL_FLAG_MASK)
                    else:
                        msg.append(value)
                    value = ord(self.ser.read()[0])
                self.msgReceived.emit(tuple(msg))

# __________________________________________________________________________________