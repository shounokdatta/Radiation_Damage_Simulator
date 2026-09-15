import numpy as np
from constants import Q, EPS_SI

class Detector:
    def __init__(self, material, thickness_um, area_cm2, v_bi=0.7, n_eff=1e15):
        self.material = material
        self.thickness_um = float(thickness_um)
        self.thickness_cm = self.thickness_um * 1e-4
        self.area_cm2 = float(area_cm2)
        self.v_bi = float(v_bi)
        self.n_eff = float(n_eff)

    def depletion_width(self, reverse_voltage):
        return self.depletion_width_for_doping(reverse_voltage, self.n_eff)

    def depletion_width_for_doping(self, reverse_voltage, doping):
        vr = np.asarray(reverse_voltage, dtype=float)
        nd = float(doping)
        w = np.sqrt(np.maximum(0.0, 2 * EPS_SI * (self.v_bi + vr) / (Q * nd)))
        return np.minimum(w, self.thickness_cm)

    def full_depletion_voltage(self):
        vfd = Q * self.n_eff * self.thickness_cm**2 / (2 * EPS_SI) - self.v_bi
        return max(float(vfd), 0.0)

    def capacitance(self, width_cm):
        w = np.asarray(width_cm, dtype=float)
        return EPS_SI * self.area_cm2 / np.maximum(w, 1e-30)
