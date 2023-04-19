import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from model.model import Phase


class PhaseUpdate(QObject):
    finished = pyqtSignal()
    p = Phase()

    def set_p(self, phase):
        self.p = phase

    @pyqtSlot()
    def proc_counter(self):  # A slot takes no params
        self.p.update_phase()
        # noinspection PyUnresolvedReferences
        self.finished.emit()


class StatusUpdate(QObject):
    intReady = pyqtSignal()

    @pyqtSlot()
    def proc_counter(self):  # A slot takes no params
        while True:
            time.sleep(0.2)
            # noinspection PyUnresolvedReferences
            self.intReady.emit()
        pass
