import sys
import time

# from login_window import open_login_window
from speech_to_text import robot


def setup_hook():
    _excepthook = sys.excepthook

    def hook(exctype, value, traceback):
        print(exctype, value, traceback)
        _excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = hook


if __name__ == '__main__':
    # setup_hook()
    # open_login_window()
    print("正在开启语音模块")
    robot.start()
    print("语音模块已经开启")

    for _ in range(1,100):
    	time.sleep(1)
    	# print("父进程正在运行")
