import numpy as np
from detector.leakage_current import LeakageCurrent


def test_reference_temperature_preserves_alpha_model():
    model = LeakageCurrent(4e-17)
    current = model.calculate(1e16, 1.0, 300e-4, 293.15)
    expected = 4e-17 * 1e16 * 1.0 * 300e-4
    assert np.isclose(current, expected)


def test_current_increases_with_fluence():
    model = LeakageCurrent(4e-17)
    low = model.calculate(1e14, 1.0, 100e-4, 293.15)
    high = model.calculate(1e16, 1.0, 100e-4, 293.15)
    assert high > low


def test_current_increases_with_temperature():
    model = LeakageCurrent(4e-17)
    cold = model.calculate(1e16, 1.0, 100e-4, 273.15)
    hot = model.calculate(1e16, 1.0, 100e-4, 313.15)
    assert hot > cold
