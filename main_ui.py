# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(204, 232)
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.left = QtWidgets.QLabel(self.centralwidget)
        self.left.setGeometry(QtCore.QRect(10, 60, 51, 61))
        self.left.setScaledContents(False)
        self.left.setObjectName("left")
        self.down = QtWidgets.QLabel(self.centralwidget)
        self.down.setGeometry(QtCore.QRect(80, 130, 51, 61))
        self.down.setScaledContents(False)
        self.down.setObjectName("down")
        self.up = QtWidgets.QLabel(self.centralwidget)
        self.up.setGeometry(QtCore.QRect(80, 0, 41, 61))
        self.up.setScaledContents(False)
        self.up.setObjectName("up")
        self.right = QtWidgets.QLabel(self.centralwidget)
        self.right.setGeometry(QtCore.QRect(130, 60, 51, 61))
        self.right.setScaledContents(False)
        self.right.setObjectName("right")
        self.button_start = QtWidgets.QPushButton(self.centralwidget)
        self.button_start.setGeometry(QtCore.QRect(0, 0, 41, 23))
        self.button_start.setObjectName("button_start")
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 204, 23))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.left.setText(_translate("main_window", "<html><head/><body><p><span style=\" font-size:24pt;\">←</span></p></body></html>"))
        self.down.setText(_translate("main_window", "<html><head/><body><p><span style=\" font-size:24pt;\">↓</span></p></body></html>"))
        self.up.setText(_translate("main_window", "<html><head/><body><p><span style=\" font-size:24pt;\">↑</span></p></body></html>"))
        self.right.setText(_translate("main_window", "<html><head/><body><p><span style=\" font-size:24pt;\">→</span></p></body></html>"))
        self.button_start.setText(_translate("main_window", "Start"))

