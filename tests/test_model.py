import unittest

import pytest

from model.model import Phase

if __name__ == '__main__':
    unittest.main()


@pytest.fixture
def init_phase():
    _model = Phase()
    _model.a.length = 1
    _model.a.resolution = 0.00400
    _model.a.dN = 0.020000
    _model.a.lambdaFBG = 1030
    _model.a.lambdaFBGStop = 1029.5
    _model.a.lambdaFBGStart = 1030.5
    _model.a.alpha = 4
    _model.a.l_ap = 0.1
    return _model


@pytest.mark.parametrize("length,alpha,t_array", [
    (50, 4, [1030, 0.9999999999999967, -2.2634550156192006]),
    (5, 1, [1030, 1.0000000000000013, 1.4470481762137468]),
])
def test_get_single_phase(init_phase, length, alpha, t_array):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    assert init_phase.get_single_phase(1030, init_phase.a.nz_array, 1, 10000, terminal_print=False) == t_array


@pytest.mark.parametrize("length,alpha,t_array", [
    (50, 4, [1030, 0.9999999999999867, -2.2634550156192006]),
    (5, 1, [1030, 1.0000000000000013, 1.4470481762137478]),
])
def test_get_single_phase_negative(init_phase, length, alpha, t_array):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    assert init_phase.get_single_phase(1030, init_phase.a.nz_array, 1, 10000, terminal_print=False) != t_array


def test_get_apodization(init_phase):
    assert init_phase.get_apodization() == init_phase.a


@pytest.mark.parametrize("length,alpha,chirp", [
    (2, 1, 7.835483099489743),
    (1, 2, 5.061191306919394),
])
def test_update_phase(init_phase, length, alpha, chirp):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    init_phase.update_phase(terminal_print=False)
    assert init_phase.chirp == chirp


@pytest.mark.parametrize("length,alpha,chirp", [
    (2, 1, 7.835483099489753),
    (1, 2, 5.061191306919384),
])
def test_update_phase_negative(init_phase, length, alpha, chirp):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    init_phase.update_phase(terminal_print=False)
    assert init_phase.chirp != chirp
