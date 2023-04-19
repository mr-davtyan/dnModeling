import multiprocessing
import sys

from controller.controller import Controller


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook

    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    c = Controller()
    sys.exit(c.run())
