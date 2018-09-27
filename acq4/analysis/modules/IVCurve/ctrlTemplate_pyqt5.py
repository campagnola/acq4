# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'acq4/analysis/modules/IVCurve/ctrlTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(318, 505)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setObjectName("frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_3.setHorizontalSpacing(10)
        self.gridLayout_3.setVerticalSpacing(1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_8 = QtWidgets.QLabel(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 15, 3, 1, 1)
        self.IVCurve_SpikeThreshold = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_SpikeThreshold.setFont(font)
        self.IVCurve_SpikeThreshold.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_SpikeThreshold.setDecimals(1)
        self.IVCurve_SpikeThreshold.setMinimum(-100.0)
        self.IVCurve_SpikeThreshold.setObjectName("IVCurve_SpikeThreshold")
        self.gridLayout_3.addWidget(self.IVCurve_SpikeThreshold, 10, 1, 1, 2)
        self.IVCurve_tau2TStart = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_tau2TStart.setFont(font)
        self.IVCurve_tau2TStart.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_tau2TStart.setDecimals(2)
        self.IVCurve_tau2TStart.setMaximum(5000.0)
        self.IVCurve_tau2TStart.setObjectName("IVCurve_tau2TStart")
        self.gridLayout_3.addWidget(self.IVCurve_tau2TStart, 9, 1, 1, 2)
        self.IVCurve_rmpTStart = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_rmpTStart.setFont(font)
        self.IVCurve_rmpTStart.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_rmpTStart.setDecimals(2)
        self.IVCurve_rmpTStart.setMaximum(10000.0)
        self.IVCurve_rmpTStart.setObjectName("IVCurve_rmpTStart")
        self.gridLayout_3.addWidget(self.IVCurve_rmpTStart, 3, 1, 1, 2)
        self.IVCurve_ssTStop = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_ssTStop.setFont(font)
        self.IVCurve_ssTStop.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_ssTStop.setMinimum(-5000.0)
        self.IVCurve_ssTStop.setMaximum(50000.0)
        self.IVCurve_ssTStop.setObjectName("IVCurve_ssTStop")
        self.gridLayout_3.addWidget(self.IVCurve_ssTStop, 5, 1, 1, 2)
        self.IVCurve_vrmp = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_vrmp.setObjectName("IVCurve_vrmp")
        self.gridLayout_3.addWidget(self.IVCurve_vrmp, 15, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 14, 0, 1, 1)
        self.IVCurve_pkTStart = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_pkTStart.setFont(font)
        self.IVCurve_pkTStart.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_pkTStart.setMinimum(-5000.0)
        self.IVCurve_pkTStart.setMaximum(50000.0)
        self.IVCurve_pkTStart.setObjectName("IVCurve_pkTStart")
        self.gridLayout_3.addWidget(self.IVCurve_pkTStart, 7, 1, 1, 2)
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 15, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.frame)
        self.label_15.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 16, 3, 1, 1)
        self.IVCurve_Update = QtWidgets.QPushButton(self.frame)
        self.IVCurve_Update.setObjectName("IVCurve_Update")
        self.gridLayout_3.addWidget(self.IVCurve_Update, 14, 2, 1, 1)
        self.IVCurve_showHide_lrrmp = QtWidgets.QCheckBox(self.frame)
        font = Qt.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IVCurve_showHide_lrrmp.setFont(font)
        self.IVCurve_showHide_lrrmp.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_showHide_lrrmp.setChecked(True)
        self.IVCurve_showHide_lrrmp.setObjectName("IVCurve_showHide_lrrmp")
        self.gridLayout_3.addWidget(self.IVCurve_showHide_lrrmp, 3, 0, 1, 1)
        self.IVCurve_PrintResults = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVCurve_PrintResults.sizePolicy().hasHeightForWidth())
        self.IVCurve_PrintResults.setSizePolicy(sizePolicy)
        self.IVCurve_PrintResults.setObjectName("IVCurve_PrintResults")
        self.gridLayout_3.addWidget(self.IVCurve_PrintResults, 14, 5, 1, 1)
        self.IVCurve_tauh_Commands = QtWidgets.QComboBox(self.frame)
        self.IVCurve_tauh_Commands.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_tauh_Commands.setObjectName("IVCurve_tauh_Commands")
        self.IVCurve_tauh_Commands.addItem("")
        self.gridLayout_3.addWidget(self.IVCurve_tauh_Commands, 10, 4, 1, 2)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setAlignment(Qt.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 2, 2, 1, 1)
        self.IVCurve_pkAmp = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_pkAmp.setObjectName("IVCurve_pkAmp")
        self.gridLayout_3.addWidget(self.IVCurve_pkAmp, 20, 2, 1, 1)
        self.IVCurve_showHide_lrss = QtWidgets.QCheckBox(self.frame)
        font = Qt.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IVCurve_showHide_lrss.setFont(font)
        self.IVCurve_showHide_lrss.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_showHide_lrss.setChecked(True)
        self.IVCurve_showHide_lrss.setObjectName("IVCurve_showHide_lrss")
        self.gridLayout_3.addWidget(self.IVCurve_showHide_lrss, 5, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 10, 0, 1, 1)
        self.IVCurve_showHide_lrpk = QtWidgets.QCheckBox(self.frame)
        font = Qt.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IVCurve_showHide_lrpk.setFont(font)
        self.IVCurve_showHide_lrpk.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_showHide_lrpk.setChecked(True)
        self.IVCurve_showHide_lrpk.setObjectName("IVCurve_showHide_lrpk")
        self.gridLayout_3.addWidget(self.IVCurve_showHide_lrpk, 7, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 16, 0, 1, 1)
        self.IVCurve_Rin = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_Rin.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_Rin.setObjectName("IVCurve_Rin")
        self.gridLayout_3.addWidget(self.IVCurve_Rin, 16, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.frame)
        self.label_11.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 19, 0, 1, 1)
        self.IVCurve_Tau = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_Tau.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_Tau.setObjectName("IVCurve_Tau")
        self.gridLayout_3.addWidget(self.IVCurve_Tau, 18, 2, 1, 1)
        self.IVCurve_FOType = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_FOType.setObjectName("IVCurve_FOType")
        self.gridLayout_3.addWidget(self.IVCurve_FOType, 19, 5, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.frame)
        self.label_19.setObjectName("label_19")
        self.gridLayout_3.addWidget(self.label_19, 1, 3, 1, 1)
        self.IVCurve_showHide_lrtau = QtWidgets.QCheckBox(self.frame)
        font = Qt.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IVCurve_showHide_lrtau.setFont(font)
        self.IVCurve_showHide_lrtau.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_showHide_lrtau.setAutoFillBackground(False)
        self.IVCurve_showHide_lrtau.setObjectName("IVCurve_showHide_lrtau")
        self.gridLayout_3.addWidget(self.IVCurve_showHide_lrtau, 9, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_3.addWidget(self.line, 12, 0, 1, 6)
        self.IVCurve_IVLimits = QtWidgets.QCheckBox(self.frame)
        self.IVCurve_IVLimits.setLayoutDirection(Qt.Qt.LeftToRight)
        self.IVCurve_IVLimits.setObjectName("IVCurve_IVLimits")
        self.gridLayout_3.addWidget(self.IVCurve_IVLimits, 0, 2, 1, 1)
        self.dbStoreBtn = QtWidgets.QPushButton(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.dbStoreBtn.setFont(font)
        self.dbStoreBtn.setObjectName("dbStoreBtn")
        self.gridLayout_3.addWidget(self.dbStoreBtn, 14, 3, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame)
        self.label_9.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 18, 0, 1, 1)
        self.IVCurve_Ih_ba = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_Ih_ba.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_Ih_ba.setObjectName("IVCurve_Ih_ba")
        self.gridLayout_3.addWidget(self.IVCurve_Ih_ba, 18, 5, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.frame)
        self.label_17.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_17.setObjectName("label_17")
        self.gridLayout_3.addWidget(self.label_17, 20, 0, 1, 1)
        self.IVCurve_Tauh = QtWidgets.QLineEdit(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_Tauh.setFont(font)
        self.IVCurve_Tauh.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_Tauh.setObjectName("IVCurve_Tauh")
        self.gridLayout_3.addWidget(self.IVCurve_Tauh, 16, 5, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame)
        self.label_12.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 20, 3, 1, 1)
        self.IVCurve_ssAmp = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_ssAmp.setObjectName("IVCurve_ssAmp")
        self.gridLayout_3.addWidget(self.IVCurve_ssAmp, 20, 5, 1, 1)
        self.IVCurve_MPLExport = QtWidgets.QPushButton(self.frame)
        self.IVCurve_MPLExport.setObjectName("IVCurve_MPLExport")
        self.gridLayout_3.addWidget(self.IVCurve_MPLExport, 21, 5, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 18, 3, 1, 1)
        self.IVCurve_Gh = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_Gh.setObjectName("IVCurve_Gh")
        self.gridLayout_3.addWidget(self.IVCurve_Gh, 15, 5, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 19, 3, 1, 1)
        self.IVCurve_subLeak = QtWidgets.QCheckBox(self.frame)
        font = Qt.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IVCurve_subLeak.setFont(font)
        self.IVCurve_subLeak.setLayoutDirection(Qt.Qt.RightToLeft)
        self.IVCurve_subLeak.setObjectName("IVCurve_subLeak")
        self.gridLayout_3.addWidget(self.IVCurve_subLeak, 4, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 21, 3, 1, 1)
        self.IVCurve_LeakMin = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_LeakMin.setFont(font)
        self.IVCurve_LeakMin.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_LeakMin.setDecimals(1)
        self.IVCurve_LeakMin.setMinimum(-200.0)
        self.IVCurve_LeakMin.setMaximum(200.0)
        self.IVCurve_LeakMin.setProperty("value", -5.0)
        self.IVCurve_LeakMin.setObjectName("IVCurve_LeakMin")
        self.gridLayout_3.addWidget(self.IVCurve_LeakMin, 4, 1, 1, 2)
        self.IVCurve_KeepT = QtWidgets.QCheckBox(self.frame)
        self.IVCurve_KeepT.setLayoutDirection(Qt.Qt.LeftToRight)
        self.IVCurve_KeepT.setObjectName("IVCurve_KeepT")
        self.gridLayout_3.addWidget(self.IVCurve_KeepT, 21, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.frame)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.frame)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 1, 0, 1, 1)
        self.IVCurve_IVLimitMax = QtWidgets.QDoubleSpinBox(self.frame)
        self.IVCurve_IVLimitMax.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_IVLimitMax.setDecimals(1)
        self.IVCurve_IVLimitMax.setMinimum(-2000.0)
        self.IVCurve_IVLimitMax.setMaximum(2000.0)
        self.IVCurve_IVLimitMax.setSingleStep(5.0)
        self.IVCurve_IVLimitMax.setProperty("value", 100.0)
        self.IVCurve_IVLimitMax.setObjectName("IVCurve_IVLimitMax")
        self.gridLayout_3.addWidget(self.IVCurve_IVLimitMax, 0, 5, 1, 1)
        self.IVCurve_IVLimitMin = QtWidgets.QDoubleSpinBox(self.frame)
        self.IVCurve_IVLimitMin.setDecimals(1)
        self.IVCurve_IVLimitMin.setMinimum(-2000.0)
        self.IVCurve_IVLimitMin.setMaximum(2000.0)
        self.IVCurve_IVLimitMin.setSingleStep(5.0)
        self.IVCurve_IVLimitMin.setProperty("value", -160.0)
        self.IVCurve_IVLimitMin.setObjectName("IVCurve_IVLimitMin")
        self.gridLayout_3.addWidget(self.IVCurve_IVLimitMin, 0, 3, 1, 2)
        self.IVCurve_tau2TStop = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_tau2TStop.setFont(font)
        self.IVCurve_tau2TStop.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_tau2TStop.setMaximum(5000.0)
        self.IVCurve_tau2TStop.setObjectName("IVCurve_tau2TStop")
        self.gridLayout_3.addWidget(self.IVCurve_tau2TStop, 9, 3, 1, 1)
        self.IVCurve_pkTStop = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_pkTStop.setFont(font)
        self.IVCurve_pkTStop.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_pkTStop.setMinimum(-5000.0)
        self.IVCurve_pkTStop.setMaximum(50000.0)
        self.IVCurve_pkTStop.setObjectName("IVCurve_pkTStop")
        self.gridLayout_3.addWidget(self.IVCurve_pkTStop, 7, 3, 1, 1)
        self.IVCurve_LeakMax = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_LeakMax.setFont(font)
        self.IVCurve_LeakMax.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_LeakMax.setDecimals(1)
        self.IVCurve_LeakMax.setMinimum(-200.0)
        self.IVCurve_LeakMax.setMaximum(203.0)
        self.IVCurve_LeakMax.setProperty("value", 5.0)
        self.IVCurve_LeakMax.setObjectName("IVCurve_LeakMax")
        self.gridLayout_3.addWidget(self.IVCurve_LeakMax, 4, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setAlignment(Qt.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 3, 1, 1)
        self.IVCurve_ssTStart = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_ssTStart.setFont(font)
        self.IVCurve_ssTStart.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_ssTStart.setMinimum(-5000.0)
        self.IVCurve_ssTStart.setMaximum(50000.0)
        self.IVCurve_ssTStart.setObjectName("IVCurve_ssTStart")
        self.gridLayout_3.addWidget(self.IVCurve_ssTStart, 5, 3, 1, 1)
        self.IVCurve_SubBaseline = QtWidgets.QCheckBox(self.frame)
        self.IVCurve_SubBaseline.setObjectName("IVCurve_SubBaseline")
        self.gridLayout_3.addWidget(self.IVCurve_SubBaseline, 3, 5, 1, 1)
        self.IVCurve_rmpTStop = QtWidgets.QDoubleSpinBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_rmpTStop.setFont(font)
        self.IVCurve_rmpTStop.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_rmpTStop.setMaximum(10000.0)
        self.IVCurve_rmpTStop.setObjectName("IVCurve_rmpTStop")
        self.gridLayout_3.addWidget(self.IVCurve_rmpTStop, 3, 3, 1, 1)
        self.IVCurve_getFileInfo = QtWidgets.QPushButton(self.frame)
        self.IVCurve_getFileInfo.setObjectName("IVCurve_getFileInfo")
        self.gridLayout_3.addWidget(self.IVCurve_getFileInfo, 2, 5, 1, 1)
        self.IVCurve_dataMode = QtWidgets.QLabel(self.frame)
        self.IVCurve_dataMode.setObjectName("IVCurve_dataMode")
        self.gridLayout_3.addWidget(self.IVCurve_dataMode, 2, 0, 1, 1)
        self.IVCurve_KeepAnalysis = QtWidgets.QCheckBox(self.frame)
        self.IVCurve_KeepAnalysis.setLayoutDirection(Qt.Qt.LeftToRight)
        self.IVCurve_KeepAnalysis.setObjectName("IVCurve_KeepAnalysis")
        self.gridLayout_3.addWidget(self.IVCurve_KeepAnalysis, 21, 2, 1, 1)
        self.IVCurve_Sequence2 = QtWidgets.QComboBox(self.frame)
        self.IVCurve_Sequence2.setObjectName("IVCurve_Sequence2")
        self.IVCurve_Sequence2.addItem("")
        self.gridLayout_3.addWidget(self.IVCurve_Sequence2, 1, 5, 1, 1)
        self.IVCurve_Sequence1 = QtWidgets.QComboBox(self.frame)
        self.IVCurve_Sequence1.setObjectName("IVCurve_Sequence1")
        self.IVCurve_Sequence1.addItem("")
        self.IVCurve_Sequence1.addItem("")
        self.IVCurve_Sequence1.addItem("")
        self.IVCurve_Sequence1.addItem("")
        self.IVCurve_Sequence1.addItem("")
        self.gridLayout_3.addWidget(self.IVCurve_Sequence1, 1, 2, 1, 1)
        self.IVCurve_AR = QtWidgets.QLineEdit(self.frame)
        self.IVCurve_AR.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_AR.setObjectName("IVCurve_AR")
        self.gridLayout_3.addWidget(self.IVCurve_AR, 19, 2, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(40)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.IVCurve_OpenScript_Btn = QtWidgets.QPushButton(self.groupBox)
        self.IVCurve_OpenScript_Btn.setGeometry(Qt.QRect(0, 35, 56, 32))
        self.IVCurve_OpenScript_Btn.setObjectName("IVCurve_OpenScript_Btn")
        self.IVCurve_RunScript_Btn = QtWidgets.QPushButton(self.groupBox)
        self.IVCurve_RunScript_Btn.setGeometry(Qt.QRect(55, 35, 51, 32))
        self.IVCurve_RunScript_Btn.setObjectName("IVCurve_RunScript_Btn")
        self.IVCurve_PrintScript_Btn = QtWidgets.QPushButton(self.groupBox)
        self.IVCurve_PrintScript_Btn.setGeometry(Qt.QRect(105, 35, 61, 32))
        self.IVCurve_PrintScript_Btn.setObjectName("IVCurve_PrintScript_Btn")
        self.IVCurve_ScriptName = QtWidgets.QLabel(self.groupBox)
        self.IVCurve_ScriptName.setGeometry(Qt.QRect(160, 40, 136, 21))
        font = Qt.QFont()
        font.setPointSize(11)
        self.IVCurve_ScriptName.setFont(font)
        self.IVCurve_ScriptName.setObjectName("IVCurve_ScriptName")
        self.gridLayout_3.addWidget(self.groupBox, 22, 0, 1, 6)
        self.IVCurve_RMPMode = QtWidgets.QComboBox(self.frame)
        font = Qt.QFont()
        font.setPointSize(12)
        self.IVCurve_RMPMode.setFont(font)
        self.IVCurve_RMPMode.setObjectName("IVCurve_RMPMode")
        self.IVCurve_RMPMode.addItem("")
        self.IVCurve_RMPMode.addItem("")
        self.IVCurve_RMPMode.addItem("")
        self.gridLayout_3.addWidget(self.IVCurve_RMPMode, 4, 5, 1, 1)
        self.IVCurve_PeakMode = QtWidgets.QComboBox(self.frame)
        self.IVCurve_PeakMode.setObjectName("IVCurve_PeakMode")
        self.IVCurve_PeakMode.addItem("")
        self.IVCurve_PeakMode.addItem("")
        self.IVCurve_PeakMode.addItem("")
        self.gridLayout_3.addWidget(self.IVCurve_PeakMode, 5, 5, 1, 1)
        self.IVCurve_FISI_ISI_button = QtWidgets.QPushButton(self.frame)
        self.IVCurve_FISI_ISI_button.setObjectName("IVCurve_FISI_ISI_button")
        self.gridLayout_3.addWidget(self.IVCurve_FISI_ISI_button, 7, 5, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.frame)
        self.label_16.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 9, 5, 1, 1)
        self.IVCurve_bridge = QtWidgets.QDoubleSpinBox(self.frame)
        palette = Qt.QPalette()
        brush = Qt.QBrush(Qt.QColor(0, 0, 0))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Active, Qt.QPalette.WindowText, brush)
        brush = Qt.QBrush(Qt.QColor(255, 0, 0))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Active, Qt.QPalette.Text, brush)
        brush = Qt.QBrush(Qt.QColor(0, 0, 0))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Active, Qt.QPalette.ButtonText, brush)
        brush = Qt.QBrush(Qt.QColor(0, 0, 0))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Inactive, Qt.QPalette.WindowText, brush)
        brush = Qt.QBrush(Qt.QColor(69, 69, 69))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Inactive, Qt.QPalette.Text, brush)
        brush = Qt.QBrush(Qt.QColor(0, 0, 0))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Inactive, Qt.QPalette.ButtonText, brush)
        brush = Qt.QBrush(Qt.QColor(69, 69, 69))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Disabled, Qt.QPalette.WindowText, brush)
        brush = Qt.QBrush(Qt.QColor(69, 69, 69))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Disabled, Qt.QPalette.Text, brush)
        brush = Qt.QBrush(Qt.QColor(106, 104, 100))
        brush.setStyle(Qt.Qt.SolidPattern)
        palette.setBrush(Qt.QPalette.Disabled, Qt.QPalette.ButtonText, brush)
        self.IVCurve_bridge.setPalette(palette)
        font = Qt.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.IVCurve_bridge.setFont(font)
        self.IVCurve_bridge.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignTrailing|Qt.Qt.AlignVCenter)
        self.IVCurve_bridge.setDecimals(1)
        self.IVCurve_bridge.setMinimum(-50.0)
        self.IVCurve_bridge.setMaximum(200.0)
        self.IVCurve_bridge.setSingleStep(10.0)
        self.IVCurve_bridge.setObjectName("IVCurve_bridge")
        self.gridLayout_3.addWidget(self.IVCurve_bridge, 10, 3, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Form)
        Qt.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = Qt.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_8.setText(_translate("Form", "gH"))
        self.IVCurve_SpikeThreshold.setSuffix(_translate("Form", " mV"))
        self.label_10.setText(_translate("Form", "Results"))
        self.label_7.setText(_translate("Form", "RMP/I<sub>0</sub>"))
        self.label_15.setText(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">&tau;<span style=\" vertical-align:sub;\">h</span> (ms)</p></body></html>"))
        self.IVCurve_Update.setText(_translate("Form", "Update"))
        self.IVCurve_showHide_lrrmp.setText(_translate("Form", "IV:RMP"))
        self.IVCurve_PrintResults.setText(_translate("Form", "Print"))
        self.IVCurve_tauh_Commands.setItemText(0, _translate("Form", "-0.6"))
        self.label.setText(_translate("Form", "T Start"))
        self.IVCurve_showHide_lrss.setText(_translate("Form", "IV:SS"))
        self.label_4.setText(_translate("Form", "Spike Thr"))
        self.IVCurve_showHide_lrpk.setText(_translate("Form", "IV:Peak"))
        self.label_2.setText(_translate("Form", "R<sub>in</sub>"))
        self.label_11.setText(_translate("Form", "Adapt \n"
"Ratio"))
        self.label_19.setText(_translate("Form", "Seq #2"))
        self.IVCurve_showHide_lrtau.setText(_translate("Form", "Ih tool"))
        self.IVCurve_IVLimits.setText(_translate("Form", "Use Limits"))
        self.dbStoreBtn.setText(_translate("Form", "-> db"))
        self.label_9.setText(_translate("Form", "&tau;<sub>m</sub> (ms)"))
        self.label_17.setText(_translate("Form", "Pk Amp"))
        self.label_12.setText(_translate("Form", "SS Amp"))
        self.IVCurve_MPLExport.setText(_translate("Form", "MPL plot"))
        self.label_5.setText(_translate("Form", "b/a (%)"))
        self.label_6.setText(_translate("Form", "F&O Type"))
        self.IVCurve_subLeak.setText(_translate("Form", "IV:Leak"))
        self.pushButton.setText(_translate("Form", "Reset"))
        self.IVCurve_KeepT.setText(_translate("Form", "Keep\n"
"Times"))
        self.label_13.setText(_translate("Form", "IV Cmd"))
        self.label_14.setText(_translate("Form", "Seq #1"))
        self.label_3.setText(_translate("Form", "T Stop"))
        self.IVCurve_SubBaseline.setText(_translate("Form", "Sub Baseline"))
        self.IVCurve_getFileInfo.setText(_translate("Form", "FileInfo"))
        self.IVCurve_dataMode.setText(_translate("Form", "DataMode"))
        self.IVCurve_KeepAnalysis.setText(_translate("Form", "Keep \n"
"Analysis"))
        self.IVCurve_Sequence2.setItemText(0, _translate("Form", "None"))
        self.IVCurve_Sequence1.setItemText(0, _translate("Form", "None"))
        self.IVCurve_Sequence1.setItemText(1, _translate("Form", "001"))
        self.IVCurve_Sequence1.setItemText(2, _translate("Form", "002"))
        self.IVCurve_Sequence1.setItemText(3, _translate("Form", "003"))
        self.IVCurve_Sequence1.setItemText(4, _translate("Form", "004"))
        self.groupBox.setTitle(_translate("Form", "Scripts"))
        self.IVCurve_OpenScript_Btn.setText(_translate("Form", "Open"))
        self.IVCurve_RunScript_Btn.setText(_translate("Form", "Run"))
        self.IVCurve_PrintScript_Btn.setText(_translate("Form", "Print"))
        self.IVCurve_ScriptName.setText(_translate("Form", "TextLabel"))
        self.IVCurve_RMPMode.setItemText(0, _translate("Form", "T (s)"))
        self.IVCurve_RMPMode.setItemText(1, _translate("Form", "I (pA)"))
        self.IVCurve_RMPMode.setItemText(2, _translate("Form", "Sp (#/s)"))
        self.IVCurve_PeakMode.setItemText(0, _translate("Form", "Abs"))
        self.IVCurve_PeakMode.setItemText(1, _translate("Form", "Min"))
        self.IVCurve_PeakMode.setItemText(2, _translate("Form", "Max"))
        self.IVCurve_FISI_ISI_button.setText(_translate("Form", "FISI/ISI"))
        self.label_16.setText(_translate("Form", "Command"))
        self.IVCurve_bridge.setSuffix(_translate("Form", "M"))

