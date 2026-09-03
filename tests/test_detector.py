import numpy as np

from materials.silicon import Silicon
from physics.detector import Detector


def test_depletion_width_does_not_exceed_detector_thickness():
    detector = Detector(Silicon(), 300, 1.0, 0.70, 1e15)
    voltage = np.array([0.0, 100.0, 500.0, 5000.0])
    width = detector.depletion_width(voltage)
    assert np.all(width <= detector.thickness_cm)


def test_capacitance_is_positive():
    detector = Detector(Silicon(), 300, 1.0, 0.70, 1e15)
    width = detector.depletion_width(np.array([0.0, 100.0, 500.0]))
    cap = detector.capacitance(width)
    assert np.all(cap > 0)


def test_full_depletion_voltage_is_nonnegative():
    detector = Detector(Silicon(), 300, 1.0, 0.70, 1e15)
    assert detector.full_depletion_voltage() >= 0
