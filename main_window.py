import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget

from face_points import start_recognition
from main_ui import Ui_main_window
from speech_to_text import robot


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.button_start.clicked.connect(self.start)

    def start(self):
        start_recognition(self)

    def speech(self):
        user_input = robot.run()
        print("user_input:")
        print(user_input)


def open_main_window():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    cp = QDesktopWidget().availableGeometry().bottomRight()
    qr = w.frameGeometry()
    qr.moveBottomRight(cp)
    w.move(qr.topLeft())
    w.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
