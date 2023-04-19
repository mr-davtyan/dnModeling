import os

import matplotlib.pyplot as plt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGridLayout, QHBoxLayout, \
    QDoubleSpinBox, QLabel, QComboBox, QProgressBar, QStyleFactory, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from model.model import Phase

spacing_px = 20


def plot_layout_custom(toolbar, canvas):
    toolbar_custom = QHBoxLayout()
    toolbar_custom.addSpacing(spacing_px)
    toolbar_custom.addWidget(toolbar)
    layout_custom = QVBoxLayout()
    layout_custom.addLayout(toolbar_custom)
    layout_custom.addWidget(canvas)
    return layout_custom


def figure_config(q_widget):
    figure_t = plt.figure(facecolor=q_widget.palette().color(QPalette.Background).name())
    figure_t.subplots_adjust(top=0.9,
                             bottom=0.09,
                             left=0.12,
                             right=0.99,
                             hspace=0.2,
                             wspace=0.2)
    return figure_t


def q_double_spin_box_config(value, range_min=0, range_max=9999, decimals=3, maximum=9999, step=1.0):
    indicator = QDoubleSpinBox()
    indicator.setRange(range_min, range_max)
    indicator.setDecimals(decimals)
    indicator.setMaximum(maximum)
    indicator.setSingleStep(step)
    indicator.setValue(value)
    return indicator


class Gui(QWidget):
    signal_update_apodization = pyqtSignal()
    signal_calculate_phase = pyqtSignal()
    signal_stop_calculate_phase = pyqtSignal()
    signal_exit = pyqtSignal()

    def __init__(self):
        super(Gui, self).__init__()

        # window title
        self.setWindowTitle("dnModeling")
        # window icon
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icon.ico')))

        self.p = Phase()
        self.a = self.p.get_apodization()

        self.layout_main = QVBoxLayout(self)
        print(QStyleFactory.keys())

        # buttons
        self.auto_update_checkbox = QCheckBox("Auto Update Apodization")
        self.button_update_apodization = QPushButton('Update Apodization')
        self.button_start = QPushButton('Calculate')
        self.button_stop = QPushButton('Stop')
        self.button_stop.setVisible(False)
        self.button_exit = QPushButton('Exit')

        # Apodization Plot
        self.figure_apodization_plot = figure_config(self)
        self.canvas_apodization_plot = FigureCanvas(self.figure_apodization_plot)
        self.toolbar_apodization_plot = NavigationToolbar(self.canvas_apodization_plot, None)
        self.layout_apodization_plot = plot_layout_custom(self.toolbar_apodization_plot,
                                                          self.canvas_apodization_plot)

        # Reflection Plot
        self.figure_reflection_plot = figure_config(self)
        self.canvas_reflection_plot = FigureCanvas(self.figure_reflection_plot)
        self.toolbar_reflection_plot = NavigationToolbar(self.canvas_reflection_plot, None)
        self.layout_reflection_plot = plot_layout_custom(self.toolbar_reflection_plot,
                                                         self.canvas_reflection_plot)

        # Phase Plot
        self.figure_phase_plot = figure_config(self)
        self.canvas_phase_plot = FigureCanvas(self.figure_phase_plot)
        self.toolbar_phase_plot = NavigationToolbar(self.canvas_phase_plot, None)
        self.layout_phase_plot = plot_layout_custom(self.toolbar_phase_plot,
                                                    self.canvas_phase_plot)

        # GD Plot
        self.figure_gd_plot = figure_config(self)
        self.canvas_gd_plot = FigureCanvas(self.figure_gd_plot)
        self.toolbar_gd_plot = NavigationToolbar(self.canvas_gd_plot, None)
        self.layout_gd_plot = plot_layout_custom(self.toolbar_gd_plot,
                                                 self.canvas_gd_plot)

        # All Plots layout
        self.layout_plots = QGridLayout(self)
        self.layout_plots.addLayout(self.layout_apodization_plot, 1, 0)
        self.layout_plots.addLayout(self.layout_reflection_plot, 1, 1)
        self.layout_plots.addLayout(self.layout_phase_plot, 2, 0)
        self.layout_plots.addLayout(self.layout_gd_plot, 2, 1)

        # Indicators
        self.layout_parameters1 = QHBoxLayout(self)
        self.layout_parameters2 = QHBoxLayout(self)

        self.indicator_time = QLabel("")
        self.indicator_time.setMinimumWidth(160)
        self.layout_parameters1.addWidget(self.indicator_time)
        self.layout_parameters1.addSpacing(spacing_px)

        self.layout_parameters1.addStretch()

        self.indicator_length = q_double_spin_box_config(decimals=2, value=self.a.length)
        self.layout_parameters1.addWidget(QLabel("Grating Length(mm)"))
        self.layout_parameters1.addWidget(self.indicator_length)
        self.layout_parameters1.addSpacing(spacing_px)

        self.indicator_central_wl = q_double_spin_box_config(value=self.a.lambdaFBG)
        self.layout_parameters1.addWidget(QLabel("Central WL(nm)"))
        self.layout_parameters1.addWidget(self.indicator_central_wl)
        self.layout_parameters1.addSpacing(spacing_px)

        self.indicator_length_wl = q_double_spin_box_config(value=abs(self.a.lambdaFBGStop - self.a.lambdaFBGStart))
        self.layout_parameters1.addWidget(QLabel("Grating Length(nm)"))
        self.layout_parameters1.addWidget(self.indicator_length_wl)
        self.layout_parameters1.addSpacing(spacing_px)

        self.indicator_apod_alfa = q_double_spin_box_config(value=self.a.alpha, step=0.1)
        self.layout_parameters1.addWidget(QLabel("Apodization A"))
        self.layout_parameters1.addWidget(self.indicator_apod_alfa)
        self.layout_parameters1.addSpacing(spacing_px)

        self.indicator_apod_l_ap = q_double_spin_box_config(value=self.a.l_ap, step=0.1)
        self.layout_parameters1.addWidget(QLabel("Apodization LAP"))
        self.layout_parameters1.addWidget(self.indicator_apod_l_ap)
        self.layout_parameters1.addSpacing(spacing_px)

        self.layout_parameters1.addStretch()

        self.indicator_chirp = QLabel("CHIRP: " "XX.XX" + " ps/nm")
        self.indicator_chirp.setMinimumWidth(160)
        self.layout_parameters2.addWidget(self.indicator_chirp)
        self.layout_parameters2.addSpacing(spacing_px)

        self.layout_parameters2.addStretch()

        self.indicator_dn = q_double_spin_box_config(value=self.a.dN, step=0.001, range_max=99, decimals=6)
        self.layout_parameters2.addWidget(QLabel("Δn"))
        self.layout_parameters2.addWidget(self.indicator_dn)

        self.indicator_dn_power = QLabel("XX" + " %")
        self.layout_parameters2.addWidget(self.indicator_dn_power)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_show_phase_error = QComboBox()
        self.indicator_show_phase_error.addItems(["Full Phase and GD", "Phase and GD Errors"])
        self.layout_parameters2.addWidget(self.indicator_show_phase_error)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_blue_first = QComboBox()
        self.indicator_blue_first.addItems(["Red First", "Blue First"])
        self.indicator_blue_first.setCurrentIndex(self.a.redFirst)
        self.layout_parameters2.addWidget(self.indicator_blue_first)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_resolution = q_double_spin_box_config(value=self.a.resolution,
                                                             step=0.001, range_max=99, decimals=5)
        self.layout_parameters2.addWidget(QLabel("Resolution(nm)"))
        self.layout_parameters2.addWidget(self.indicator_resolution)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_fit_range = q_double_spin_box_config(value=self.p.fit_percent,
                                                            step=0.001, decimals=1, maximum=99)
        self.layout_parameters2.addWidget(QLabel("Fit Range (%)"))
        self.layout_parameters2.addWidget(self.indicator_fit_range)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_n0 = q_double_spin_box_config(value=self.p.a.n0, step=0.001, range_max=99, decimals=6)
        self.layout_parameters2.addWidget(QLabel("Δn0"))
        self.layout_parameters2.addWidget(self.indicator_n0)
        self.layout_parameters2.addSpacing(spacing_px)

        self.indicator_cpus = q_double_spin_box_config(value=self.p.cpus, range_max=16, decimals=0)
        self.layout_parameters2.addWidget(QLabel("CPUs #"))
        self.layout_parameters2.addWidget(self.indicator_cpus)
        self.layout_parameters2.addSpacing(spacing_px)

        self.layout_parameters2.addStretch()

        # buttons layout
        self.layout_buttons = QHBoxLayout(self)
        self.layout_buttons.addWidget(self.auto_update_checkbox)
        self.layout_buttons.setStretchFactor(self.auto_update_checkbox, 0)
        buttons_array = (self.button_update_apodization, self.button_start, self.button_stop, self.button_exit)
        for button in buttons_array:
            self.layout_buttons.addWidget(button)
            self.layout_buttons.setStretchFactor(button, 1)
        self.layout_buttons.setSpacing(spacing_px)

        # progressbar layout
        self.layout_progressbar = QHBoxLayout(self)
        self.progressbar_bar = QProgressBar(self)
        self.progressbar_bar.setTextVisible(False)
        self.progressbar_bar.setMaximumHeight(8)
        self.progressbar_bar.setStyleSheet("QProgressBar::chunk ""{""background-color: #1f77b4;""border : 1px""}")
        self.layout_progressbar.addWidget(self.progressbar_bar)

        # Main layout
        self.layout_main.addLayout(self.layout_plots)
        self.layout_main.addLayout(self.layout_progressbar)
        self.layout_main.addLayout(self.layout_parameters1)
        self.layout_main.addLayout(self.layout_parameters2)
        self.layout_main.addLayout(self.layout_buttons)
        self.layout_main.addStretch()

        self.auto_update_checkbox.clicked.connect(self.checkbox_auto_update_clicked)
        self.button_update_apodization.clicked.connect(self.signal_update_apodization)
        self.button_start.clicked.connect(self.start_calculation)
        self.button_stop.clicked.connect(self.stop_calculation)
        self.button_exit.clicked.connect(self.signal_exit)
        self.indicator_show_phase_error.currentIndexChanged.connect(self.refresh_phase)

        self.enable_indicators()

    # connecting-disconnecting Signals to the indicators
    def connect_parameters(self, connect=True):
        for it in range(self.layout_parameters1.count()):
            if self.layout_parameters1.itemAt(it).widget().__class__.__name__.__eq__("QDoubleSpinBox"):
                if connect:
                    self.layout_parameters1.itemAt(it).widget().valueChanged.connect(self.signal_update_apodization)
                else:
                    self.layout_parameters1.itemAt(it).widget().valueChanged.disconnect()
        for it in range(self.layout_parameters2.count()):
            if self.layout_parameters2.itemAt(it).widget().__class__.__name__.__eq__("QDoubleSpinBox"):
                if connect:
                    self.layout_parameters2.itemAt(it).widget().valueChanged.connect(self.signal_update_apodization)
                else:
                    self.layout_parameters2.itemAt(it).widget().valueChanged.disconnect()
        if connect:
            self.indicator_blue_first.currentIndexChanged.connect(self.signal_update_apodization)
        else:
            self.indicator_blue_first.currentIndexChanged.disconnect()

    def refresh_apodization(self):
        power = self.p.get_single_phase(self.p.a.lambdaFBG, self.p.a.nz_array, 1, 0, False)[
                    1] * 100  # checking dN level
        if 0 < power < 100:
            self.figure_apodization_plot.clear()
            self.a = self.p.get_apodization()
            ax = self.figure_apodization_plot.add_subplot(111)
            ax.set_ylabel("Reflectivity")
            ax.set_title("Apodization Profile")
            ax.autoscale(enable=False, axis="y", tight=False)
            reflection = [it * power / 100 for it in self.a.apodization_array]
            color = "#1f77b4"
            if not self.p.last_calculated_nz_50 == self.p.a.nz_array[50]:
                color = "#9467bd"
            ax.plot(self.a.wl_array, reflection, color=color)
            self.canvas_apodization_plot.draw()
            self.indicator_dn_power.setText(str(int(power)) + " %")
            print("Apodization Plot Updated")
        else:
            self.indicator_dn_power.setText("NaN" + " %")
            print("dN is out of range")

    def set_progress(self, progress):
        self.progressbar_bar.setValue(progress)

    def set_expected_time(self, expected_time):
        self.indicator_time.setText(expected_time)

    def checkbox_auto_update_clicked(self):
        # noinspection PyUnresolvedReferences
        self.signal_update_apodization.emit()
        if self.auto_update_checkbox.isChecked():
            self.button_update_apodization.setEnabled(False)
            self.connect_parameters(connect=True)
        else:
            self.button_update_apodization.setEnabled(True)
            self.connect_parameters(connect=False)

    def start_calculation(self):
        # noinspection PyUnresolvedReferences
        self.signal_calculate_phase.emit()
        self.button_start.setVisible(False)
        self.button_stop.setVisible(True)
        if not self.auto_update_checkbox.isChecked():
            self.button_update_apodization.setEnabled(False)
        self.button_update_apodization.setText('Calculation is in progress')
        self.auto_update_checkbox.setEnabled(False)
        self.enable_indicators(False)

    def stop_calculation(self):
        # noinspection PyUnresolvedReferences
        self.signal_stop_calculate_phase.emit()
        self.button_stop.setVisible(False)
        self.button_start.setVisible(True)
        self.button_start.setEnabled(False)
        self.button_start.setText('Stopping the calculation process')

    def enable_indicators(self, enable=True):
        for it in range(self.layout_parameters1.count()):
            if not self.layout_parameters1.itemAt(it).widget().__class__.__name__.__eq__("NoneType"):
                self.layout_parameters1.itemAt(it).widget().setEnabled(enable)
        for it in range(self.layout_parameters2.count()):
            if not self.layout_parameters2.itemAt(it).widget().__class__.__name__.__eq__("NoneType"):
                self.layout_parameters2.itemAt(it).widget().setEnabled(enable)
        if len(self.p.phase_unwrap) == 0:
            self.indicator_show_phase_error.setEnabled(False)

    def refresh_phase(self):
        self.button_start.setVisible(True)
        self.button_start.setEnabled(True)
        self.button_start.setText('Calculate')
        self.button_stop.setVisible(False)
        if not self.auto_update_checkbox.isChecked():
            self.button_update_apodization.setEnabled(True)
        self.button_update_apodization.setText('Update Apodization')
        self.auto_update_checkbox.setEnabled(True)
        self.enable_indicators(True)

        if len(self.p.wl) == 0:
            return

        self.indicator_chirp.setText("CHIRP: " + str(round(self.p.chirp, 2)) + " ps/nm")
        self.refresh_plots()

    def refresh_plots(self):
        self.figure_reflection_plot.clear()
        ax = self.figure_reflection_plot.add_subplot(111)
        ax.set_ylabel("Power")
        ax.set_title("Reflectivity")
        ax.plot(self.p.wl, self.p.reflection)
        self.canvas_reflection_plot.draw()
        print("Reflection Plot Updated")

        phase = self.p.phase_unwrap
        gd = self.p.gd
        if self.indicator_show_phase_error.currentIndex() == 1:
            phase = self.p.phase_error
            gd = self.p.gd_error

        self.figure_phase_plot.clear()
        ax = self.figure_phase_plot.add_subplot(111)
        ax.set_ylabel("Radians")
        ax.set_title("Phase")
        ax.plot(self.p.wl, phase)
        self.canvas_phase_plot.draw()
        print("Phase Plot Updated")

        self.figure_gd_plot.clear()
        ax = self.figure_gd_plot.add_subplot(111)
        ax.set_ylabel("Time (ps)")
        ax.set_title("Group Delay")
        ax.plot(self.p.wl, gd)
        self.canvas_gd_plot.draw()
        print("GD Plot Updated")
