import time
from datetime import datetime
from serial import Serial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QPointF, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QGraphicsRectItem
from message import *
from mainwidget import MainWidget
from wiflyreceiver import WiflyReceiver
from wiflysender import WiflySender
from rover import *

SIMULATION_STATE_PHASE_1 = 1
SIMULATION_STATE_PHASE_2 = 2
SIMULATION_STATE_PHASE_3 = 3
SIMULATION_STATE_PHASE_4 = 4
SIMULATION_STATE_PHASE_5 = 5

CANVAS_RATIO = 3

DOT_SIZE = 2

class MainController(QObject):

    appStart = pyqtSignal()
    newCommand = pyqtSignal(tuple)

    def __init__(self):
        super(MainController, self).__init__()
        self.ser = Serial(WIFLY_SERIAL_PORT, WIFLY_BAUD_RATE)
        self.wiflyReceiver = WiflyReceiver(self.ser)
        self.wiflySender = WiflySender(self.ser)
        self.rover = Rover()
        self.mainWidget = MainWidget()
        self.wiflyReceiverThread = QThread()
        self.wiflyReceiver.moveToThread(self.wiflyReceiverThread)
        self.wiflySenderThread = QThread()
        self.wiflySender.moveToThread(self.wiflySenderThread)
        self.simState = SIMULATION_STATE_PHASE_1
        self.simTimer = QTimer()
        self.simTimer.setSingleShot(True)

        self.wiflyReceiver.msgReceived.connect(self.mainWidget.appendMsg)
        self.wiflyReceiver.msgReceived.connect(self.rover.processData)
        self.newCommand.connect(self.wiflySender.sendMsg)
        self.appStart.connect(self.wiflyReceiver.processMsg)
        self.mainWidget.ui.gearSlider.valueChanged.connect(self.manualGearChange)
        self.mainWidget.ui.upButton.clicked.connect(self.manualMoveForward)
        self.mainWidget.ui.downButton.clicked.connect(self.manualMoveBackward)
        self.mainWidget.ui.leftButton.clicked.connect(self.manualMoveLeft)
        self.mainWidget.ui.rightButton.clicked.connect(self.manualMoveRight)
        self.mainWidget.ui.brakeButton.clicked.connect(self.manualStop)
        self.mainWidget.ui.simulationButton.clicked.connect(self.simulationStart)
        self.rover.newRoverPosition.connect(self.drawRover)
        self.rover.newWallDetected.connect(self.drawNewWall)
        self.simTimer.timeout.connect(self.simulationUpdate)

        self.mapScene = QGraphicsScene(0, 0, WORLD_X / CANVAS_RATIO, WORLD_Y / CANVAS_RATIO)
        self.mainWidget.ui.mappingGraphicsView.setScene(self.mapScene)

        self.roverRect = QGraphicsRectItem()
        self.mapScene.addItem(self.roverRect)

        """
        rect1 = QGraphicsRectItem()
        rect2 = QGraphicsRectItem()
        self.mapScene.addItem(rect1)
        self.mapScene.addItem(rect2)
        rect1.setRect(100, 100, 20, 40)
        rect2.setRect(100, 100, 20, 40)
        #rect.moveBy(10, 50)
        rect2.setTransformOriginPoint(100, 100)
        rect2.setRotation(-10)
        print rect1.rect().center()
        #print rect2.transformOriginPoint().x(), rect2.transformOriginPoint().y()
        """

    @pyqtSlot(tuple, tuple)
    def drawNewWall(self, wallFront, wallRear):
        pFront = QGraphicsRectItem(wallFront[0] / CANVAS_RATIO,
                                   wallFront[1] / CANVAS_RATIO,
                                   DOT_SIZE, DOT_SIZE)
        pRear = QGraphicsRectItem(wallRear[0] / CANVAS_RATIO,
                                  wallRear[1] / CANVAS_RATIO,
                                  DOT_SIZE, DOT_SIZE)
        self.mapScene.addItem(pFront)
        self.mapScene.addItem(pRear)

    @pyqtSlot(tuple, float)
    def drawRover(self, center, orientation):
        self.roverRect.setRect((center[0] - ROVER_WIDTH / 2) / CANVAS_RATIO,
                               (center[1] - ROVER_LENGTH / 2) / CANVAS_RATIO,
                               ROVER_WIDTH / CANVAS_RATIO, ROVER_LENGTH / CANVAS_RATIO)
        self.roverRect.setTransformOriginPoint(center[0] / CANVAS_RATIO, center[1] / CANVAS_RATIO)
        self.roverRect.setRotation(math.degrees(-orientation))

    @pyqtSlot()
    def manualGearChange(self):
        gear = self.mainWidget.ui.gearSlider.value()
        self.mainWidget.ui.gearLcdNumber.display(gear)
        self.rover.roverGear = gear
        self.rover.updateMotorCommand()
        self.newCommand.emit(tuple(self.rover.commandMsg))

    @pyqtSlot()
    def manualMoveForward(self):
        self.rover.roverDirection = ROVER_DIRECTION_FORWARD
        self.rover.updateMotorCommand()
        self.newCommand.emit(tuple(self.rover.commandMsg))

    @pyqtSlot()
    def manualMoveBackward(self):
        self.rover.roverDirection = ROVER_DIRECTION_BACKWARD
        self.rover.updateMotorCommand()
        self.newCommand.emit(tuple(self.rover.commandMsg))

    @pyqtSlot()
    def manualMoveLeft(self):
        self.rover.roverDirection = ROVER_DIRECTION_LEFT
        self.rover.updateMotorCommand()
        self.newCommand.emit(tuple(self.rover.commandMsg))

    @pyqtSlot()
    def manualMoveRight(self):
        self.rover.roverDirection = ROVER_DIRECTION_RIGHT
        self.rover.updateMotorCommand()
        self.newCommand.emit(tuple(self.rover.commandMsg))

    @pyqtSlot()
    def manualStop(self):
        self.mainWidget.ui.gearSlider.setValue(0)

    @pyqtSlot()
    def simulationStart(self):
        self.simState == SIMULATION_STATE_PHASE_1
        self.simTimer.start(5000)

    @pyqtSlot()
    def simulationUpdate(self):
        if self.simState == SIMULATION_STATE_PHASE_1:
            self.simState = SIMULATION_STATE_PHASE_2
            self.rover.roverGear = 2
            self.rover.roverDirection = ROVER_DIRECTION_FORWARD
            self.rover.updateMotorCommand()
            self.newCommand.emit(tuple(self.rover.commandMsg))
            self.simTimer.start(16000)
        elif self.simState == SIMULATION_STATE_PHASE_2:
            self.simState = SIMULATION_STATE_PHASE_3
            self.rover.roverDirection = ROVER_DIRECTION_BACKWARD
            self.rover.updateMotorCommand()
            self.newCommand.emit(tuple(self.rover.commandMsg))
            self.simTimer.start(6100)
        elif self.simState == SIMULATION_STATE_PHASE_3:
            self.simState = SIMULATION_STATE_PHASE_4
            self.rover.roverDirection = ROVER_DIRECTION_LEFT
            self.rover.updateMotorCommand()
            self.newCommand.emit(tuple(self.rover.commandMsg))
            self.simTimer.start(3500)
        elif self.simState == SIMULATION_STATE_PHASE_4:
            self.simState = SIMULATION_STATE_PHASE_5
            self.rover.roverDirection = ROVER_DIRECTION_BACKWARD
            self.rover.updateMotorCommand()
            self.newCommand.emit(tuple(self.rover.commandMsg))
            self.simTimer.start(8300)
        elif self.simState == SIMULATION_STATE_PHASE_5:
            self.rover.roverGear = 0
            self.rover.roverDirection = ROVER_DIRECTION_STOP
            self.rover.updateMotorCommand()
            self.newCommand.emit(tuple(self.rover.commandMsg))

    def start(self):
        self.mainWidget.show()
        self.wiflyReceiverThread.start()
        self.wiflySenderThread.start()
        self.appStart.emit()
