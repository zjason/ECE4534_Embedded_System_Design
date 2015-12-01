from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from ui_mainwidget import Ui_MainWidget
from message import *

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.setWindowTitle('Rover')
        self.setFixedSize(self.size())
        self.ui.debugTextEdit.setReadOnly(True)
        self.ui.gearSlider.setMaximum(5)

    @pyqtSlot(tuple)
    def appendMsg(self, msg):
        line = str(datetime.now().time()) + '\ttag: '
        if msg[0] == MSG_TAG_WIFLY:
            line += 'wifly'
        elif msg[0] == MSG_TAG_SENSOR:
            line += 'sensor'
        elif msg[0] == MSG_TAG_MOTOR:
            line += 'motor'
        elif msg[0] == MSG_TAG_CONTROLLER:
            line += 'controller'
        line += '\tcommand: '
        if msg[1] == MSG_COMMAND_SENSOR_RAW_READ:
            line += 'sensor_raw_read'
        elif msg[1] == MSG_COMMAND_MOTOR_ENCODER_READ:
            line += 'motor_encoder_read'
        line += '\tcontent: '
        line += '%6d%6d%6d%6d' % (msg[2:6])
        self.ui.debugTextEdit.append(line)
