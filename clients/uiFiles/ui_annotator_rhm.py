# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_annotator_righthandmouse.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_annotator_rhm(object):
    def setupUi(self, annotator_rhm):
        annotator_rhm.setObjectName("annotator_rhm")
        annotator_rhm.resize(862, 670)
        self.gridLayout = QtWidgets.QGridLayout(annotator_rhm)
        self.gridLayout.setObjectName("gridLayout")
        self.markBox = QtWidgets.QGroupBox(annotator_rhm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.markBox.sizePolicy().hasHeightForWidth())
        self.markBox.setSizePolicy(sizePolicy)
        self.markBox.setObjectName("markBox")
        self.markGrid = QtWidgets.QGridLayout(self.markBox)
        self.markGrid.setContentsMargins(3, 3, 3, 3)
        self.markGrid.setSpacing(3)
        self.markGrid.setObjectName("markGrid")
        self.gridLayout.addWidget(self.markBox, 2, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(annotator_rhm)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.finishNoRelaunchButton = QtWidgets.QPushButton(self.frame_2)
        self.finishNoRelaunchButton.setObjectName("finishNoRelaunchButton")
        self.gridLayout_2.addWidget(self.finishNoRelaunchButton, 0, 2, 1, 1)
        self.cancelButton = QtWidgets.QPushButton(self.frame_2)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout_2.addWidget(self.cancelButton, 0, 4, 1, 1)
        self.finishedButton = QtWidgets.QPushButton(self.frame_2)
        self.finishedButton.setObjectName("finishedButton")
        self.gridLayout_2.addWidget(self.finishedButton, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.frame_2, 5, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(annotator_rhm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName("groupBox_3")
        self.commentGrid = QtWidgets.QGridLayout(self.groupBox_3)
        self.commentGrid.setContentsMargins(3, 3, 3, 3)
        self.commentGrid.setSpacing(3)
        self.commentGrid.setObjectName("commentGrid")
        self.gridLayout.addWidget(self.groupBox_3, 4, 0, 1, 1)
        self.pageFrame = QtWidgets.QFrame(annotator_rhm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pageFrame.sizePolicy().hasHeightForWidth())
        self.pageFrame.setSizePolicy(sizePolicy)
        self.pageFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.pageFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pageFrame.setObjectName("pageFrame")
        self.pageFrameGrid = QtWidgets.QGridLayout(self.pageFrame)
        self.pageFrameGrid.setContentsMargins(3, 3, 3, 3)
        self.pageFrameGrid.setObjectName("pageFrameGrid")
        self.gridLayout.addWidget(self.pageFrame, 0, 1, 6, 1)
        self.groupBox = QtWidgets.QGroupBox(annotator_rhm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.crossButton = QtWidgets.QToolButton(self.groupBox)
        self.crossButton.setObjectName("crossButton")
        self.gridLayout_3.addWidget(self.crossButton, 0, 4, 1, 1)
        self.commentUpButton = QtWidgets.QToolButton(self.groupBox)
        self.commentUpButton.setToolTipDuration(-1)
        self.commentUpButton.setObjectName("commentUpButton")
        self.gridLayout_3.addWidget(self.commentUpButton, 0, 5, 1, 1)
        self.tickButton = QtWidgets.QToolButton(self.groupBox)
        self.tickButton.setToolTipDuration(-1)
        self.tickButton.setObjectName("tickButton")
        self.gridLayout_3.addWidget(self.tickButton, 1, 4, 1, 1)
        self.commentButton = QtWidgets.QToolButton(self.groupBox)
        self.commentButton.setToolTipDuration(-1)
        self.commentButton.setObjectName("commentButton")
        self.gridLayout_3.addWidget(self.commentButton, 1, 5, 1, 1)
        self.boxButton = QtWidgets.QToolButton(self.groupBox)
        self.boxButton.setObjectName("boxButton")
        self.gridLayout_3.addWidget(self.boxButton, 2, 4, 1, 1)
        self.commentDownButton = QtWidgets.QToolButton(self.groupBox)
        self.commentDownButton.setToolTipDuration(-1)
        self.commentDownButton.setObjectName("commentDownButton")
        self.gridLayout_3.addWidget(self.commentDownButton, 2, 5, 1, 1)
        self.penButton = QtWidgets.QToolButton(self.groupBox)
        self.penButton.setObjectName("penButton")
        self.gridLayout_3.addWidget(self.penButton, 0, 6, 1, 1)
        self.textButton = QtWidgets.QToolButton(self.groupBox)
        self.textButton.setObjectName("textButton")
        self.gridLayout_3.addWidget(self.textButton, 1, 6, 1, 1)
        self.lineButton = QtWidgets.QToolButton(self.groupBox)
        self.lineButton.setObjectName("lineButton")
        self.gridLayout_3.addWidget(self.lineButton, 2, 6, 1, 1)
        self.deleteButton = QtWidgets.QToolButton(self.groupBox)
        self.deleteButton.setObjectName("deleteButton")
        self.gridLayout_3.addWidget(self.deleteButton, 2, 3, 1, 1)
        self.undoButton = QtWidgets.QToolButton(self.groupBox)
        self.undoButton.setObjectName("undoButton")
        self.gridLayout_3.addWidget(self.undoButton, 1, 3, 1, 1)
        self.redoButton = QtWidgets.QToolButton(self.groupBox)
        self.redoButton.setObjectName("redoButton")
        self.gridLayout_3.addWidget(self.redoButton, 0, 3, 1, 1)
        self.panButton = QtWidgets.QToolButton(self.groupBox)
        self.panButton.setObjectName("panButton")
        self.gridLayout_3.addWidget(self.panButton, 0, 2, 1, 1)
        self.zoomButton = QtWidgets.QToolButton(self.groupBox)
        self.zoomButton.setObjectName("zoomButton")
        self.gridLayout_3.addWidget(self.zoomButton, 1, 2, 1, 1)
        self.moveButton = QtWidgets.QToolButton(self.groupBox)
        self.moveButton.setObjectName("moveButton")
        self.gridLayout_3.addWidget(self.moveButton, 2, 2, 1, 1)
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.keyHelpButton = QtWidgets.QPushButton(self.frame)
        self.keyHelpButton.setObjectName("keyHelpButton")
        self.horizontalLayout.addWidget(self.keyHelpButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout_3.addWidget(self.frame, 3, 2, 1, 5)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(annotator_rhm)
        QtCore.QMetaObject.connectSlotsByName(annotator_rhm)
        annotator_rhm.setTabOrder(self.finishedButton, self.cancelButton)

    def retranslateUi(self, annotator_rhm):
        _translate = QtCore.QCoreApplication.translate
        annotator_rhm.setWindowTitle(_translate("annotator_rhm", "Annotate paper"))
        self.markBox.setTitle(_translate("annotator_rhm", "Enter Mark"))
        self.finishNoRelaunchButton.setText(_translate("annotator_rhm", "End && \n"
" Return"))
        self.cancelButton.setText(_translate("annotator_rhm", "&Cancel"))
        self.finishedButton.setText(_translate("annotator_rhm", "End && \n"
" Next"))
        self.groupBox_3.setTitle(_translate("annotator_rhm", "Comment list"))
        self.groupBox.setTitle(_translate("annotator_rhm", "Tools"))
        self.crossButton.setToolTip(_translate("annotator_rhm", "press e"))
        self.crossButton.setText(_translate("annotator_rhm", "..."))
        self.commentUpButton.setToolTip(_translate("annotator_rhm", "press r"))
        self.commentUpButton.setText(_translate("annotator_rhm", "..."))
        self.tickButton.setToolTip(_translate("annotator_rhm", "press d"))
        self.tickButton.setText(_translate("annotator_rhm", "..."))
        self.commentButton.setToolTip(_translate("annotator_rhm", "press f"))
        self.commentButton.setText(_translate("annotator_rhm", "..."))
        self.boxButton.setToolTip(_translate("annotator_rhm", "press c"))
        self.boxButton.setText(_translate("annotator_rhm", "..."))
        self.commentDownButton.setToolTip(_translate("annotator_rhm", "press v"))
        self.commentDownButton.setText(_translate("annotator_rhm", "..."))
        self.penButton.setToolTip(_translate("annotator_rhm", "press t"))
        self.penButton.setText(_translate("annotator_rhm", "..."))
        self.textButton.setToolTip(_translate("annotator_rhm", "press g"))
        self.textButton.setText(_translate("annotator_rhm", "..."))
        self.lineButton.setToolTip(_translate("annotator_rhm", "press b"))
        self.lineButton.setText(_translate("annotator_rhm", "..."))
        self.deleteButton.setToolTip(_translate("annotator_rhm", "press x"))
        self.deleteButton.setText(_translate("annotator_rhm", "..."))
        self.undoButton.setToolTip(_translate("annotator_rhm", "press s"))
        self.undoButton.setText(_translate("annotator_rhm", "..."))
        self.redoButton.setToolTip(_translate("annotator_rhm", "press w"))
        self.redoButton.setText(_translate("annotator_rhm", "..."))
        self.panButton.setToolTip(_translate("annotator_rhm", "press q"))
        self.panButton.setText(_translate("annotator_rhm", "..."))
        self.zoomButton.setToolTip(_translate("annotator_rhm", "press a"))
        self.zoomButton.setText(_translate("annotator_rhm", "..."))
        self.moveButton.setToolTip(_translate("annotator_rhm", "press z"))
        self.moveButton.setText(_translate("annotator_rhm", "..."))
        self.keyHelpButton.setText(_translate("annotator_rhm", "Key Help"))

