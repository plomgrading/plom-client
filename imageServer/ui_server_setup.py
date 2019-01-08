# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../qtCreatorFiles/ui_server_setup.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ServerInfo(object):
    def setupUi(self, ServerInfo):
        ServerInfo.setObjectName("ServerInfo")
        ServerInfo.resize(490, 437)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ServerInfo)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.serverGBox = QtWidgets.QGroupBox(ServerInfo)
        self.serverGBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.serverGBox.sizePolicy().hasHeightForWidth())
        self.serverGBox.setSizePolicy(sizePolicy)
        self.serverGBox.setObjectName("serverGBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.serverGBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.serverLabel = QtWidgets.QLabel(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.serverLabel.sizePolicy().hasHeightForWidth())
        self.serverLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.serverLabel.setFont(font)
        self.serverLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.serverLabel.setObjectName("serverLabel")
        self.gridLayout.addWidget(self.serverLabel, 0, 0, 1, 1)
        self.mportLabel = QtWidgets.QLabel(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.mportLabel.sizePolicy().hasHeightForWidth())
        self.mportLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.mportLabel.setFont(font)
        self.mportLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mportLabel.setObjectName("mportLabel")
        self.gridLayout.addWidget(self.mportLabel, 1, 0, 1, 1)
        self.mportSB = QtWidgets.QSpinBox(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.mportSB.sizePolicy().hasHeightForWidth())
        self.mportSB.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.mportSB.setFont(font)
        self.mportSB.setMaximum(65535)
        self.mportSB.setProperty("value", 41984)
        self.mportSB.setObjectName("mportSB")
        self.gridLayout.addWidget(self.mportSB, 1, 1, 1, 1)
        self.wportLabel = QtWidgets.QLabel(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.wportLabel.sizePolicy().hasHeightForWidth())
        self.wportLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.wportLabel.setFont(font)
        self.wportLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.wportLabel.setObjectName("wportLabel")
        self.gridLayout.addWidget(self.wportLabel, 1, 2, 1, 1)
        self.wportSB = QtWidgets.QSpinBox(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.wportSB.sizePolicy().hasHeightForWidth())
        self.wportSB.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.wportSB.setFont(font)
        self.wportSB.setMaximum(65535)
        self.wportSB.setProperty("value", 41985)
        self.wportSB.setObjectName("wportSB")
        self.gridLayout.addWidget(self.wportSB, 1, 3, 1, 1)
        self.serverLE = QtWidgets.QLineEdit(self.serverGBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.serverLE.sizePolicy().hasHeightForWidth())
        self.serverLE.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.serverLE.setFont(font)
        self.serverLE.setObjectName("serverLE")
        self.gridLayout.addWidget(self.serverLE, 0, 1, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.serverGBox)
        self.manageUsersButton = QtWidgets.QPushButton(ServerInfo)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.manageUsersButton.sizePolicy().hasHeightForWidth()
        )
        self.manageUsersButton.setSizePolicy(sizePolicy)
        self.manageUsersButton.setObjectName("manageUsersButton")
        self.verticalLayout_2.addWidget(self.manageUsersButton)
        self.classListButton = QtWidgets.QPushButton(ServerInfo)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.classListButton.sizePolicy().hasHeightForWidth()
        )
        self.classListButton.setSizePolicy(sizePolicy)
        self.classListButton.setObjectName("classListButton")
        self.verticalLayout_2.addWidget(self.classListButton)
        self.saveCloseButton = QtWidgets.QPushButton(ServerInfo)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.saveCloseButton.sizePolicy().hasHeightForWidth()
        )
        self.saveCloseButton.setSizePolicy(sizePolicy)
        self.saveCloseButton.setObjectName("saveCloseButton")
        self.verticalLayout_2.addWidget(self.saveCloseButton)
        self.closeButton = QtWidgets.QPushButton(ServerInfo)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.closeButton.sizePolicy().hasHeightForWidth())
        self.closeButton.setSizePolicy(sizePolicy)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout_2.addWidget(self.closeButton)

        self.retranslateUi(ServerInfo)
        QtCore.QMetaObject.connectSlotsByName(ServerInfo)
        ServerInfo.setTabOrder(self.serverLE, self.mportSB)
        ServerInfo.setTabOrder(self.mportSB, self.wportSB)

    def retranslateUi(self, ServerInfo):
        _translate = QtCore.QCoreApplication.translate
        ServerInfo.setWindowTitle(_translate("ServerInfo", "Choose your task"))
        self.serverGBox.setTitle(_translate("ServerInfo", "Server Information"))
        self.serverLabel.setText(_translate("ServerInfo", "Server name"))
        self.mportLabel.setText(_translate("ServerInfo", "Message port"))
        self.wportLabel.setText(_translate("ServerInfo", "Webdav port"))
        self.serverLE.setText(_translate("ServerInfo", "127.0.0.1"))
        self.manageUsersButton.setText(_translate("ServerInfo", "Manage users"))
        self.classListButton.setText(_translate("ServerInfo", "Get class list"))
        self.saveCloseButton.setText(_translate("ServerInfo", "Save && Close"))
        self.closeButton.setText(_translate("ServerInfo", "Close"))
