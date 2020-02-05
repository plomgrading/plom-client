# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../qtCreatorFiles/ui_marker.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MarkerWindow(object):
    def setupUi(self, MarkerWindow):
        MarkerWindow.setObjectName("MarkerWindow")
        MarkerWindow.setWindowModality(QtCore.Qt.WindowModal)
        MarkerWindow.resize(1024, 768)
        self.gridLayout_3 = QtWidgets.QGridLayout(MarkerWindow)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.closeButton = QtWidgets.QPushButton(MarkerWindow)
        self.closeButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.gridLayout_3.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.widget = QtWidgets.QWidget(MarkerWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.userBox = QtWidgets.QGroupBox(self.widget)
        self.userBox.setObjectName("userBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.userBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_2 = QtWidgets.QLabel(self.userBox)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.pgLabel = QtWidgets.QLabel(self.userBox)
        self.pgLabel.setObjectName("pgLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pgLabel)
        self.label_3 = QtWidgets.QLabel(self.userBox)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.vLabel = QtWidgets.QLabel(self.userBox)
        self.vLabel.setObjectName("vLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.vLabel)
        self.label_5 = QtWidgets.QLabel(self.userBox)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.scoreLabel = QtWidgets.QLabel(self.userBox)
        self.scoreLabel.setObjectName("scoreLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.scoreLabel)
        self.verticalLayout_2.addWidget(self.userBox)
        self.tableBox = QtWidgets.QGroupBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tableBox.sizePolicy().hasHeightForWidth())
        self.tableBox.setSizePolicy(sizePolicy)
        self.tableBox.setObjectName("tableBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tableBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableView = SimpleTableView(self.tableBox)
        self.tableView.setMinimumSize(QtCore.QSize(250, 0))
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.gridLayout_2.addWidget(self.tableView, 0, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.tableBox)
        self.buttonFrame = QtWidgets.QFrame(self.widget)
        self.buttonFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttonFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttonFrame.setObjectName("buttonFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.buttonFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.filterButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterButton.sizePolicy().hasHeightForWidth())
        self.filterButton.setSizePolicy(sizePolicy)
        self.filterButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.filterButton.setObjectName("filterButton")
        self.gridLayout.addWidget(self.filterButton, 4, 0, 1, 1)
        self.filterLE = QtWidgets.QLineEdit(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterLE.sizePolicy().hasHeightForWidth())
        self.filterLE.setSizePolicy(sizePolicy)
        self.filterLE.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.filterLE.setMaxLength(256)
        self.filterLE.setClearButtonEnabled(True)
        self.filterLE.setObjectName("filterLE")
        self.gridLayout.addWidget(self.filterLE, 4, 1, 1, 3)
        self.annButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.annButton.sizePolicy().hasHeightForWidth())
        self.annButton.setSizePolicy(sizePolicy)
        self.annButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.annButton.setObjectName("annButton")
        self.gridLayout.addWidget(self.annButton, 0, 0, 1, 3)
        self.getNextButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.getNextButton.sizePolicy().hasHeightForWidth())
        self.getNextButton.setSizePolicy(sizePolicy)
        self.getNextButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.getNextButton.setObjectName("getNextButton")
        self.gridLayout.addWidget(self.getNextButton, 0, 3, 1, 1)
        self.revertButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.revertButton.sizePolicy().hasHeightForWidth())
        self.revertButton.setSizePolicy(sizePolicy)
        self.revertButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.revertButton.setObjectName("revertButton")
        self.gridLayout.addWidget(self.revertButton, 3, 0, 1, 1)
        self.deferButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deferButton.sizePolicy().hasHeightForWidth())
        self.deferButton.setSizePolicy(sizePolicy)
        self.deferButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.deferButton.setObjectName("deferButton")
        self.gridLayout.addWidget(self.deferButton, 3, 1, 1, 1)
        self.tagButton = QtWidgets.QPushButton(self.buttonFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagButton.sizePolicy().hasHeightForWidth())
        self.tagButton.setSizePolicy(sizePolicy)
        self.tagButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tagButton.setObjectName("tagButton")
        self.gridLayout.addWidget(self.tagButton, 3, 2, 1, 1)
        self.viewButton = QtWidgets.QPushButton(self.buttonFrame)
        self.viewButton.setObjectName("viewButton")
        self.gridLayout.addWidget(self.viewButton, 3, 3, 1, 1)
        self.verticalLayout_2.addWidget(self.buttonFrame)
        self.styleChoiceBox = QtWidgets.QGroupBox(self.widget)
        self.styleChoiceBox.setObjectName("styleChoiceBox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.styleChoiceBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.markUpRB = QtWidgets.QRadioButton(self.styleChoiceBox)
        self.markUpRB.setChecked(True)
        self.markUpRB.setObjectName("markUpRB")
        self.markStyleGroup = QtWidgets.QButtonGroup(MarkerWindow)
        self.markStyleGroup.setObjectName("markStyleGroup")
        self.markStyleGroup.addButton(self.markUpRB)
        self.horizontalLayout_4.addWidget(self.markUpRB)
        self.markDownRB = QtWidgets.QRadioButton(self.styleChoiceBox)
        self.markDownRB.setChecked(False)
        self.markDownRB.setObjectName("markDownRB")
        self.markStyleGroup.addButton(self.markDownRB)
        self.horizontalLayout_4.addWidget(self.markDownRB)
        self.markTotalRB = QtWidgets.QRadioButton(self.styleChoiceBox)
        self.markTotalRB.setObjectName("markTotalRB")
        self.markStyleGroup.addButton(self.markTotalRB)
        self.horizontalLayout_4.addWidget(self.markTotalRB)
        self.verticalLayout_2.addWidget(self.styleChoiceBox)
        self.handChoiceBox = QtWidgets.QGroupBox(self.widget)
        self.handChoiceBox.setObjectName("handChoiceBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.handChoiceBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.leftMouseRB = QtWidgets.QRadioButton(self.handChoiceBox)
        self.leftMouseRB.setObjectName("leftMouseRB")
        self.mouseHandGroup = QtWidgets.QButtonGroup(MarkerWindow)
        self.mouseHandGroup.setObjectName("mouseHandGroup")
        self.mouseHandGroup.addButton(self.leftMouseRB)
        self.horizontalLayout_3.addWidget(self.leftMouseRB)
        self.rightMouseRB = QtWidgets.QRadioButton(self.handChoiceBox)
        self.rightMouseRB.setChecked(True)
        self.rightMouseRB.setObjectName("rightMouseRB")
        self.mouseHandGroup.addButton(self.rightMouseRB)
        self.horizontalLayout_3.addWidget(self.rightMouseRB)
        self.verticalLayout_2.addWidget(self.handChoiceBox)
        self.frameProgress = QtWidgets.QFrame(self.widget)
        self.frameProgress.setObjectName("frameProgress")
        self.layoutProgress = QtWidgets.QHBoxLayout(self.frameProgress)
        self.layoutProgress.setContentsMargins(0, -1, 0, -1)
        self.layoutProgress.setObjectName("layoutProgress")
        self.labelProgress = QtWidgets.QLabel(self.frameProgress)
        self.labelProgress.setObjectName("labelProgress")
        self.layoutProgress.addWidget(self.labelProgress)
        self.mProgressBar = QtWidgets.QProgressBar(self.frameProgress)
        self.mProgressBar.setProperty("value", 1)
        self.mProgressBar.setObjectName("mProgressBar")
        self.layoutProgress.addWidget(self.mProgressBar)
        self.verticalLayout_2.addWidget(self.frameProgress)
        self.gridLayout_3.addWidget(self.widget, 0, 0, 1, 1)
        self.widget_2 = QtWidgets.QWidget(MarkerWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.paperBox = QtWidgets.QGroupBox(self.widget_2)
        self.paperBox.setObjectName("paperBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.paperBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_4.addWidget(self.paperBox, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.widget_2, 0, 1, 3, 1)

        self.retranslateUi(MarkerWindow)
        QtCore.QMetaObject.connectSlotsByName(MarkerWindow)
        MarkerWindow.setTabOrder(self.tableView, self.closeButton)

    def retranslateUi(self, MarkerWindow):
        _translate = QtCore.QCoreApplication.translate
        MarkerWindow.setWindowTitle(_translate("MarkerWindow", "Mark papers"))
        self.closeButton.setText(_translate("MarkerWindow", "&Close"))
        self.userBox.setTitle(_translate("MarkerWindow", "User"))
        self.label_2.setText(_translate("MarkerWindow", "Pagegroup "))
        self.pgLabel.setText(_translate("MarkerWindow", "NUMBER"))
        self.label_3.setText(_translate("MarkerWindow", "Version"))
        self.vLabel.setText(_translate("MarkerWindow", "NUMBER"))
        self.label_5.setText(_translate("MarkerWindow", "Max score"))
        self.scoreLabel.setText(_translate("MarkerWindow", "NUMBER"))
        self.tableBox.setTitle(_translate("MarkerWindow", "Paper list"))
        self.filterButton.setText(_translate("MarkerWindow", "Filter"))
        self.filterLE.setPlaceholderText(_translate("MarkerWindow", "Filter on tag text"))
        self.annButton.setText(_translate("MarkerWindow", "&Annotate && mark"))
        self.getNextButton.setText(_translate("MarkerWindow", "&Get next"))
        self.revertButton.setText(_translate("MarkerWindow", "&Revert"))
        self.deferButton.setText(_translate("MarkerWindow", "Defer"))
        self.tagButton.setText(_translate("MarkerWindow", "Tag"))
        self.viewButton.setText(_translate("MarkerWindow", "View"))
        self.styleChoiceBox.setTitle(_translate("MarkerWindow", "Marking style"))
        self.markUpRB.setText(_translate("MarkerWindow", "&Up"))
        self.markDownRB.setText(_translate("MarkerWindow", "&Down"))
        self.markTotalRB.setText(_translate("MarkerWindow", "&Total"))
        self.handChoiceBox.setTitle(_translate("MarkerWindow", "Mouse Hand"))
        self.leftMouseRB.setText(_translate("MarkerWindow", "&Left"))
        self.rightMouseRB.setText(_translate("MarkerWindow", "Ri&ght"))
        self.labelProgress.setText(_translate("MarkerWindow", "Progress:"))
        self.mProgressBar.setFormat(_translate("MarkerWindow", "%v of %m"))
        self.paperBox.setTitle(_translate("MarkerWindow", "Current paper"))
from useful_classes import SimpleTableView
