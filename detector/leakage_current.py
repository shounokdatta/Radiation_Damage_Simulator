import numpy as np
from constants import Q, EG_SI, K_B_EV

class LeakageCurrent:
    def __init__(self, alpha=4e-17):
        self.alpha = float(alpha)

    @staticmethod
    def temperature_factor(temperature_k):
        T=np.asarray(temperature_k,dtype=float)
        return (T/300.0)**2 * np.exp((-EG_SI/(2*K_B_EV))*(1/T-1/300.0))

    def calculate(self, fluence, area_cm2, thickness_cm, temperature_k=None):
        # alpha * fluence * depleted volume; temperature dependence is applied when supplied.
        current = self.alpha * np.asarray(fluence,dtype=float) * float(area_cm2) * np.asarray(thickness_cm,dtype=float)
        if temperature_k is not None:
            current = current * self.temperature_factor(temperature_k)
        return current
