import cmath
import math
from collections import defaultdict
from time import process_time
import matplotlib.pyplot as plt

numberOfPoints = 301536
# numberOfPoints = 111536
length = 50.00
c = 300000
n0 = 1.456
dN = 0.002950
lambdaFBG = 1030
deltaN = 0
deltaZ = 10000000
dZ = length / numberOfPoints * 10 ** 6
lambdaFBGStart = 1021.75
lambdaFBGStop = 1038.25
deltaLambdaFBG = abs(lambdaFBGStart - lambdaFBGStop)
alpha = 4
l_ap = 0.400
z0 = length * 1000000
arrayZSize = z0 / dZ
blueFirst: bool = True
resolution = 0.10400


def get_apodization_and_nz_array():
    apodization_array_t = []
    z_array_t = []
    lambda_array_t = []
    nz_array_t = []

    if blueFirst:
        z_start = z0  # Blue first
    else:
        z_start = 0  # Red first

    z = z_start
    x_array_t = []
    for it in range(numberOfPoints + 1):
        x_array_t.append(it * deltaLambdaFBG / numberOfPoints)
        z_array_t.append(z)
        apodization_array_t.append(
            1 / 2 * (math.tanh(alpha * (x_array_t[it] - 0 - l_ap)) +
                     math.tanh(alpha * (deltaLambdaFBG - x_array_t[it] - l_ap))))

        lambda_array_t.append(lambdaFBGStart + it * deltaLambdaFBG / numberOfPoints)

        nz_array_t.append((n0 + dN * math.sin(4 * math.pi * z_array_t[it] * n0 / lambdaFBG -
                                              2 * math.pi * n0 / lambdaFBG ** 2 * deltaLambdaFBG / (length * 10 ** 6) *
                                              (z_array_t[it] - length * 10 ** 6 / 2) ** 2) * apodization_array_t[it]) +
                          (deltaN * math.sin(2 * math.pi * z_array_t[it] / deltaZ)))

        if blueFirst:
            z -= dZ  # Blue first
        else:
            z += dZ  # Red first

    if blueFirst:
        apodization_array_t.reverse()  # Blue first
    return [apodization_array_t, nz_array_t]


def get_phase_and_power(nz_array_temp, lambda_current):
    start = process_time()

    k_zw_array = [2 * math.pi * element / lambda_current for element in nz_array_temp]

    t_current = []
    t_old = [0. + 0.j for _ in range(4)]

    for it in range(numberOfPoints):
        t_t_0 = (2 * k_zw_array[it])
        t_t_1 = (k_zw_array[it] + k_zw_array[it + 1])
        t_t_3 = (k_zw_array[it] - k_zw_array[it + 1])
        t_t_2 = (cmath.exp(complex(0, 1) * dZ * k_zw_array[it]))
        t_t_4 = (cmath.exp(complex(0, -1) * dZ * k_zw_array[it]))

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

    v3: complex = (t_current[2] * -1) / t_current[3]
    reflection = abs(v3) ** 2
    phase = cmath.phase(v3)

    end = process_time()
    print("Lambda : " + str(lambda_current))
    print("Power : " + str(reflection))
    print("Phase : " + str(phase))
    print("Time : " + str(round(end - start, 5)) + " seconds")
    print("")

    return [lambda_current, reflection, phase]


if __name__ == '__main__':
    apodization_nz = get_apodization_and_nz_array()
    apodization = apodization_nz[0]
    nz = apodization_nz[1]

    resolution_points: int = round((deltaLambdaFBG + 2) / resolution)

    lambda_array = [(lambdaFBGStart - 1) + (resolution * it) for it in range(resolution_points - 1)]
    power_array = defaultdict()
    phase_array = defaultdict()

    for it in lambda_array:
        powerPhaseTemp = get_phase_and_power(nz, it)
        power_array[it] = powerPhaseTemp[1]
        phase_array[it] = powerPhaseTemp[2]
        # lambda_array.append(powerPhaseTemp[0])
        # power_array.append(powerPhaseTemp[1])
        # phase_array.append(powerPhaseTemp[2])

    plt.plot(power_array.keys(), power_array.values())
    plt.show()
    plt.plot(phase_array.keys(), phase_array.values())
    plt.show()
