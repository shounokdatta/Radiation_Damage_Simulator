import numpy as np
from constants import Q, EPSILON_SI


class Detector:
    """Planar silicon detector under reverse bias."""

    def __init__(self, material, thickness_um, area_cm2, v_bi, n_eff):
        self.material = material
        self.thickness_um = float(thickness_um)
        self.thickness_cm = self.thickness_um * 1e-4
        self.area_cm2 = float(area_cm2)
        self.v_bi = float(v_bi)
        self.n_eff = float(n_eff)
        self.epsilon = EPSILON_SI

        if self.thickness_um <= 0:
            raise ValueError("Detector thickness must be greater than zero.")
        if self.area_cm2 <= 0:
            raise ValueError("Detector area must be greater than zero.")
        if self.n_eff <= 0:
            raise ValueError("Effective doping must be greater than zero.")
        if self.v_bi < 0:
            raise ValueError("Built-in voltage cannot be negative.")

    def depletion_width(self, reverse_voltage):
        reverse_voltage = np.asarray(reverse_voltage, dtype=float)
        if np.any(reverse_voltage < 0):
            raise ValueError("Reverse-bias voltage cannot be negative.")

        width = np.sqrt(
            (2.0 * self.epsilon * (reverse_voltage + self.v_bi))
            / (Q * self.n_eff)
        )
        return np.minimum(width, self.thickness_cm)

    def depletion_width_for_doping(self, reverse_voltage, doping):
        doping = float(doping)
        if doping <= 0:
            raise ValueError("Doping must be greater than zero.")

        reverse_voltage = np.asarray(reverse_voltage, dtype=float)
        width = np.sqrt(
            (2.0 * self.epsilon * (reverse_voltage + self.v_bi))
            / (Q * doping)
        )
        return np.minimum(width, self.thickness_cm)

    def capacitance(self, depletion_width):
        depletion_width = np.asarray(depletion_width, dtype=float)
        if np.any(depletion_width <= 0):
            raise ValueError("Depletion width must be greater than zero.")
        return self.epsilon * self.area_cm2 / depletion_width

    def full_depletion_voltage(self):
        voltage = (
            (Q * self.n_eff * self.thickness_cm**2)
            / (2.0 * self.epsilon)
        ) - self.v_bi
        return max(float(voltage), 0.0)
