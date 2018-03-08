import os

import psutil
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget

from face_points import start_recognition
from main_ui import Ui_main_window


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.should_exit = False
        self.button_start.clicked.connect(self.start)
        self.button_exit.clicked.connect(self.exit)
        self.timer_camera = QTimer()
        self.timer_camera.start(1000)
        self.timer_camera.timeout.connect(self.start)

    def start(self):
        start_recognition(self)

    def exit(self):
        self.should_exit = True
        p = psutil.Process(os.getpid()).ppid()
        psutil.Process(p).terminate()
        self.close()


def open_main_window():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    # cp = QDesktopWidget().availableGeometry().bottomRight()
    # qr = w.frameGeometry()
    # qr.moveBottomRight(cp)
    # w.move(qr.topLeft())
    sg = QDesktopWidget().availableGeometry()
    fg = w.frameGeometry()
    wg = w.geometry()
    wi = (sg.width() - (fg.width() - wg.width())) / 2
    hi = sg.height() - (fg.height() - wg.height())
    w.move(int(sg.width() / 2), sg.y())
    w.resize(int(wi), int(hi))
    w.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
