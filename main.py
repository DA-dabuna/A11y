import sys

from login_window import open_login_window


def setup_hook():
    _excepthook = sys.excepthook

    def hook(exctype, value, traceback):
        print(exctype, value, traceback)
        _excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = hook


if __name__ == '__main__':
    setup_hook()
    open_login_window()
