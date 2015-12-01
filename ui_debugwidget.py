# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'debugwidget.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DebugWidget(object):
    def setupUi(self, DebugWidget):
        DebugWidget.setObjectName("DebugWidget")
        DebugWidget.resize(800, 600)
        self.txtDebug = QtWidgets.QTextEdit(DebugWidget)
        self.txtDebug.setGeometry(QtCore.QRect(0, 0, 800, 600))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtDebug.sizePolicy().hasHeightForWidth())
        self.txtDebug.setSizePolicy(sizePolicy)
        self.txtDebug.setReadOnly(False)
        self.txtDebug.setObjectName("txtDebug")

        self.retranslateUi(DebugWidget)
        QtCore.QMetaObject.connectSlotsByName(DebugWidget)

    def retranslateUi(self, DebugWidget):
        _translate = QtCore.QCoreApplication.translate
        DebugWidget.setWindowTitle(_translate("DebugWidget", "Debug"))

