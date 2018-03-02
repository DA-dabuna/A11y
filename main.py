import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget

from face_recognition import start_recognition
from main_ui import Ui_main_window
from speech_to_text import robot


def setup_hook():
    _excepthook = sys.excepthook

    def hook(exctype, value, traceback):
        print(exctype, value, traceback)
        _excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = hook


def open_main_window():
    setup_hook()
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


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.button_start.clicked.connect(self.start)

    def start(self):
        start_recognition(self)

    def speech(self):
        # speech
        user_input = robot.start()
        print("user_input:")
        print(user_input)


if __name__ == '__main__':
    open_main_window()
