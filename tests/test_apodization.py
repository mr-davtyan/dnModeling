import unittest

import pytest

from model.model import Phase

if __name__ == '__main__':
    unittest.main()


@pytest.fixture
def init_phase():
    _model = Phase()
    _model.a.length = 50
    _model.a.resolution = 0.00400
    _model.a.dN = 0.008000
    _model.a.lambdaFBG = 1030
    _model.a.lambdaFBGStop = 1020
    _model.a.lambdaFBGStart = 1040
    _model.a.alpha = 4
    _model.a.l_ap = 0.400
    return _model


@pytest.mark.parametrize("length,alpha,t_nz_value", [
    (50, 4, 1.4508369597643913),
    (5, 1, 1.4540672556211285),
])
def test_apodization_update(init_phase, length, alpha, t_nz_value):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    assert init_phase.a.nz_array[int(len(init_phase.a.nz_array)/2)] == t_nz_value


@pytest.mark.parametrize("length,alpha,t_nz_value", [
    (50, 4, 1.4508369597643923),
    (5, 1, 1.4540672556211295),
])
def test_apodization_update_negative(init_phase, length, alpha, t_nz_value):
    init_phase.a.length = length
    init_phase.a.alpha = alpha
    init_phase.a.apodization_update()
    assert init_phase.a.nz_array[int(len(init_phase.a.nz_array)/2)] != t_nz_value
