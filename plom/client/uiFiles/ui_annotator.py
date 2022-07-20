# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtCreatorFiles/ui_annotator.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_annotator(object):
    def setupUi(self, annotator):
        annotator.setObjectName("annotator")
        annotator.setWindowModality(QtCore.Qt.WindowModal)
        annotator.resize(862, 670)
        self.horizontalLayout = QtWidgets.QHBoxLayout(annotator)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.hideableBox = QtWidgets.QFrame(annotator)
        self.hideableBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.hideableBox.setFrameShadow(QtWidgets.QFrame.Raised)
        self.hideableBox.setObjectName("hideableBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.hideableBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frameTools = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameTools.sizePolicy().hasHeightForWidth())
        self.frameTools.setSizePolicy(sizePolicy)
        self.frameTools.setObjectName("frameTools")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frameTools)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout1.setObjectName("horizontalLayout1")
        self.hamMenuButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.hamMenuButton.sizePolicy().hasHeightForWidth())
        self.hamMenuButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.hamMenuButton.setFont(font)
        self.hamMenuButton.setText("☰")
        self.hamMenuButton.setObjectName("hamMenuButton")
        self.horizontalLayout1.addWidget(self.hamMenuButton)
        self.markLabel = QtWidgets.QLabel(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.markLabel.sizePolicy().hasHeightForWidth())
        self.markLabel.setSizePolicy(sizePolicy)
        self.markLabel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.markLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.markLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.markLabel.setObjectName("markLabel")
        self.horizontalLayout1.addWidget(self.markLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.finishedButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.finishedButton.sizePolicy().hasHeightForWidth())
        self.finishedButton.setSizePolicy(sizePolicy)
        self.finishedButton.setWhatsThis("")
        self.finishedButton.setObjectName("finishedButton")
        self.horizontalLayout_2.addWidget(self.finishedButton)
        self.helpButton = QtWidgets.QPushButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.helpButton.sizePolicy().hasHeightForWidth())
        self.helpButton.setSizePolicy(sizePolicy)
        self.helpButton.setObjectName("helpButton")
        self.horizontalLayout_2.addWidget(self.helpButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.zoomCB = QtWidgets.QComboBox(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoomCB.sizePolicy().hasHeightForWidth())
        self.zoomCB.setSizePolicy(sizePolicy)
        self.zoomCB.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.zoomCB.setObjectName("zoomCB")
        self.horizontalLayout2.addWidget(self.zoomCB)
        self.zoomButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoomButton.sizePolicy().hasHeightForWidth())
        self.zoomButton.setSizePolicy(sizePolicy)
        self.zoomButton.setIconSize(QtCore.QSize(24, 24))
        self.zoomButton.setCheckable(True)
        self.zoomButton.setAutoExclusive(True)
        self.zoomButton.setObjectName("zoomButton")
        self.horizontalLayout2.addWidget(self.zoomButton)
        self.panButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.panButton.sizePolicy().hasHeightForWidth())
        self.panButton.setSizePolicy(sizePolicy)
        self.panButton.setIconSize(QtCore.QSize(24, 24))
        self.panButton.setCheckable(True)
        self.panButton.setAutoExclusive(True)
        self.panButton.setObjectName("panButton")
        self.horizontalLayout2.addWidget(self.panButton)
        self.rearrangePagesButton = QtWidgets.QPushButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rearrangePagesButton.sizePolicy().hasHeightForWidth())
        self.rearrangePagesButton.setSizePolicy(sizePolicy)
        self.rearrangePagesButton.setObjectName("rearrangePagesButton")
        self.horizontalLayout2.addWidget(self.rearrangePagesButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout2)
        self.horizontalLayout3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout3.setObjectName("horizontalLayout3")
        self.deleteButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)
        self.deleteButton.setIconSize(QtCore.QSize(24, 24))
        self.deleteButton.setCheckable(True)
        self.deleteButton.setAutoExclusive(True)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout3.addWidget(self.deleteButton)
        self.undoButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.undoButton.sizePolicy().hasHeightForWidth())
        self.undoButton.setSizePolicy(sizePolicy)
        self.undoButton.setIconSize(QtCore.QSize(24, 24))
        self.undoButton.setObjectName("undoButton")
        self.horizontalLayout3.addWidget(self.undoButton)
        self.redoButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.redoButton.sizePolicy().hasHeightForWidth())
        self.redoButton.setSizePolicy(sizePolicy)
        self.redoButton.setIconSize(QtCore.QSize(24, 24))
        self.redoButton.setObjectName("redoButton")
        self.horizontalLayout3.addWidget(self.redoButton)
        self.moveButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.moveButton.sizePolicy().hasHeightForWidth())
        self.moveButton.setSizePolicy(sizePolicy)
        self.moveButton.setIconSize(QtCore.QSize(24, 24))
        self.moveButton.setCheckable(True)
        self.moveButton.setAutoExclusive(True)
        self.moveButton.setObjectName("moveButton")
        self.horizontalLayout3.addWidget(self.moveButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout3)
        self.wideModeLabel = QtWidgets.QLabel(self.frameTools)
        self.wideModeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.wideModeLabel.setObjectName("wideModeLabel")
        self.verticalLayout_3.addWidget(self.wideModeLabel)
        self.horizontalLayout4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout4.setObjectName("horizontalLayout4")
        self.boxButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boxButton.sizePolicy().hasHeightForWidth())
        self.boxButton.setSizePolicy(sizePolicy)
        self.boxButton.setMinimumSize(QtCore.QSize(45, 0))
        self.boxButton.setIconSize(QtCore.QSize(40, 40))
        self.boxButton.setCheckable(True)
        self.boxButton.setAutoExclusive(True)
        self.boxButton.setObjectName("boxButton")
        self.horizontalLayout4.addWidget(self.boxButton)
        self.tickButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tickButton.sizePolicy().hasHeightForWidth())
        self.tickButton.setSizePolicy(sizePolicy)
        self.tickButton.setMinimumSize(QtCore.QSize(45, 0))
        self.tickButton.setToolTipDuration(-1)
        self.tickButton.setIconSize(QtCore.QSize(40, 40))
        self.tickButton.setCheckable(True)
        self.tickButton.setAutoExclusive(True)
        self.tickButton.setObjectName("tickButton")
        self.horizontalLayout4.addWidget(self.tickButton)
        self.crossButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.crossButton.sizePolicy().hasHeightForWidth())
        self.crossButton.setSizePolicy(sizePolicy)
        self.crossButton.setMinimumSize(QtCore.QSize(45, 0))
        self.crossButton.setIconSize(QtCore.QSize(40, 40))
        self.crossButton.setCheckable(True)
        self.crossButton.setAutoExclusive(True)
        self.crossButton.setObjectName("crossButton")
        self.horizontalLayout4.addWidget(self.crossButton)
        self.textButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textButton.sizePolicy().hasHeightForWidth())
        self.textButton.setSizePolicy(sizePolicy)
        self.textButton.setMinimumSize(QtCore.QSize(45, 0))
        self.textButton.setIconSize(QtCore.QSize(40, 40))
        self.textButton.setCheckable(True)
        self.textButton.setAutoExclusive(True)
        self.textButton.setObjectName("textButton")
        self.horizontalLayout4.addWidget(self.textButton)
        self.lineButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineButton.sizePolicy().hasHeightForWidth())
        self.lineButton.setSizePolicy(sizePolicy)
        self.lineButton.setMinimumSize(QtCore.QSize(45, 0))
        self.lineButton.setIconSize(QtCore.QSize(40, 40))
        self.lineButton.setCheckable(True)
        self.lineButton.setAutoExclusive(True)
        self.lineButton.setObjectName("lineButton")
        self.horizontalLayout4.addWidget(self.lineButton)
        self.penButton = QtWidgets.QToolButton(self.frameTools)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.penButton.sizePolicy().hasHeightForWidth())
        self.penButton.setSizePolicy(sizePolicy)
        self.penButton.setMinimumSize(QtCore.QSize(45, 0))
        self.penButton.setIconSize(QtCore.QSize(40, 40))
        self.penButton.setCheckable(True)
        self.penButton.setAutoExclusive(True)
        self.penButton.setObjectName("penButton")
        self.horizontalLayout4.addWidget(self.penButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout4)
        self.verticalLayout.addWidget(self.frameTools)
        self.frame7_comment = QtWidgets.QFrame(self.hideableBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.frame7_comment.sizePolicy().hasHeightForWidth())
        self.frame7_comment.setSizePolicy(sizePolicy)
        self.frame7_comment.setObjectName("frame7_comment")
        self.container_rubricwidget = QtWidgets.QVBoxLayout(self.frame7_comment)
        self.container_rubricwidget.setContentsMargins(0, -1, 0, 0)
        self.container_rubricwidget.setObjectName("container_rubricwidget")
        self.frame6 = QtWidgets.QFrame(self.frame7_comment)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame6.sizePolicy().hasHeightForWidth())
        self.frame6.setSizePolicy(sizePolicy)
        self.frame6.setObjectName("frame6")
        self.hboxlayout = QtWidgets.QHBoxLayout(self.frame6)
        self.hboxlayout.setContentsMargins(0, 0, 0, 0)
        self.hboxlayout.setObjectName("hboxlayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.noAnswerButton = QtWidgets.QPushButton(self.frame6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.noAnswerButton.sizePolicy().hasHeightForWidth())
        self.noAnswerButton.setSizePolicy(sizePolicy)
        self.noAnswerButton.setMinimumSize(QtCore.QSize(0, 45))
        self.noAnswerButton.setObjectName("noAnswerButton")
        self.hboxlayout.addWidget(self.noAnswerButton)
        spacerItem1 = QtWidgets.QSpacerItem(6, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.container_rubricwidget.addWidget(self.frame6)
        self.verticalLayout.addWidget(self.frame7_comment)
        self.horizontalLayout.addWidget(self.hideableBox)
        self.revealBox0 = QtWidgets.QFrame(annotator)
        self.revealBox0.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.revealBox0.setFrameShadow(QtWidgets.QFrame.Raised)
        self.revealBox0.setObjectName("revealBox0")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.revealBox0)
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
        self.revealLayout.setContentsMargins(0, 0, 0, 0)
        self.revealLayout.setSpacing(3)
        self.revealLayout.setObjectName("revealLayout")
        self.narrowMarkLabel = QtWidgets.QLabel(self.revealBox1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.narrowMarkLabel.sizePolicy().hasHeightForWidth())
        self.narrowMarkLabel.setSizePolicy(sizePolicy)
        self.narrowMarkLabel.setMinimumSize(QtCore.QSize(0, 34))
        self.narrowMarkLabel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.narrowMarkLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.narrowMarkLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.narrowMarkLabel.setObjectName("narrowMarkLabel")
        self.revealLayout.addWidget(self.narrowMarkLabel, 1, 0, 1, 1)
        self.narrowModeLabel = QtWidgets.QLabel(self.revealBox1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.narrowModeLabel.sizePolicy().hasHeightForWidth())
        self.narrowModeLabel.setSizePolicy(sizePolicy)
        self.narrowModeLabel.setMinimumSize(QtCore.QSize(0, 34))
        self.narrowModeLabel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.narrowModeLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.narrowModeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.narrowModeLabel.setObjectName("narrowModeLabel")
        self.revealLayout.addWidget(self.narrowModeLabel, 2, 0, 1, 1)
        self.wideButton = QtWidgets.QPushButton(self.revealBox1)
        self.wideButton.setMinimumSize(QtCore.QSize(0, 34))
        self.wideButton.setObjectName("wideButton")
        self.revealLayout.addWidget(self.wideButton, 5, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.revealLayout.addItem(spacerItem2, 4, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.revealBox1)
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
        self.verticalLayout_2.addWidget(self.revealBox2)
        self.horizontalLayout.addWidget(self.revealBox0)
        self.pageFrame = QtWidgets.QFrame(annotator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pageFrame.sizePolicy().hasHeightForWidth())
        self.pageFrame.setSizePolicy(sizePolicy)
        self.pageFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.pageFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pageFrame.setObjectName("pageFrame")
        self.pageFrameGrid = QtWidgets.QGridLayout(self.pageFrame)
        self.pageFrameGrid.setContentsMargins(0, 0, 0, 0)
        self.pageFrameGrid.setObjectName("pageFrameGrid")
        self.horizontalLayout.addWidget(self.pageFrame)

        self.retranslateUi(annotator)
        QtCore.QMetaObject.connectSlotsByName(annotator)

    def retranslateUi(self, annotator):
        _translate = QtCore.QCoreApplication.translate
        annotator.setWindowTitle(_translate("annotator", "Annotate paper"))
        self.markLabel.setText(_translate("annotator", "kk out of nn"))
        self.finishedButton.setToolTip(_translate("annotator", "Save and move to the next paper"))
        self.finishedButton.setText(_translate("annotator", "Next"))
        self.helpButton.setToolTip(_translate("annotator", "<html><head/><body><p>Help with keyboard shortcuts</p></body></html>"))
        self.helpButton.setText(_translate("annotator", "Key help"))
        self.zoomButton.setToolTip(_translate("annotator", "press a"))
        self.zoomButton.setText(_translate("annotator", "..."))
        self.panButton.setToolTip(_translate("annotator", "press q"))
        self.panButton.setText(_translate("annotator", "..."))
        self.rearrangePagesButton.setToolTip(_translate("annotator", "<html><head/><body><p>Find a missing page, discard irrelevant pages, rotate pages, etc</p></body></html>"))
        self.rearrangePagesButton.setText(_translate("annotator", "Adjust pages"))
        self.deleteButton.setToolTip(_translate("annotator", "press x"))
        self.deleteButton.setText(_translate("annotator", "..."))
        self.undoButton.setToolTip(_translate("annotator", "press s"))
        self.undoButton.setText(_translate("annotator", "..."))
        self.redoButton.setToolTip(_translate("annotator", "press w"))
        self.redoButton.setText(_translate("annotator", "..."))
        self.moveButton.setToolTip(_translate("annotator", "press z"))
        self.moveButton.setText(_translate("annotator", "..."))
        self.wideModeLabel.setText(_translate("annotator", "mode"))
        self.boxButton.setToolTip(_translate("annotator", "press c"))
        self.boxButton.setText(_translate("annotator", "..."))
        self.tickButton.setToolTip(_translate("annotator", "press d"))
        self.tickButton.setText(_translate("annotator", "..."))
        self.crossButton.setToolTip(_translate("annotator", "press e"))
        self.crossButton.setText(_translate("annotator", "..."))
        self.textButton.setToolTip(_translate("annotator", "press g"))
        self.textButton.setText(_translate("annotator", "..."))
        self.lineButton.setToolTip(_translate("annotator", "press b"))
        self.lineButton.setText(_translate("annotator", "..."))
        self.penButton.setToolTip(_translate("annotator", "press t"))
        self.penButton.setText(_translate("annotator", "..."))
        self.noAnswerButton.setText(_translate("annotator", "No answer"))
        self.narrowMarkLabel.setText(_translate("annotator", "kk out of nn"))
        self.narrowModeLabel.setText(_translate("annotator", "mode"))
        self.wideButton.setText(_translate("annotator", "wide"))
