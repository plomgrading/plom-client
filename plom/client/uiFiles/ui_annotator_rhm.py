# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtCreatorFiles/ui_annotator_rhm.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_annotator_rhm(object):
    def setupUi(self, annotator_rhm):
        annotator_rhm.setObjectName("annotator_rhm")
        annotator_rhm.setWindowModality(QtCore.Qt.WindowModal)
        annotator_rhm.resize(862, 670)
        self.gridLayout = QtWidgets.QGridLayout(annotator_rhm)
        self.gridLayout.setObjectName("gridLayout")
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
        self.gridLayout.addWidget(self.pageFrame, 0, 3, 5, 1)
        self.revealBox0 = QtWidgets.QFrame(annotator_rhm)
        self.revealBox0.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.revealBox0.setFrameShadow(QtWidgets.QFrame.Raised)
        self.revealBox0.setObjectName("revealBox0")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.revealBox0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.revealBox1 = QtWidgets.QFrame(self.revealBox0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.revealBox1.sizePolicy().hasHeightForWidth())
        self.revealBox1.setSizePolicy(sizePolicy)
        self.revealBox1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.revealBox1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.revealBox1.setObjectName("revealBox1")
        self.revealLayout = QtWidgets.QGridLayout(self.revealBox1)
        self.revealLayout.setContentsMargins(3, 3, 3, 3)
        self.revealLayout.setSpacing(3)
        self.revealLayout.setObjectName("revealLayout")
        self.deltaButton = QtWidgets.QToolButton(self.revealBox1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deltaButton.sizePolicy().hasHeightForWidth())
        self.deltaButton.setSizePolicy(sizePolicy)
        self.deltaButton.setMinimumSize(QtCore.QSize(45, 0))
        self.deltaButton.setObjectName("deltaButton")
        self.revealLayout.addWidget(self.deltaButton, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.revealBox1, 0, QtCore.Qt.AlignTop)
        self.revealBox2 = QtWidgets.QFrame(self.revealBox0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.revealBox2.sizePolicy().hasHeightForWidth())
        self.revealBox2.setSizePolicy(sizePolicy)
        self.revealBox2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.revealBox2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.revealBox2.setObjectName("revealBox2")
        self.revealLayout2 = QtWidgets.QVBoxLayout(self.revealBox2)
        self.revealLayout2.setContentsMargins(3, 3, 3, 3)
        self.revealLayout2.setSpacing(3)
        self.revealLayout2.setObjectName("revealLayout2")
        self.verticalLayout_2.addWidget(self.revealBox2, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.gridLayout.addWidget(self.revealBox0, 0, 2, 5, 1)
        self.hideableBox = QtWidgets.QFrame(annotator_rhm)
        self.hideableBox.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.hideableBox.setFrameShadow(QtWidgets.QFrame.Raised)
        self.hideableBox.setObjectName("hideableBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.hideableBox)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_3 = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.modeLayout = QtWidgets.QHBoxLayout(self.frame_3)
        self.modeLayout.setContentsMargins(3, 3, 3, 3)
        self.modeLayout.setSpacing(3)
        self.modeLayout.setObjectName("modeLayout")
        self.hideButton = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hideButton.sizePolicy().hasHeightForWidth())
        self.hideButton.setSizePolicy(sizePolicy)
        self.hideButton.setObjectName("hideButton")
        self.modeLayout.addWidget(self.hideButton, 0, QtCore.Qt.AlignRight)
        self.modeLabel = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modeLabel.sizePolicy().hasHeightForWidth())
        self.modeLabel.setSizePolicy(sizePolicy)
        self.modeLabel.setText("<mode>")
        self.modeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modeLabel.setObjectName("modeLabel")
        self.modeLayout.addWidget(self.modeLabel, 0, QtCore.Qt.AlignHCenter)
        self.markLabel = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.markLabel.sizePolicy().hasHeightForWidth())
        self.markLabel.setSizePolicy(sizePolicy)
        self.markLabel.setObjectName("markLabel")
        self.modeLayout.addWidget(self.markLabel, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.frame_3)
        self.frame = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setObjectName("frame")
        self.toolLayout = QtWidgets.QGridLayout(self.frame)
        self.toolLayout.setContentsMargins(3, 3, 3, 3)
        self.toolLayout.setSpacing(3)
        self.toolLayout.setObjectName("toolLayout")
        self.penButton = QtWidgets.QToolButton(self.frame)
        self.penButton.setMinimumSize(QtCore.QSize(45, 0))
        self.penButton.setObjectName("penButton")
        self.toolLayout.addWidget(self.penButton, 0, 4, 1, 1)
        self.textButton = QtWidgets.QToolButton(self.frame)
        self.textButton.setMinimumSize(QtCore.QSize(45, 0))
        self.textButton.setObjectName("textButton")
        self.toolLayout.addWidget(self.textButton, 1, 4, 1, 1)
        self.commentDownButton = QtWidgets.QToolButton(self.frame)
        self.commentDownButton.setMinimumSize(QtCore.QSize(45, 0))
        self.commentDownButton.setToolTipDuration(-1)
        self.commentDownButton.setObjectName("commentDownButton")
        self.toolLayout.addWidget(self.commentDownButton, 2, 3, 1, 1)
        self.commentUpButton = QtWidgets.QToolButton(self.frame)
        self.commentUpButton.setMinimumSize(QtCore.QSize(45, 0))
        self.commentUpButton.setToolTipDuration(-1)
        self.commentUpButton.setObjectName("commentUpButton")
        self.toolLayout.addWidget(self.commentUpButton, 0, 3, 1, 1)
        self.panButton = QtWidgets.QToolButton(self.frame)
        self.panButton.setMinimumSize(QtCore.QSize(45, 0))
        self.panButton.setObjectName("panButton")
        self.toolLayout.addWidget(self.panButton, 0, 0, 1, 1)
        self.lineButton = QtWidgets.QToolButton(self.frame)
        self.lineButton.setMinimumSize(QtCore.QSize(45, 0))
        self.lineButton.setObjectName("lineButton")
        self.toolLayout.addWidget(self.lineButton, 2, 4, 1, 1)
        self.tickButton = QtWidgets.QToolButton(self.frame)
        self.tickButton.setMinimumSize(QtCore.QSize(45, 0))
        self.tickButton.setToolTipDuration(-1)
        self.tickButton.setObjectName("tickButton")
        self.toolLayout.addWidget(self.tickButton, 1, 2, 1, 1)
        self.moveButton = QtWidgets.QToolButton(self.frame)
        self.moveButton.setMinimumSize(QtCore.QSize(45, 0))
        self.moveButton.setObjectName("moveButton")
        self.toolLayout.addWidget(self.moveButton, 2, 0, 1, 1)
        self.redoButton = QtWidgets.QToolButton(self.frame)
        self.redoButton.setMinimumSize(QtCore.QSize(45, 0))
        self.redoButton.setObjectName("redoButton")
        self.toolLayout.addWidget(self.redoButton, 0, 1, 1, 1)
        self.zoomButton = QtWidgets.QToolButton(self.frame)
        self.zoomButton.setMinimumSize(QtCore.QSize(45, 0))
        self.zoomButton.setObjectName("zoomButton")
        self.toolLayout.addWidget(self.zoomButton, 1, 0, 1, 1)
        self.deleteButton = QtWidgets.QToolButton(self.frame)
        self.deleteButton.setMinimumSize(QtCore.QSize(45, 0))
        self.deleteButton.setObjectName("deleteButton")
        self.toolLayout.addWidget(self.deleteButton, 2, 1, 1, 1)
        self.commentButton = QtWidgets.QToolButton(self.frame)
        self.commentButton.setMinimumSize(QtCore.QSize(45, 0))
        self.commentButton.setToolTipDuration(-1)
        self.commentButton.setObjectName("commentButton")
        self.toolLayout.addWidget(self.commentButton, 1, 3, 1, 1)
        self.undoButton = QtWidgets.QToolButton(self.frame)
        self.undoButton.setMinimumSize(QtCore.QSize(45, 0))
        self.undoButton.setObjectName("undoButton")
        self.toolLayout.addWidget(self.undoButton, 1, 1, 1, 1)
        self.crossButton = QtWidgets.QToolButton(self.frame)
        self.crossButton.setMinimumSize(QtCore.QSize(45, 0))
        self.crossButton.setObjectName("crossButton")
        self.toolLayout.addWidget(self.crossButton, 0, 2, 1, 1)
        self.boxButton = QtWidgets.QToolButton(self.frame)
        self.boxButton.setMinimumSize(QtCore.QSize(45, 0))
        self.boxButton.setObjectName("boxButton")
        self.toolLayout.addWidget(self.boxButton, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.frame, 0, QtCore.Qt.AlignHCenter)
        self.frame_4 = QtWidgets.QFrame(self.hideableBox)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.buttonsLayout = QtWidgets.QHBoxLayout(self.frame_4)
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.keyHelpButton = QtWidgets.QPushButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keyHelpButton.sizePolicy().hasHeightForWidth())
        self.keyHelpButton.setSizePolicy(sizePolicy)
        self.keyHelpButton.setObjectName("keyHelpButton")
        self.buttonsLayout.addWidget(self.keyHelpButton)
        self.viewButton = QtWidgets.QPushButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewButton.sizePolicy().hasHeightForWidth())
        self.viewButton.setSizePolicy(sizePolicy)
        self.viewButton.setObjectName("viewButton")
        self.buttonsLayout.addWidget(self.viewButton)
        self.zoomCB = QtWidgets.QComboBox(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoomCB.sizePolicy().hasHeightForWidth())
        self.zoomCB.setSizePolicy(sizePolicy)
        self.zoomCB.setObjectName("zoomCB")
        self.buttonsLayout.addWidget(self.zoomCB)
        self.verticalLayout.addWidget(self.frame_4)
        self.markBox = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.markBox.sizePolicy().hasHeightForWidth())
        self.markBox.setSizePolicy(sizePolicy)
        self.markBox.setObjectName("markBox")
        self.markGrid = QtWidgets.QGridLayout(self.markBox)
        self.markGrid.setContentsMargins(3, 3, 3, 3)
        self.markGrid.setSpacing(3)
        self.markGrid.setObjectName("markGrid")
        self.verticalLayout.addWidget(self.markBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.noAnswerButton = QtWidgets.QPushButton(self.hideableBox)
        self.noAnswerButton.setObjectName("noAnswerButton")
        self.horizontalLayout_2.addWidget(self.noAnswerButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.frame_31 = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.frame_31.sizePolicy().hasHeightForWidth())
        self.frame_31.setSizePolicy(sizePolicy)
        self.frame_31.setObjectName("frame_31")
        self.commentGrid = QtWidgets.QGridLayout(self.frame_31)
        self.commentGrid.setContentsMargins(3, 3, 3, 3)
        self.commentGrid.setSpacing(3)
        self.commentGrid.setObjectName("commentGrid")
        self.verticalLayout.addWidget(self.frame_31)
        self.frame_2 = QtWidgets.QFrame(self.hideableBox)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.ebLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.ebLayout.setContentsMargins(3, 3, 3, 3)
        self.ebLayout.setSpacing(3)
        self.ebLayout.setObjectName("ebLayout")
        self.finishedButton = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.finishedButton.sizePolicy().hasHeightForWidth())
        self.finishedButton.setSizePolicy(sizePolicy)
        self.finishedButton.setWhatsThis("")
        self.finishedButton.setObjectName("finishedButton")
        self.ebLayout.addWidget(self.finishedButton)
        self.finishNoRelaunchButton = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.finishNoRelaunchButton.sizePolicy().hasHeightForWidth())
        self.finishNoRelaunchButton.setSizePolicy(sizePolicy)
        self.finishNoRelaunchButton.setObjectName("finishNoRelaunchButton")
        self.ebLayout.addWidget(self.finishNoRelaunchButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setObjectName("cancelButton")
        self.ebLayout.addWidget(self.cancelButton)
        self.verticalLayout.addWidget(self.frame_2)
        self.gridLayout.addWidget(self.hideableBox, 0, 1, 5, 1)

        self.retranslateUi(annotator_rhm)
        QtCore.QMetaObject.connectSlotsByName(annotator_rhm)
        annotator_rhm.setTabOrder(self.finishedButton, self.cancelButton)

    def retranslateUi(self, annotator_rhm):
        _translate = QtCore.QCoreApplication.translate
        annotator_rhm.setWindowTitle(_translate("annotator_rhm", "Annotate paper"))
        self.deltaButton.setText(_translate("annotator_rhm", "..."))
        self.hideButton.setText(_translate("annotator_rhm", "Compact"))
        self.markLabel.setText(_translate("annotator_rhm", "kkk out of nnn"))
        self.penButton.setToolTip(_translate("annotator_rhm", "press t"))
        self.penButton.setText(_translate("annotator_rhm", "..."))
        self.textButton.setToolTip(_translate("annotator_rhm", "press g"))
        self.textButton.setText(_translate("annotator_rhm", "..."))
        self.commentDownButton.setToolTip(_translate("annotator_rhm", "press v"))
        self.commentDownButton.setText(_translate("annotator_rhm", "..."))
        self.commentUpButton.setToolTip(_translate("annotator_rhm", "press r"))
        self.commentUpButton.setText(_translate("annotator_rhm", "..."))
        self.panButton.setToolTip(_translate("annotator_rhm", "press q"))
        self.panButton.setText(_translate("annotator_rhm", "..."))
        self.lineButton.setToolTip(_translate("annotator_rhm", "press b"))
        self.lineButton.setText(_translate("annotator_rhm", "..."))
        self.tickButton.setToolTip(_translate("annotator_rhm", "press d"))
        self.tickButton.setText(_translate("annotator_rhm", "..."))
        self.moveButton.setToolTip(_translate("annotator_rhm", "press z"))
        self.moveButton.setText(_translate("annotator_rhm", "..."))
        self.redoButton.setToolTip(_translate("annotator_rhm", "press w"))
        self.redoButton.setText(_translate("annotator_rhm", "..."))
        self.zoomButton.setToolTip(_translate("annotator_rhm", "press a"))
        self.zoomButton.setText(_translate("annotator_rhm", "..."))
        self.deleteButton.setToolTip(_translate("annotator_rhm", "press x"))
        self.deleteButton.setText(_translate("annotator_rhm", "..."))
        self.commentButton.setToolTip(_translate("annotator_rhm", "press f"))
        self.commentButton.setText(_translate("annotator_rhm", "..."))
        self.undoButton.setToolTip(_translate("annotator_rhm", "press s"))
        self.undoButton.setText(_translate("annotator_rhm", "..."))
        self.crossButton.setToolTip(_translate("annotator_rhm", "press e"))
        self.crossButton.setText(_translate("annotator_rhm", "..."))
        self.boxButton.setToolTip(_translate("annotator_rhm", "press c"))
        self.boxButton.setText(_translate("annotator_rhm", "..."))
        self.keyHelpButton.setToolTip(_translate("annotator_rhm", "List shortcut keys"))
        self.keyHelpButton.setText(_translate("annotator_rhm", "Key help"))
        self.viewButton.setToolTip(_translate("annotator_rhm", "Show entire paper in new window"))
        self.viewButton.setText(_translate("annotator_rhm", "View all"))
        self.noAnswerButton.setText(_translate("annotator_rhm", "No answer given"))
        self.finishedButton.setToolTip(_translate("annotator_rhm", "Save and move to the next paper"))
        self.finishedButton.setText(_translate("annotator_rhm", "Next"))
        self.finishNoRelaunchButton.setToolTip(_translate("annotator_rhm", "Save and return to marker window"))
        self.finishNoRelaunchButton.setText(_translate("annotator_rhm", "Done"))
        self.cancelButton.setToolTip(_translate("annotator_rhm", "Cancel the current annotations and return to marker window"))
        self.cancelButton.setText(_translate("annotator_rhm", "&Cancel"))
