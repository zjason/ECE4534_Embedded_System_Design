import sys
from PyQt5.QtWidgets import QApplication
from maincontroller import MainController

if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = MainController()
    w.start()
    sys.exit(a.exec_())
