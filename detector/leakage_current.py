import numpy as np
from constants import K_B_EV, EG_SI, T_REF_K


class LeakageCurrent:
    """
    Radiation-induced leakage-current model:

        I_ref = alpha * fluence * depleted_volume

    An optional silicon temperature scaling is applied relative to T_REF_K:

        f(T) = (T/T_ref)^2 * exp[-Eg/(2kB) * (1/T - 1/T_ref)]

    Therefore temperature=T_REF_K preserves the original alpha model exactly.
    """

    def __init__(self, alpha):
        self.alpha = float(alpha)
        if self.alpha <= 0:
            raise ValueError("Damage constant alpha must be greater than zero.")

    @staticmethod
    def temperature_factor(temperature_k):
        temperature_k = np.asarray(temperature_k, dtype=float)
        if np.any(temperature_k <= 0):
            raise ValueError("Temperature must be greater than 0 K.")

        return (temperature_k / T_REF_K) ** 2 * np.exp(
            -EG_SI / (2.0 * K_B_EV)
            * (1.0 / temperature_k - 1.0 / T_REF_K)
        )

    def calculate(
        self,
        fluence,
        area_cm2,
        thickness_cm,
        temperature_k=T_REF_K,
    ):
        fluence = float(fluence)
        area_cm2 = float(area_cm2)
        thickness_cm = np.asarray(thickness_cm, dtype=float)

        if fluence < 0:
            raise ValueError("Fluence cannot be negative.")
        if area_cm2 <= 0:
            raise ValueError("Area must be greater than zero.")
        if np.any(thickness_cm < 0):
            raise ValueError("Depleted thickness cannot be negative.")

        depleted_volume_cm3 = area_cm2 * thickness_cm
        current_ref = self.alpha * fluence * depleted_volume_cm3
        return current_ref * self.temperature_factor(temperature_k)
