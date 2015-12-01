import math
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from message import *

# __________________________________________________________________________________

ROVER_WIDTH = 170.0
ROVER_LENGTH = 230.0
ROVER_CENTER_OFFSET = 10.5
WHEELBASE = 86.635
BETA = math.atan(ROVER_WIDTH / ROVER_LENGTH)
X_MAX = 1700.0
Y_MAX = 1700.0
WORLD_X = 2000.0
WORLD_Y = 2000.0

ENCODER_TICK_TO_MM = (37.0 * math.pi) * 4 / 298 / 12

ROVER_STATE_INIT_POSITION = 1
ROVER_STATE_FOLLOW_WALL = 2

ROVER_DIRECTION_STOP = 0
ROVER_DIRECTION_FORWARD = 1
ROVER_DIRECTION_LEFT = 2
ROVER_DIRECTION_BACKWARD = 3
ROVER_DIRECTION_RIGHT = 4

# __________________________________________________________________________________

# Convert raw sensor read to distance measured in millimeter
def getSensorDistance(raw):
    #distance = 3636966 / (400 * raw - 211) - 4
    distance = 1.0 * 3678953 / (400 * raw + 2) - 4
    return 65535.0 if (distance > 65535.0) else distance

# Convert encoder data to distance measured in millimeter
# track run 0.118 mm per tick
def getEncoderDistance(raw):
    return (raw) * ENCODER_TICK_TO_MM

# __________________________________________________________________________________

class Rover(QObject):

    newWallDetected = pyqtSignal(tuple, tuple)
    newRoverPosition = pyqtSignal(tuple, float)

    def __init__(self):
        super(Rover, self).__init__()

        self.state = ROVER_STATE_INIT_POSITION

        self.position = [0.0, 0.0]
        self.orientation = 0.0
        self.motorDirection = [1, 1]

        self.roverGear = 0;
        self.roverDirection = ROVER_DIRECTION_STOP
        self.commandMsg = [0 for x in range(6)]

        self.wallRear = [X_MAX, Y_MAX]
        self.wallFront = [X_MAX, 0.0]

    def initPosition(self, s1, s2):
        phi = math.atan((s1 - s2) / ROVER_LENGTH)
        self.orientation = phi
        self.position[0] = X_MAX - s1 * math.cos(phi) - ROVER_LENGTH * math.sin(BETA - phi) / (2 * math.cos(BETA))
        self.position[1] = Y_MAX + s1 * math.sin(phi) - ROVER_LENGTH * (1 / math.cos(phi) - math.cos(BETA - phi) / (2 * math.cos(BETA)))
        self.wallFront[1] = Y_MAX - ROVER_LENGTH / math.cos(phi)

    def updateRoverPosition(self, e1, e2):
        e1 *= self.motorDirection[0]
        e2 *= self.motorDirection[1]
        if e1 == e2:
            self.position[0] -= e1 * math.sin(self.orientation)
            self.position[1] -= e2 * math.cos(self.orientation)
        else:
            phi = self.orientation
            theta = (e2 - e1) / WHEELBASE
            self.orientation += theta
            self.position[0] += ROVER_CENTER_OFFSET * math.sin(phi)
            self.position[0] += (e1 + e2) / (e2 - e1) * WHEELBASE / 2 * (math.cos(phi + theta) - math.cos(phi))
            self.position[0] -= ROVER_CENTER_OFFSET * math.sin(phi + theta)
            self.position[1] += ROVER_CENTER_OFFSET * math.cos(phi)
            self.position[1] += (e1 + e2) / (e2 - e1) * WHEELBASE / 2 * (math.sin(phi) - math.sin(phi + theta))
            self.position[1] -= ROVER_CENTER_OFFSET * math.cos(phi + theta)

    def updateWallPosition(self, s1, s2):
        phi = self.orientation
        self.wallFront[0] = self.position[0] + s1 * math.cos(phi) + ROVER_LENGTH * math.sin(BETA - phi) / (2 * math.cos(BETA))
        self.wallFront[1] = self.position[1] - s1 * math.sin(phi) - ROVER_LENGTH * math.cos(BETA - phi) / (2 * math.cos(BETA))
        self.wallRear[0] = self.position[0] + s2 * math.cos(phi) + ROVER_LENGTH * (math.sin(phi) + math.sin(BETA - phi) / (2 * math.cos(BETA)))
        self.wallRear[1] = self.position[1] - s2 * math.sin(phi) + ROVER_LENGTH * (math.cos(phi) - math.cos(BETA - phi) / (2 * math.cos(BETA)))

    @pyqtSlot(tuple)
    def processData(self, msg):
        if msg[0] == MSG_TAG_SENSOR and msg[1] == MSG_COMMAND_SENSOR_RAW_READ:
            s1 = getSensorDistance(msg[2])
            s2 = getSensorDistance(msg[3] - 5)
            if self.state == ROVER_STATE_INIT_POSITION:
                self.initPosition(s1, s2)
                self.state = ROVER_STATE_FOLLOW_WALL
                self.newRoverPosition.emit(tuple(self.position), self.orientation)
            elif self.state == ROVER_STATE_FOLLOW_WALL:
                self.updateWallPosition(s1, s2)
            self.newWallDetected.emit(tuple(self.wallFront), tuple(self.wallRear))
        if msg[0] == MSG_TAG_MOTOR and msg[1] == MSG_COMMAND_MOTOR_ENCODER_READ:
            e1 = getEncoderDistance(msg[2] * 256 + msg[3])
            e2 = getEncoderDistance(msg[4] * 256 + msg[5])
            if self.state == ROVER_STATE_FOLLOW_WALL:
                self.updateRoverPosition(e1, e2)
                self.newRoverPosition.emit(tuple(self.position), self.orientation)

    def updateMotorCommand(self):
        self.commandMsg[0] = MSG_TAG_MOTOR
        self.commandMsg[1] = MSG_COMMAND_MOTOR_PWM
        if self.roverDirection == ROVER_DIRECTION_STOP or self.roverGear == 0:
            self.commandMsg[2:] = [0x01, 0x00, 0x01, 0x01]
            self.motorDirection = [1, 1]
        elif self.roverDirection == ROVER_DIRECTION_FORWARD:
            self.motorDirection = [1, 1]
            if self.roverGear == 1:
                self.commandMsg[2:] = [0x01, 0x3c, 0x01, 0x4e]
            elif self.roverGear == 2:
                self.commandMsg[2:] = [0x01, 0x46, 0x01, 0x50]
            elif self.roverGear == 3:
                self.commandMsg[2:] = [0x01, 0x50, 0x01, 0x54]
            elif self.roverGear == 4:
                self.commandMsg[2:] = [0x01, 0x5a, 0x01, 0x5c]
            elif self.roverGear == 5:
                self.commandMsg[2:] = [0x01, 0x64, 0x01, 0x64]
        elif self.roverDirection == ROVER_DIRECTION_BACKWARD:
            self.motorDirection = [-1, -1]
            if self.roverGear == 1:
                self.commandMsg[2:] = [0x00, 0x3c, 0x00, 0x4e]
            elif self.roverGear == 2:
                self.commandMsg[2:] = [0x00, 0x46, 0x00, 0x53]
            elif self.roverGear == 3:
                self.commandMsg[2:] = [0x00, 0x50, 0x00, 0x54]
            elif self.roverGear == 4:
                self.commandMsg[2:] = [0x00, 0x5a, 0x00, 0x5c]
            elif self.roverGear == 5:
                self.commandMsg[2:] = [0x00, 0x64, 0x00, 0x64]
        elif self.roverDirection == ROVER_DIRECTION_LEFT:
            self.motorDirection = [-1, 1]
            if self.roverGear == 1:
                self.commandMsg[2:] = [0x01, 0x55, 0x01, 0x55]
                self.motorDirection[0] = 1
            elif self.roverGear == 2:
                self.commandMsg[2:] = [0x00, 0x4b, 0x01, 0x4b]
            elif self.roverGear == 3:
                self.commandMsg[2:] = [0x01, 0x00, 0x01, 0x64]
                self.motorDirection[0] = 1
            elif self.roverGear == 4:
                self.commandMsg[2:] = [0x00, 0x3c, 0x01, 0x50]
            elif self.roverGear == 5:
                self.commandMsg[2:] = [0x00, 0x64, 0x01, 0x64]
        elif self.roverDirection == ROVER_DIRECTION_RIGHT:
            self.motorDirection = [1, -1]
            if self.roverGear == 1:
                self.commandMsg[2:] = [0x01, 0x55, 0x01, 0x55]
                self.motorDirection[1] = 1
            elif self.roverGear == 2:
                self.commandMsg[2:] = [0x01, 0x4b, 0x00, 0x4b]
            elif self.roverGear == 3:
                self.commandMsg[2:] = [0x01, 0x64, 0x01, 0x00]
                self.motorDirection[1] = 1
            elif self.roverGear == 4:
                self.commandMsg[2:] = [0x01, 0x50, 0x00, 0x3c]
            elif self.roverGear == 5:
                self.commandMsg[2:] = [0x01, 0x64, 0x00, 0x64]
