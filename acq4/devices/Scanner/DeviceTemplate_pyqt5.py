# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'acq4/devices/Scanner/DeviceTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(587, 333)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(Qt.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.calibrationList = QtWidgets.QTreeWidget(self.layoutWidget)
        self.calibrationList.setRootIsDecorated(False)
        self.calibrationList.setItemsExpandable(False)
        self.calibrationList.setObjectName("calibrationList")
        self.calibrationList.header().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.calibrationList)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibrateBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.calibrateBtn.setObjectName("calibrateBtn")
        self.horizontalLayout_2.addWidget(self.calibrateBtn)
        self.deleteBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.deleteBtn.setObjectName("deleteBtn")
        self.horizontalLayout_2.addWidget(self.deleteBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.groupBox = QtWidgets.QGroupBox(self.layoutWidget)
        self.groupBox.setAlignment(Qt.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 4, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 5, 2, 1, 1)
        self.yMaxSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.yMaxSpin.setMinimum(-10.0)
        self.yMaxSpin.setMaximum(10.0)
        self.yMaxSpin.setSingleStep(0.1)
        self.yMaxSpin.setProperty("value", 2.0)
        self.yMaxSpin.setObjectName("yMaxSpin")
        self.gridLayout_2.addWidget(self.yMaxSpin, 5, 3, 1, 1)
        self.scanDurationSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.scanDurationSpin.setMinimum(0.01)
        self.scanDurationSpin.setMaximum(100.0)
        self.scanDurationSpin.setProperty("value", 5.0)
        self.scanDurationSpin.setObjectName("scanDurationSpin")
        self.gridLayout_2.addWidget(self.scanDurationSpin, 2, 3, 1, 1)
        self.xMinSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.xMinSpin.setMinimum(-10.0)
        self.xMinSpin.setMaximum(10.0)
        self.xMinSpin.setSingleStep(0.1)
        self.xMinSpin.setProperty("value", -2.0)
        self.xMinSpin.setObjectName("xMinSpin")
        self.gridLayout_2.addWidget(self.xMinSpin, 4, 1, 1, 1)
        self.scanLabel = QtWidgets.QLabel(self.groupBox)
        self.scanLabel.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.scanLabel.setObjectName("scanLabel")
        self.gridLayout_2.addWidget(self.scanLabel, 2, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.cameraCombo = InterfaceCombo(self.groupBox)
        self.cameraCombo.setObjectName("cameraCombo")
        self.gridLayout_2.addWidget(self.cameraCombo, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.laserCombo = InterfaceCombo(self.groupBox)
        self.laserCombo.setObjectName("laserCombo")
        self.gridLayout_2.addWidget(self.laserCombo, 2, 1, 1, 1)
        self.storeCamConfBtn = QtWidgets.QPushButton(self.groupBox)
        self.storeCamConfBtn.setObjectName("storeCamConfBtn")
        self.gridLayout_2.addWidget(self.storeCamConfBtn, 1, 2, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout_2.addItem(spacerItem, 3, 1, 1, 1)
        self.yMinSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.yMinSpin.setMinimum(-10.0)
        self.yMinSpin.setMaximum(10.0)
        self.yMinSpin.setSingleStep(0.1)
        self.yMinSpin.setProperty("value", -2.0)
        self.yMinSpin.setObjectName("yMinSpin")
        self.gridLayout_2.addWidget(self.yMinSpin, 4, 3, 1, 1)
        self.xMaxSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.xMaxSpin.setMinimum(-10.0)
        self.xMaxSpin.setMaximum(10.0)
        self.xMaxSpin.setSingleStep(0.1)
        self.xMaxSpin.setProperty("value", 2.0)
        self.xMaxSpin.setObjectName("xMaxSpin")
        self.gridLayout_2.addWidget(self.xMaxSpin, 5, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.shutterGroup = QtWidgets.QGroupBox(self.layoutWidget)
        self.shutterGroup.setAlignment(Qt.Qt.AlignCenter)
        self.shutterGroup.setObjectName("shutterGroup")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.shutterGroup)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setHorizontalSpacing(5)
        self.gridLayout_4.setVerticalSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.shutterBtn = QtWidgets.QPushButton(self.shutterGroup)
        self.shutterBtn.setObjectName("shutterBtn")
        self.gridLayout_4.addWidget(self.shutterBtn, 0, 5, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.shutterGroup)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.shutterXSpin = QtWidgets.QDoubleSpinBox(self.shutterGroup)
        self.shutterXSpin.setEnabled(False)
        self.shutterXSpin.setDecimals(3)
        self.shutterXSpin.setMinimum(-10.0)
        self.shutterXSpin.setMaximum(10.0)
        self.shutterXSpin.setObjectName("shutterXSpin")
        self.gridLayout_4.addWidget(self.shutterXSpin, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.shutterGroup)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 0, 2, 1, 1)
        self.shutterYSpin = QtWidgets.QDoubleSpinBox(self.shutterGroup)
        self.shutterYSpin.setEnabled(False)
        self.shutterYSpin.setDecimals(3)
        self.shutterYSpin.setMinimum(-10.0)
        self.shutterYSpin.setMaximum(10.0)
        self.shutterYSpin.setObjectName("shutterYSpin")
        self.gridLayout_4.addWidget(self.shutterYSpin, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 4, 1, 1)
        self.verticalLayout.addWidget(self.shutterGroup)
        self.view = ImageView(self.splitter)
        self.view.setObjectName("view")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        Qt.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = Qt.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.calibrationList.headerItem().setText(0, _translate("Form", "Optics"))
        self.calibrationList.headerItem().setText(1, _translate("Form", "Laser"))
        self.calibrationList.headerItem().setText(2, _translate("Form", "Spot"))
        self.calibrationList.headerItem().setText(3, _translate("Form", "Date"))
        self.calibrateBtn.setText(_translate("Form", "Calibrate"))
        self.deleteBtn.setText(_translate("Form", "Delete"))
        self.groupBox.setTitle(_translate("Form", "Calibration Parameters"))
        self.label.setText(_translate("Form", "X min"))
        self.label_4.setText(_translate("Form", "X max"))
        self.label_5.setText(_translate("Form", "Y min"))
        self.label_6.setText(_translate("Form", "Y max"))
        self.yMaxSpin.setSuffix(_translate("Form", " V"))
        self.scanDurationSpin.setSuffix(_translate("Form", " s"))
        self.xMinSpin.setSuffix(_translate("Form", " V"))
        self.scanLabel.setText(_translate("Form", "Scan duration:"))
        self.label_2.setText(_translate("Form", "Camera:"))
        self.label_3.setText(_translate("Form", "Laser:"))
        self.storeCamConfBtn.setToolTip(_translate("Form", "Remember the current camera configuration (including exposure time, ROI, etc) to use whenever calibrating against this camera."))
        self.storeCamConfBtn.setText(_translate("Form", "Store Camera Config"))
        self.yMinSpin.setSuffix(_translate("Form", " V"))
        self.xMaxSpin.setSuffix(_translate("Form", " V"))
        self.shutterGroup.setTitle(_translate("Form", "Virtual Shutter"))
        self.shutterBtn.setText(_translate("Form", "Close Shutter"))
        self.label_7.setText(_translate("Form", "X"))
        self.label_8.setText(_translate("Form", "Y"))

from acq4.pyqtgraph import ImageView
from acq4.util.InterfaceCombo import InterfaceCombo
