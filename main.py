# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cmath
import math
from time import process_time
import asyncio
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt

# numberOfPoints = 301536
numberOfPoints = 111536
L = 50.00
c = 300000
n0 = 1.456
dN = 0.002950
lambdaFBG = 1030
deltaN = 0
deltaZ = 10000000
dZ = L / numberOfPoints * 10 ** 6
lambdaFBGStart = 1021.75
lambdaFBGStop = 1038.25
deltaLambdaFBG = abs(lambdaFBGStart - lambdaFBGStop)
alpha = 4
lap = 0.400
z0 = L * 1000000
arrayZSize = z0 / dZ
blueFirst: bool = True

resolution = 0.00400


def get_apodization_and_nz_array():
    apodization_array_t = []
    zArrayT = []
    lambdaArrayT = []
    nzArrayT = []

    if blueFirst:
        zStart = z0  # Blue first
    else:
        zStart = 0  # Red first

    zTemp = zStart
    xArrayT = []
    for i in range(numberOfPoints + 1):
        xArrayT.append(i * deltaLambdaFBG / numberOfPoints)
        zArrayT.append(zTemp)
        apodization_array_t.append(
            1 / 2 * (math.tanh(alpha * (xArrayT[i] - 0 - lap)) +
                     math.tanh(alpha * (deltaLambdaFBG - xArrayT[i] - lap))))

        lambdaArrayT.append(lambdaFBGStart + i * deltaLambdaFBG / numberOfPoints)

        nzArrayT.append((n0 + dN * math.sin(4 * math.pi * zArrayT[i] * n0 / lambdaFBG -
                                            2 * math.pi * n0 / lambdaFBG ** 2 * deltaLambdaFBG / (L * 10 ** 6) *
                                            (zArrayT[i] - L * 10 ** 6 / 2) ** 2) * apodization_array_t[i]) +
                        (deltaN * math.sin(2 * math.pi * zArrayT[i] / deltaZ)))

        if blueFirst:
            zTemp -= dZ  # Blue first
        else:
            zTemp += dZ  # Red first

    if blueFirst:
        apodization_array_t.reverse()  # Blue first
    return [apodization_array_t, nzArrayT]


def get_phase_and_power(nz_array_temp, lambda_current_temp):
    lambdaZWArray = []
    kZWArray = []
    tb = np.empty((numberOfPoints, 4))
    ts = np.empty((numberOfPoints, 4), dtype=complex)
    # T = np.empty((numberOfPoints, 4), dtype=complex)
    T = np.empty((4), dtype=complex)
    TLast = np.empty((numberOfPoints, 4), dtype=complex)
    for i in range(numberOfPoints + 1):
        lambdaZWArray.append(lambda_current_temp / nz_array_temp[i])
        kZWArray.append(2 * math.pi * nz_array_temp[i] / lambda_current_temp)
    # print("kZWArray done")

    TCurrent = np.zeros(4, dtype=complex)
    TOld = np.zeros(4, dtype=complex)

    for i in range(numberOfPoints):

        # tb[i][0] = ((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i]))
        # tb[i][1] = ((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i]))
        # tb[i][2] = tb[i][1]
        # tb[i][3] = tb[i][0]
        #
        # # print("tb done")
        #
        # ts[i][0] = (cmath.exp(complex(0, 1) * dZ * kZWArray[i]))
        # ts[i][1] = 0
        # ts[i][2] = 0
        # ts[i][3] = (cmath.exp(complex(0, -1) * dZ * kZWArray[i]))

        # print("ts done")

        # T[i][0] = (tb[i][0] * ts[i][0]) + (tb[i][1] * ts[i][2])
        # T[i][1] = (tb[i][0] * ts[i][1]) + (tb[i][1] * ts[i][3])
        # T[i][2] = (tb[i][2] * ts[i][0]) + (tb[i][3] * ts[i][2])
        # T[i][3] = (tb[i][2] * ts[i][1]) + (tb[i][3] * ts[i][3])

        # print("T done")

        # T[i][0] = (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * (cmath.exp(complex(0, 1) * dZ * kZWArray[i]))) + (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * 0)
        # T[i][1] = (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * 0) + (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * (cmath.exp(complex(0, -1) * dZ * kZWArray[i])))
        # T[i][2] = (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * (cmath.exp(complex(0, 1) * dZ * kZWArray[i]))) + (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * 0)
        # T[i][3] = (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * 0) + (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * (cmath.exp(complex(0, -1) * dZ * kZWArray[i])))

        T[0] = (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * (
            cmath.exp(complex(0, 1) * dZ * kZWArray[i]))) + (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * 0)
        T[1] = (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * 0) + (
                    ((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * (
                cmath.exp(complex(0, -1) * dZ * kZWArray[i])))
        T[2] = (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * (
            cmath.exp(complex(0, 1) * dZ * kZWArray[i]))) + (((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * 0)
        T[3] = (((kZWArray[i] - kZWArray[i + 1]) / (2 * kZWArray[i])) * 0) + (
                    ((kZWArray[i] + kZWArray[i + 1]) / (2 * kZWArray[i])) * (
                cmath.exp(complex(0, -1) * dZ * kZWArray[i])))

        if i == 0:
            TCurrent[0] = (T[0] * 1) + (T[2] * 0)
            TCurrent[1] = (T[1] * 1) + (T[3] * 0)
            TCurrent[2] = (T[0] * 0) + (T[2] * 1)
            TCurrent[3] = (T[1] * 0) + (T[3] * 1)

        else:
            TCurrent[0] = (T[0] * TOld[0]) + (T[2] * TOld[1])
            TCurrent[1] = (T[1] * TOld[0]) + (T[3] * TOld[1])
            TCurrent[2] = (T[0] * TOld[2]) + (T[2] * TOld[3])
            TCurrent[3] = (T[1] * TOld[2]) + (T[3] * TOld[3])

        for i in range(4):
            TOld[i] = TCurrent[i]

    # for i in range(numberOfPoints):
    #     if i == 0:
    #         TLast[i][0] = (T[i][0] * 1) + (T[i][2] * 0)
    #         TLast[i][1] = (T[i][1] * 1) + (T[i][3] * 0)
    #         TLast[i][2] = (T[i][0] * 0) + (T[i][2] * 1)
    #         TLast[i][3] = (T[i][1] * 0) + (T[i][3] * 1)
    #     else:
    #         TLast[i][0] = (T[i][0] * TLast[i - 1][0]) + (T[i][2] * TLast[i - 1][1])
    #         TLast[i][1] = (T[i][1] * TLast[i - 1][0]) + (T[i][3] * TLast[i - 1][1])
    #         TLast[i][2] = (T[i][0] * TLast[i - 1][2]) + (T[i][2] * TLast[i - 1][3])
    #         TLast[i][3] = (T[i][1] * TLast[i - 1][2]) + (T[i][3] * TLast[i - 1][3])

    print("TLast done")
    # S2: complex = TLast[numberOfPoints - 1, 2]
    # T2: complex = TLast[numberOfPoints - 1, 3]
    S2: complex = TCurrent[2]
    T2: complex = TCurrent[3]

    V3: complex = (S2 * -1) / T2
    PowerT = abs(V3) ** 2
    PhaseT = cmath.phase(V3)

    return [PowerT, PhaseT]




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    apodization_nz_temp = get_apodization_and_nz_array()
    apodizationArray = apodization_nz_temp[0]
    nzArray = apodization_nz_temp[1]

    # start = process_time()
    # powerPhaseTemp = get_phase_and_power(nzArray, 1031)
    # end = process_time()
    # print("Phase and Power done")
    # print("Power : " + str(powerPhaseTemp[0]))
    # print("Phase : " + str(powerPhaseTemp[1]))
    # print("Time : " + str(round(end-start, 5)) + " seconds")

    resolution_points: int = round((deltaLambdaFBG + 2) / resolution)
    lambda_arrayT = []
    for i in range(resolution_points - 1):
        lambda_arrayT.append((lambdaFBGStart - 1) + (resolution * i))

    power_arrayT = []
    phase_arrayT = []

    for i in range(resolution_points - 1):
        print(lambda_arrayT[i])
        start = process_time()
        powerPhaseTemp = get_phase_and_power(nzArray, lambda_arrayT[i])
        end = process_time()

        power_arrayT.append(powerPhaseTemp[0])
        phase_arrayT.append(powerPhaseTemp[1])

        print("Phase and Power done")
        print("Power : " + str(powerPhaseTemp[0]))
        print("Phase : " + str(powerPhaseTemp[1]))
        print("Time : " + str(round(end - start, 5)) + " seconds")
        print("")

    plt.plot(lambda_arrayT, power_arrayT)
    plt.show()
    plt.plot(lambda_arrayT, phase_arrayT)
    plt.show()

    # print(power)
    # print(phase)
