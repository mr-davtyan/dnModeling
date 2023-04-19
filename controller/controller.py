import datetime
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDesktopWidget

from model.model import Phase
from view.view import Gui
from .worker import PhaseUpdate, StatusUpdate


class Controller:

    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._model = Phase()
        self._view = Gui()
        self._view.p = self._model

        self.worker_phase_update = PhaseUpdate()  # no parent!
        self.thread_phase_update = QThread()  # no parent!
        self.worker_phase_update.set_p(self._model)

        self.worker_status_update = StatusUpdate()  # no parent!
        self.thread_status_update = QThread()  # no parent!

        self.expected_time = 0.1
        self.time_started = datetime.datetime.now()

        self.status_done = True
        self.status_interrupted = False
        self.progress = 0

        self.init()

    def run(self):
        self._view.show()
        # moving window to the center of the screen
        rc = self._view.frameGeometry()
        rc.moveCenter(QDesktopWidget().availableGeometry().center())
        self._view.move(rc.topLeft())
        return self._app.exec_()

    def init(self):
        # connecting Signals
        self._view.signal_update_apodization.connect(self.update_apodization)
        self._view.signal_calculate_phase.connect(self.update_phase)
        self._view.signal_stop_calculate_phase.connect(self.stop_update_phase)
        self._view.signal_exit.connect(self.exit)

        # creating a new thread for background phase update (multiprocessing)
        self.worker_phase_update.moveToThread(self.thread_phase_update)
        self.worker_phase_update.finished.connect(self.thread_phase_update.quit)
        self.thread_phase_update.started.connect(self.worker_phase_update.proc_counter)
        self.thread_phase_update.finished.connect(self.refresh_phase_plots)

        # creating and starting a new thread for background status update
        self.worker_status_update.intReady.connect(self.status_update)
        self.worker_status_update.moveToThread(self.thread_status_update)
        self.thread_status_update.started.connect(self.worker_status_update.proc_counter)
        self.thread_status_update.start()

        # initial apodization update
        self.update_apodization()

    # work progress status update
    def status_update(self):
        if not self.status_done:
            self.progress = min(int((datetime.datetime.now() - self.time_started).seconds / self.expected_time * 100),
                                100)
            self._view.set_progress(self.progress)
            elapsed_time = (datetime.datetime.now() - self.time_started).seconds
            remaining_time = max(int(self.expected_time - elapsed_time), 0)
            self._view.set_expected_time(str(int(self.expected_time)).__add__(" sec / ").__add__(str(remaining_time)))

    # updating apodization per user request
    def update_apodization(self):
        print("Updating Apodization model")
        self._model.a.numberOfPoints = int(self._view.indicator_length.value() * 2000)
        self._model.a.length = self._view.indicator_length.value()
        self._model.a.resolution = self._view.indicator_resolution.value()
        self._model.a.dN = self._view.indicator_dn.value()
        self._model.a.lambdaFBG = self._view.indicator_central_wl.value()
        self._model.a.lambdaFBGStop = self._view.indicator_central_wl.value() + (
                self._view.indicator_length_wl.value() / 2)
        self._model.a.lambdaFBGStart = self._view.indicator_central_wl.value() - (
                self._view.indicator_length_wl.value() / 2)
        self._model.a.alpha = self._view.indicator_apod_alfa.value()
        self._model.a.l_ap = self._view.indicator_apod_l_ap.value()
        self._model.a.redFirst = self._view.indicator_blue_first.currentIndex()
        self._model.a.n0 = self._view.indicator_n0.value()
        self._model.fit_percent = self._view.indicator_fit_range.value()
        self._model.cpus = int(self._view.indicator_cpus.value())

        self._model.a.apodization_update()

        self._view.refresh_plots()

        # performing benchmark based on current computer performance
        print("Updating Phase model")
        self.status_done = True
        a = datetime.datetime.now()
        for i in range(4):  # benchmark
            _ = self._model.get_single_phase(self._model.a.lambdaFBG + i / 10, self._model.a.nz_array, 1, 0, False)[1]
        b = datetime.datetime.now()

        k: float = self._model.a.resolution_points / 4.0 / self._model.cpus
        self.expected_time = (((b - a).seconds * 1000) + (
                (b - a).microseconds / 1000)) * k / 1000

        print("Expected time - ", str(int(self.expected_time)), " seconds")

        self._view.refresh_apodization()
        self._view.set_expected_time(str(int(self.expected_time)).__add__(" sec / 0"))
        self._view.set_progress(100 if self._model.last_calculated_nz_50 == self._model.a.nz_array[50] else 0)

    # starting the background thread to update phases
    def update_phase(self):
        print("Starting Calculation")
        self.status_interrupted = False
        self.status_done = False
        self.time_started = datetime.datetime.now()
        self.thread_phase_update.start()

    def stop_update_phase(self):
        print("Updating Phase model")
        self.status_interrupted = True
        self._model.stop = True

    def refresh_phase_plots(self):
        print("Done. Refreshing Phase Plots")
        self.status_done = True
        if not self.status_interrupted:
            self._view.set_progress(100)
            self._view.set_expected_time(str(int(self.expected_time)).__add__(" sec / 0"))
            self._model.last_calculated_nz_50 = self._model.a.nz_array[50]
        self._view.refresh_phase()
        self._view.refresh_apodization()

    def exit(self):
        self._app.exit()
