import math


class Apodization:
    def __init__(self):
        self.wl_array = []
        self.apodization_array = []
        self.nz_array = []

        self.length = 5.00
        self.c = 300000
        self.n0 = 1.456
        self.dN = 0.008000
        self.lambdaFBG = 1030
        self.deltaN = 0
        self.deltaZ = 10000000
        self.lambdaFBGStart = 1021.75
        self.lambdaFBGStop = 1038.25
        self.alpha = 4.0
        self.l_ap = 0.400
        self.redFirst: bool = True
        self.resolution = 0.00400
        self.dZ = 0

        self.numberOfPoints = int(self.length * 2000)

        self.resolution_points: int = 0

        if len(self.apodization_array) == 0:
            self.apodization_update()

    def apodization_update(self):
        z0 = self.length * 1000000
        self.numberOfPoints = int(self.length * 2000)
        self.dZ = self.length / self.numberOfPoints * 10 ** 6
        delta_lambda_fbg = abs(self.lambdaFBGStart - self.lambdaFBGStop)

        apod_array_t = []
        z_array_t = []
        lambda_array_t = []
        nz_array_t = []

        if self.redFirst:
            z_start = z0  # Blue first
        else:
            z_start = 0  # Red first

        z = z_start
        x_array_t = []
        for it in range(self.numberOfPoints + 1):
            x_array_t.append(it * delta_lambda_fbg / self.numberOfPoints)
            z_array_t.append(z)
            apod_array_t.append(
                1 / 2 * (math.tanh(self.alpha * (x_array_t[it] - 0 - self.l_ap)) +
                         math.tanh(self.alpha * (delta_lambda_fbg - x_array_t[it] - self.l_ap))))

            lambda_array_t.append(self.lambdaFBGStart + it * delta_lambda_fbg / self.numberOfPoints)

            nz_array_t.append((self.n0 + self.dN * math.sin(4 * math.pi * z_array_t[it] * self.n0 / self.lambdaFBG -
                                                            2 * math.pi * self.n0 / self.lambdaFBG ** 2 *
                                                            delta_lambda_fbg / (self.length * 10 ** 6) *
                                                            (z_array_t[it] - self.length * 10 ** 6 / 2) ** 2) *
                               apod_array_t[it]) +
                              (self.deltaN * math.sin(2 * math.pi * z_array_t[it] / self.deltaZ)))

            if self.redFirst:
                z -= self.dZ  # Blue first
            else:
                z += self.dZ  # Red first

        if self.redFirst:
            apod_array_t.reverse()  # Blue first

        self.wl_array = lambda_array_t
        self.apodization_array = apod_array_t
        self.nz_array = nz_array_t

        delta_lambda_fbg = abs(self.lambdaFBGStart - self.lambdaFBGStop)
        self.resolution_points = round((delta_lambda_fbg + 2) / self.resolution)
