from constants import EPS_SI, K_B_EV, EG_SI

class Silicon:
    name = "Silicon"
    relative_permittivity = 11.7
    bandgap_ev = EG_SI
    intrinsic_carrier_reference_cm3 = 1.45e10

    @property
    def permittivity_f_cm(self):
        return EPS_SI

    def intrinsic_carrier(self, temperature_k):
        import numpy as np
        T = np.asarray(temperature_k, dtype=float)
        return self.intrinsic_carrier_reference_cm3 * (T / 300.0) ** 1.5 * np.exp(-self.bandgap_ev/(2*K_B_EV) * (1/T - 1/300.0))
