# __________________________________________________________________________________

WIFLY_SERIAL_PORT = '/dev/cu.usbserial-A702ZMMF'
WIFLY_BAUD_RATE = 57600

# __________________________________________________________________________________

MSG_TAG_WIFLY = 0x01
MSG_TAG_SENSOR = 0x02
MSG_TAG_MOTOR = 0x03
MSG_TAG_CONTROLLER = 0x04

MSG_COMMAND_WIFLY_SEND = 0x11
MSG_COMMAND_WIFLY_RECEIVED = 0x12
MSG_COMMAND_SENSOR_RAW_READ = 0x21
MSG_COMMAND_SENSOR_CHANGE_RATE = 0x22
MSG_COMMAND_SENSOR_TURN_ON = 0x23
MSG_COMMAND_SENSOR_TURN_OFF = 0x24
MSG_COMMAND_SENSOR_ADC_READY = 0x25
MSG_COMMAND_MOTOR_PWM = 0x31
MSG_COMMAND_MOTOR_ENCODER_READ = 0x32
MSG_COMMAND_CONTROLLER_NULL = 0x40

MSG_EXTERNAL_FLAG_START = 0x62
MSG_EXTERNAL_FLAG_END = 0x63
MSG_EXTERNAL_FLAG_ESCAPE = 0x7d
MSG_EXTERNAL_FLAG_MASK = 0x20

# __________________________________________________________________________________