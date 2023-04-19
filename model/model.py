import cmath
import datetime
import math
import multiprocessing
from functools import partial

import numpy as np

from .apodization import Apodization

count = multiprocessing.Value('i', 0)


class Phase:
    def __init__(self):
        global count

        self.a = Apodization()
        self.stop = False

        self.wl = []
        self.freq = []

        self.reflection = []

        self.phase_unwrap = []
        self.phase_error = []

        self.gd = []
        self.gd_error = []

        self.chirp = 0.00

        self.fit_percent = 60
        self.cpus: int = min(10, multiprocessing.cpu_count() - 1)

        self.last_calculated_nz_50 = 0

    def update_phase(self, terminal_print=True):

        self.stop = False

        count.value = 0

        lambda_array_sorted = [(self.a.lambdaFBGStart - 1) + (self.a.resolution * it) for it in
                               range(self.a.resolution_points - 1)]

        start = datetime.datetime.now()

        pool = multiprocessing.Pool(processes=self.cpus)
        final_data_array = pool.map(
            partial(self.get_single_phase, nz=self.a.nz_array, cpus=self.cpus,
                    resolution_points=self.a.resolution_points, terminal_print=terminal_print),
            lambda_array_sorted, chunksize=None)

        if self.stop:
            print("Interrupted")
            self.stop = False
            return

        print("Time : " + str((datetime.datetime.now() - start).seconds) + " seconds")

        self.wl = [it[0] for it in final_data_array]
        self.freq = [3 / it * 10 ** 17 for it in self.wl]

        self.reflection = [it[1] for it in final_data_array]

        t_phase = [it[2] for it in final_data_array]
        self.phase_unwrap = np.unwrap(t_phase)

        self.gd = np.gradient(self.phase_unwrap) / np.gradient(
            [2 * math.pi * 3 * 10 ** 8 / it / 10 ** 3 for it in self.wl])

        gd_fix = []
        k = 0
        for i in range(len(self.gd)):
            if i > 1:
                if abs(self.gd[i - 1] - self.gd[i]) > 200:
                    k = k + (self.gd[i - 1] - self.gd[i])
            gd_fix.append(k + self.gd[i])
        self.gd = gd_fix

        self.phase_unwrap = np.cumsum([it * -1 * (self.wl[2] - self.wl[1]) for it in self.gd])

        # taking some percent of the spectrum from the center for fit coefficients
        f = (100 - self.fit_percent) / 2 / 100
        fit_range = int(len(self.freq) * f), int(len(self.freq) * (1 - f))
        phase_fit_coefficients = np.polyfit(self.freq[fit_range[0]:fit_range[1]],
                                            self.phase_unwrap[fit_range[0]:fit_range[1]],
                                            2)
        t_phase_fit = [
            it ** 2 * phase_fit_coefficients[0] + it * phase_fit_coefficients[1] + phase_fit_coefficients[2]
            for it in self.freq]

        self.phase_error = [self.phase_unwrap[it] - t_phase_fit[it] for it in range(len(self.phase_unwrap))]
        self.gd_error = np.gradient(self.phase_error) / np.gradient(self.wl) * - 1

        self.chirp = np.polyfit(self.wl, self.gd, 1)[0]

    def get_single_phase(self, wl_current, nz, cpus, resolution_points, terminal_print=True):
        if self.stop:
            return

        k_zw = [2 * math.pi * element / wl_current for element in nz]
        t_current = []
        t_old = [0. + 0.j for _ in range(4)]

        for it in range(self.a.numberOfPoints):
            t_t_0 = (2 * k_zw[it])
            t_t_1 = (k_zw[it] + k_zw[it + 1])
            t_t_3 = (k_zw[it] - k_zw[it + 1])
            t_t_2 = (cmath.exp(complex(0, 1) * self.a.dZ * k_zw[it]))
            t_t_4 = (cmath.exp(complex(0, -1) * self.a.dZ * k_zw[it]))

            t0 = (t_t_1 * t_t_2) / t_t_0
            t1 = (t_t_3 * t_t_4) / t_t_0
            t2 = (t_t_3 * t_t_2) / t_t_0
            t3 = (t_t_1 * t_t_4) / t_t_0

            if it == 0:
                t_current.append(t0)
                t_current.append(t1)
                t_current.append(t2)
                t_current.append(t3)
            else:
                t_current[0] = (t0 * t_old[0]) + (t2 * t_old[1])
                t_current[1] = (t1 * t_old[0]) + (t3 * t_old[1])
                t_current[2] = (t0 * t_old[2]) + (t2 * t_old[3])
                t_current[3] = (t1 * t_old[2]) + (t3 * t_old[3])

            t_old = t_current.copy()

        v3 = (t_current[2] * -1) / t_current[3]
        reflection = abs(v3) ** 2
        phase = cmath.phase(v3)

        with count.get_lock():
            count.value += 1

        progress = min((count.value / (resolution_points - 1) * 100 * cpus).__round__(1), 100)

        if terminal_print:
            print(str(progress) + "%")
            print("Wl: " + str(wl_current) + "nm")
            print("Power : " + str(reflection))
            print("Phase : " + str(phase))
            print("")

        return [wl_current, reflection, phase]

    def get_apodization(self):
        return self.a
