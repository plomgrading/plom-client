# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../qtCreatorFiles/ui_iic.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IIC(object):
    def setupUi(self, IIC):
        IIC.setObjectName("IIC")
        IIC.resize(1024, 660)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(IIC)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.tabWidget = QtWidgets.QTabWidget(IIC)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName("tabWidget")
        self.loginTab = QtWidgets.QWidget()
        self.loginTab.setObjectName("loginTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.loginTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.userGBox = QtWidgets.QGroupBox(self.loginTab)
        self.userGBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.userGBox.sizePolicy().hasHeightForWidth())
        self.userGBox.setSizePolicy(sizePolicy)
        self.userGBox.setObjectName("userGBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.userGBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.userGBox)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.userLE = QtWidgets.QLineEdit(self.userGBox)
        self.userLE.setReadOnly(True)
        self.userLE.setPlaceholderText("")
        self.userLE.setObjectName("userLE")
        self.gridLayout_3.addWidget(self.userLE, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.userGBox)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.passwordLE = QtWidgets.QLineEdit(self.userGBox)
        self.passwordLE.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordLE.setObjectName("passwordLE")
        self.gridLayout_3.addWidget(self.passwordLE, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.userGBox)
        self.serverGBox = QtWidgets.QGroupBox(self.loginTab)
        self.serverGBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.serverGBox.sizePolicy().hasHeightForWidth())
        self.serverGBox.setSizePolicy(sizePolicy)
        self.serverGBox.setObjectName("serverGBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.serverGBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.serverLabel = QtWidgets.QLabel(self.serverGBox)
        self.serverLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.serverLabel.setObjectName("serverLabel")
        self.gridLayout_2.addWidget(self.serverLabel, 0, 0, 1, 1)
        self.serverLE = QtWidgets.QLineEdit(self.serverGBox)
        self.serverLE.setObjectName("serverLE")
        self.gridLayout_2.addWidget(self.serverLE, 0, 1, 1, 2)
        self.mportSB = QtWidgets.QSpinBox(self.serverGBox)
        self.mportSB.setMaximum(65535)
        self.mportSB.setProperty("value", 41984)
        self.mportSB.setObjectName("mportSB")
        self.gridLayout_2.addWidget(self.mportSB, 1, 1, 1, 1)
        self.mportLabel = QtWidgets.QLabel(self.serverGBox)
        self.mportLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mportLabel.setObjectName("mportLabel")
        self.gridLayout_2.addWidget(self.mportLabel, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.serverGBox)
        self.fontBox = QtWidgets.QGroupBox(self.loginTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontBox.sizePolicy().hasHeightForWidth())
        self.fontBox.setSizePolicy(sizePolicy)
        self.fontBox.setObjectName("fontBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.fontBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.fontSB = QtWidgets.QSpinBox(self.fontBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontSB.sizePolicy().hasHeightForWidth())
        self.fontSB.setSizePolicy(sizePolicy)
        self.fontSB.setMinimum(2)
        self.fontSB.setMaximum(24)
        self.fontSB.setProperty("value", 10)
        self.fontSB.setObjectName("fontSB")
        self.gridLayout_4.addWidget(self.fontSB, 0, 1, 1, 1)
        self.fontLabel = QtWidgets.QLabel(self.fontBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontLabel.sizePolicy().hasHeightForWidth())
        self.fontLabel.setSizePolicy(sizePolicy)
        self.fontLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fontLabel.setObjectName("fontLabel")
        self.gridLayout_4.addWidget(self.fontLabel, 0, 0, 1, 1)
        self.fontButton = QtWidgets.QPushButton(self.fontBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontButton.sizePolicy().hasHeightForWidth())
        self.fontButton.setSizePolicy(sizePolicy)
        self.fontButton.setObjectName("fontButton")
        self.gridLayout_4.addWidget(self.fontButton, 0, 2, 1, 1)
        self.verticalLayout.addWidget(self.fontBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loginButton = QtWidgets.QPushButton(self.loginTab)
        self.loginButton.setObjectName("loginButton")
        self.horizontalLayout.addWidget(self.loginButton)
        spacerItem = QtWidgets.QSpacerItem(703, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget.addTab(self.loginTab, "")
        self.scanTab = QtWidgets.QWidget()
        self.scanTab.setEnabled(False)
        self.scanTab.setObjectName("scanTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scanTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.scanTab)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scanTW = QtWidgets.QTreeWidget(self.groupBox)
        self.scanTW.setAlternatingRowColors(True)
        self.scanTW.setColumnCount(2)
        self.scanTW.setObjectName("scanTW")
        self.scanTW.headerItem().setText(0, "1")
        self.scanTW.headerItem().setText(1, "2")
        self.verticalLayout_3.addWidget(self.scanTW)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.refreshSButton = QtWidgets.QPushButton(self.groupBox)
        self.refreshSButton.setObjectName("refreshSButton")
        self.horizontalLayout_2.addWidget(self.refreshSButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.removePageB = QtWidgets.QPushButton(self.groupBox)
        self.removePageB.setObjectName("removePageB")
        self.horizontalLayout_2.addWidget(self.removePageB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(self.scanTab)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.incompTW = QtWidgets.QTreeWidget(self.groupBox_3)
        self.incompTW.setAlternatingRowColors(True)
        self.incompTW.setColumnCount(2)
        self.incompTW.setObjectName("incompTW")
        self.incompTW.headerItem().setText(0, "1")
        self.incompTW.headerItem().setText(1, "2")
        self.verticalLayout_4.addWidget(self.incompTW)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.refreshIButton = QtWidgets.QPushButton(self.groupBox_3)
        self.refreshIButton.setObjectName("refreshIButton")
        self.horizontalLayout_3.addWidget(self.refreshIButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.subsPageB = QtWidgets.QPushButton(self.groupBox_3)
        self.subsPageB.setObjectName("subsPageB")
        self.horizontalLayout_3.addWidget(self.subsPageB)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.tabWidget.addTab(self.scanTab, "")
        self.overallTab = QtWidgets.QWidget()
        self.overallTab.setEnabled(False)
        self.overallTab.setObjectName("overallTab")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.overallTab)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.overallTW = QtWidgets.QTableWidget(self.overallTab)
        self.overallTW.setAlternatingRowColors(True)
        self.overallTW.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.overallTW.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.overallTW.setColumnCount(4)
        self.overallTW.setObjectName("overallTW")
        self.overallTW.setRowCount(0)
        self.overallTW.horizontalHeader().setStretchLastSection(True)
        self.overallTW.verticalHeader().setVisible(False)
        self.verticalLayout_14.addWidget(self.overallTW)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.refreshOButton = QtWidgets.QPushButton(self.overallTab)
        self.refreshOButton.setObjectName("refreshOButton")
        self.horizontalLayout_11.addWidget(self.refreshOButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem3)
        self.verticalLayout_14.addLayout(self.horizontalLayout_11)
        self.tabWidget.addTab(self.overallTab, "")
        self.idTab = QtWidgets.QWidget()
        self.idTab.setEnabled(False)
        self.idTab.setObjectName("idTab")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.idTab)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.groupBox_2 = QtWidgets.QGroupBox(self.idTab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 2)
        self.papersLE = QtWidgets.QLineEdit(self.groupBox_2)
        self.papersLE.setReadOnly(True)
        self.papersLE.setObjectName("papersLE")
        self.gridLayout.addWidget(self.papersLE, 0, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 2)
        self.totPB = QtWidgets.QProgressBar(self.groupBox_2)
        self.totPB.setProperty("value", 0)
        self.totPB.setObjectName("totPB")
        self.gridLayout.addWidget(self.totPB, 2, 2, 1, 1)
        self.idPB = QtWidgets.QProgressBar(self.groupBox_2)
        self.idPB.setProperty("value", 0)
        self.idPB.setObjectName("idPB")
        self.gridLayout.addWidget(self.idPB, 1, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 2)
        self.verticalLayout_11.addLayout(self.gridLayout)
        self.refreshIDButon = QtWidgets.QPushButton(self.groupBox_2)
        self.refreshIDButon.setObjectName("refreshIDButon")
        self.verticalLayout_11.addWidget(self.refreshIDButon)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_11.addItem(spacerItem4)
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.selectRectButton = QtWidgets.QPushButton(self.groupBox_4)
        self.selectRectButton.setObjectName("selectRectButton")
        self.verticalLayout_12.addWidget(self.selectRectButton)
        self.predictButton = QtWidgets.QPushButton(self.groupBox_4)
        self.predictButton.setEnabled(False)
        self.predictButton.setObjectName("predictButton")
        self.verticalLayout_12.addWidget(self.predictButton)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_12.addItem(spacerItem5)
        self.delPredButton = QtWidgets.QPushButton(self.groupBox_4)
        self.delPredButton.setObjectName("delPredButton")
        self.verticalLayout_12.addWidget(self.delPredButton)
        self.verticalLayout_11.addWidget(self.groupBox_4)
        self.horizontalLayout_9.addLayout(self.verticalLayout_11)
        self.predGB = QtWidgets.QGroupBox(self.groupBox_2)
        self.predGB.setObjectName("predGB")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.predGB)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.predictionTW = QtWidgets.QTableWidget(self.predGB)
        self.predictionTW.setAlternatingRowColors(True)
        self.predictionTW.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.predictionTW.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectColumns)
        self.predictionTW.setColumnCount(3)
        self.predictionTW.setObjectName("predictionTW")
        self.predictionTW.setRowCount(0)
        self.predictionTW.horizontalHeader().setStretchLastSection(True)
        self.predictionTW.verticalHeader().setVisible(False)
        self.verticalLayout_13.addWidget(self.predictionTW)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem6)
        self.predListRefreshB = QtWidgets.QPushButton(self.predGB)
        self.predListRefreshB.setObjectName("predListRefreshB")
        self.horizontalLayout_10.addWidget(self.predListRefreshB)
        self.verticalLayout_13.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_9.addWidget(self.predGB)
        self.verticalLayout_10.addWidget(self.groupBox_2)
        self.tabWidget.addTab(self.idTab, "")
        self.progressTab = QtWidgets.QWidget()
        self.progressTab.setEnabled(False)
        self.progressTab.setObjectName("progressTab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.progressTab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollArea = QtWidgets.QScrollArea(self.progressTab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.markBucket = QtWidgets.QWidget()
        self.markBucket.setGeometry(QtCore.QRect(0, 0, 64, 16))
        self.markBucket.setObjectName("markBucket")
        self.scrollArea.setWidget(self.markBucket)
        self.verticalLayout_5.addWidget(self.scrollArea)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.refreshPButton = QtWidgets.QPushButton(self.progressTab)
        self.refreshPButton.setObjectName("refreshPButton")
        self.horizontalLayout_4.addWidget(self.refreshPButton)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.progressTab, "")
        self.unknownTab = QtWidgets.QWidget()
        self.unknownTab.setEnabled(False)
        self.unknownTab.setObjectName("unknownTab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.unknownTab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.unknownTV = QtWidgets.QTableView(self.unknownTab)
        self.unknownTV.setObjectName("unknownTV")
        self.verticalLayout_6.addWidget(self.unknownTV)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.refreshUButton = QtWidgets.QPushButton(self.unknownTab)
        self.refreshUButton.setObjectName("refreshUButton")
        self.horizontalLayout_6.addWidget(self.refreshUButton)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem8)
        self.actionUButton = QtWidgets.QPushButton(self.unknownTab)
        self.actionUButton.setObjectName("actionUButton")
        self.horizontalLayout_6.addWidget(self.actionUButton)
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        self.tabWidget.addTab(self.unknownTab, "")
        self.collideTab = QtWidgets.QWidget()
        self.collideTab.setEnabled(False)
        self.collideTab.setObjectName("collideTab")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.collideTab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.collideTV = QtWidgets.QTableView(self.collideTab)
        self.collideTV.setObjectName("collideTV")
        self.verticalLayout_8.addWidget(self.collideTV)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.refreshCButton = QtWidgets.QPushButton(self.collideTab)
        self.refreshCButton.setObjectName("refreshCButton")
        self.horizontalLayout_7.addWidget(self.refreshCButton)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem9)
        self.actionCButton = QtWidgets.QPushButton(self.collideTab)
        self.actionCButton.setObjectName("actionCButton")
        self.horizontalLayout_7.addWidget(self.actionCButton)
        self.verticalLayout_8.addLayout(self.horizontalLayout_7)
        self.tabWidget.addTab(self.collideTab, "")
        self.discardTab = QtWidgets.QWidget()
        self.discardTab.setEnabled(False)
        self.discardTab.setObjectName("discardTab")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.discardTab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.discardTV = QtWidgets.QTableView(self.discardTab)
        self.discardTV.setObjectName("discardTV")
        self.verticalLayout_9.addWidget(self.discardTV)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.refreshDButton = QtWidgets.QPushButton(self.discardTab)
        self.refreshDButton.setObjectName("refreshDButton")
        self.horizontalLayout_8.addWidget(self.refreshDButton)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem10)
        self.actionDButton = QtWidgets.QPushButton(self.discardTab)
        self.actionDButton.setObjectName("actionDButton")
        self.horizontalLayout_8.addWidget(self.actionDButton)
        self.verticalLayout_9.addLayout(self.horizontalLayout_8)
        self.tabWidget.addTab(self.discardTab, "")
        self.reviewTab = QtWidgets.QWidget()
        self.reviewTab.setEnabled(False)
        self.reviewTab.setObjectName("reviewTab")
        self.verticalLayout_19 = QtWidgets.QVBoxLayout(self.reviewTab)
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_6 = QtWidgets.QLabel(self.reviewTab)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_15.addWidget(self.label_6)
        self.questionCB = QtWidgets.QComboBox(self.reviewTab)
        self.questionCB.setObjectName("questionCB")
        self.verticalLayout_15.addWidget(self.questionCB)
        self.horizontalLayout_12.addLayout(self.verticalLayout_15)
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_7 = QtWidgets.QLabel(self.reviewTab)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_16.addWidget(self.label_7)
        self.versionCB = QtWidgets.QComboBox(self.reviewTab)
        self.versionCB.setObjectName("versionCB")
        self.verticalLayout_16.addWidget(self.versionCB)
        self.horizontalLayout_12.addLayout(self.verticalLayout_16)
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_8 = QtWidgets.QLabel(self.reviewTab)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_17.addWidget(self.label_8)
        self.userCB = QtWidgets.QComboBox(self.reviewTab)
        self.userCB.setObjectName("userCB")
        self.verticalLayout_17.addWidget(self.userCB)
        self.horizontalLayout_12.addLayout(self.verticalLayout_17)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem11)
        self.filterB = QtWidgets.QPushButton(self.reviewTab)
        self.filterB.setObjectName("filterB")
        self.horizontalLayout_12.addWidget(self.filterB)
        self.verticalLayout_19.addLayout(self.horizontalLayout_12)
        self.reviewTW = QtWidgets.QTableWidget(self.reviewTab)
        self.reviewTW.setAlternatingRowColors(True)
        self.reviewTW.setColumnCount(7)
        self.reviewTW.setObjectName("reviewTW")
        self.reviewTW.setRowCount(0)
        self.reviewTW.horizontalHeader().setStretchLastSection(True)
        self.reviewTW.verticalHeader().setVisible(False)
        self.reviewTW.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_19.addWidget(self.reviewTW)
        self.tabWidget.addTab(self.reviewTab, "")
        self.verticalLayout_7.addWidget(self.tabWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem12)
        self.closeButton = QtWidgets.QPushButton(IIC)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout_5.addWidget(self.closeButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.retranslateUi(IIC)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(IIC)
        IIC.setTabOrder(self.passwordLE, self.serverLE)
        IIC.setTabOrder(self.serverLE, self.mportSB)
        IIC.setTabOrder(self.mportSB, self.loginButton)
        IIC.setTabOrder(self.loginButton, self.fontSB)
        IIC.setTabOrder(self.fontSB, self.fontButton)
        IIC.setTabOrder(self.fontButton, self.tabWidget)
        IIC.setTabOrder(self.tabWidget, self.userLE)
        IIC.setTabOrder(self.userLE, self.scanTW)
        IIC.setTabOrder(self.scanTW, self.refreshSButton)
        IIC.setTabOrder(self.refreshSButton, self.removePageB)
        IIC.setTabOrder(self.removePageB, self.incompTW)
        IIC.setTabOrder(self.incompTW, self.refreshIButton)
        IIC.setTabOrder(self.refreshIButton, self.subsPageB)
        IIC.setTabOrder(self.subsPageB, self.overallTW)
        IIC.setTabOrder(self.overallTW, self.refreshOButton)
        IIC.setTabOrder(self.refreshOButton, self.papersLE)
        IIC.setTabOrder(self.papersLE, self.refreshIDButon)
        IIC.setTabOrder(self.refreshIDButon, self.selectRectButton)
        IIC.setTabOrder(self.selectRectButton, self.predictButton)
        IIC.setTabOrder(self.predictButton, self.delPredButton)
        IIC.setTabOrder(self.delPredButton, self.predictionTW)
        IIC.setTabOrder(self.predictionTW, self.predListRefreshB)
        IIC.setTabOrder(self.predListRefreshB, self.scrollArea)
        IIC.setTabOrder(self.scrollArea, self.refreshPButton)
        IIC.setTabOrder(self.refreshPButton, self.unknownTV)
        IIC.setTabOrder(self.unknownTV, self.refreshUButton)
        IIC.setTabOrder(self.refreshUButton, self.actionUButton)
        IIC.setTabOrder(self.actionUButton, self.collideTV)
        IIC.setTabOrder(self.collideTV, self.refreshCButton)
        IIC.setTabOrder(self.refreshCButton, self.actionCButton)
        IIC.setTabOrder(self.actionCButton, self.discardTV)
        IIC.setTabOrder(self.discardTV, self.refreshDButton)
        IIC.setTabOrder(self.refreshDButton, self.actionDButton)
        IIC.setTabOrder(self.actionDButton, self.closeButton)

    def retranslateUi(self, IIC):
        _translate = QtCore.QCoreApplication.translate
        IIC.setWindowTitle(_translate("IIC", "Overview and Management"))
        self.userGBox.setTitle(_translate("IIC", "User Information"))
        self.label.setText(_translate("IIC", "Username"))
        self.userLE.setText(_translate("IIC", "manager"))
        self.label_2.setText(_translate("IIC", "Password"))
        self.serverGBox.setTitle(_translate("IIC", "Server Information"))
        self.serverLabel.setText(_translate("IIC", "Server name:"))
        self.serverLE.setText(_translate("IIC", "127.0.0.1"))
        self.mportLabel.setText(_translate("IIC", "Port:"))
        self.fontBox.setTitle(_translate("IIC", "Font size"))
        self.fontLabel.setText(_translate("IIC", "Font size"))
        self.fontButton.setText(_translate("IIC", "Set font"))
        self.loginButton.setText(_translate("IIC", "&Login"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.loginTab), _translate("IIC", "L&ogin"))
        self.groupBox.setTitle(_translate("IIC", "Completely scanned papers"))
        self.refreshSButton.setText(_translate("IIC", "Refresh"))
        self.removePageB.setText(_translate("IIC", "Remove page from server"))
        self.groupBox_3.setTitle(_translate("IIC", "Incomplete papers"))
        self.refreshIButton.setText(_translate("IIC", "Refresh"))
        self.subsPageB.setText(_translate("IIC", "Substitute missing page with blank"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.scanTab), _translate("IIC", "&Scan Status"))
        self.refreshOButton.setText(_translate("IIC", "Refresh"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.overallTab), _translate("IIC", "Overall &Progress"))
        self.groupBox_2.setTitle(_translate("IIC", "ID and Totalling progress, and ID predictions"))
        self.label_3.setText(_translate("IIC", "Number of papers:"))
        self.label_5.setText(_translate("IIC", "Totalling progress"))
        self.label_4.setText(_translate("IIC", "ID progress"))
        self.refreshIDButon.setText(_translate("IIC", "Refresh"))
        self.groupBox_4.setTitle(_translate("IIC", "Read student numbers from ID pages"))
        self.selectRectButton.setText(_translate("IIC", "Select ID rectangle"))
        self.predictButton.setText(_translate("IIC", "Run predictions"))
        self.delPredButton.setText(_translate("IIC", "Delete predictions"))
        self.predGB.setTitle(_translate("IIC", "ID prediction list"))
        self.predictionTW.setSortingEnabled(True)
        self.predListRefreshB.setText(_translate("IIC", "Refresh List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.idTab), _translate("IIC", "&ID Progress"))
        self.refreshPButton.setText(_translate("IIC", "Refresh"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.progressTab), _translate("IIC", "&Marking Progress"))
        self.refreshUButton.setText(_translate("IIC", "Refresh"))
        self.actionUButton.setText(_translate("IIC", "Perform actions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.unknownTab), _translate("IIC", "&Unknown Pages"))
        self.refreshCButton.setText(_translate("IIC", "&Refresh"))
        self.actionCButton.setText(_translate("IIC", "Perfrom actions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.collideTab), _translate("IIC", "&Colliding Pages"))
        self.refreshDButton.setText(_translate("IIC", "Refresh"))
        self.actionDButton.setText(_translate("IIC", "Perform actions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.discardTab), _translate("IIC", "&Discarded Pages"))
        self.label_6.setText(_translate("IIC", "Question"))
        self.label_7.setText(_translate("IIC", "Version"))
        self.label_8.setText(_translate("IIC", "Username"))
        self.filterB.setText(_translate("IIC", "&Filter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reviewTab), _translate("IIC", "&Review Marking"))
        self.closeButton.setText(_translate("IIC", "&Quit"))
