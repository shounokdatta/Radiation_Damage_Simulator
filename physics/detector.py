# ============================================================
# SILICON DETECTOR PHYSICS
# ============================================================

import numpy as np

from constants import Q, EPSILON_SI


class Detector:

    def __init__(
        self,
        material,
        thickness_um,
        area_cm2,
        v_bi,
        n_eff
    ):

        self.material = material

        # Detector dimensions
        self.thickness_um = thickness_um
        self.thickness_cm = thickness_um * 1e-4

        self.area_cm2 = area_cm2

        # Junction parameters
        self.v_bi = v_bi
        self.n_eff = n_eff

        # Silicon permittivity
        self.epsilon = EPSILON_SI


    # ========================================================
    # DEPLETION WIDTH
    # ========================================================

    def depletion_width(self, reverse_voltage):

        reverse_voltage = np.asarray(
            reverse_voltage,
            dtype=float
        )

        # Depletion width:
        #
        # W = sqrt[
        #       2 * epsilon * (V_R + V_BI)
        #       --------------------------------
        #              q * N_eff
        # ]

        depletion_width = np.sqrt(
            (
                2
                * self.epsilon
                * (reverse_voltage + self.v_bi)
            )
            /
            (
                Q
                * self.n_eff
            )
        )

        # Depletion width cannot exceed detector thickness
        depletion_width = np.minimum(
            depletion_width,
            self.thickness_cm
        )

        return depletion_width


    # ========================================================
    # CAPACITANCE
    # ========================================================

    def capacitance(self, depletion_width):

        depletion_width = np.asarray(
            depletion_width,
            dtype=float
        )

        # C = epsilon * A / W
        capacitance = (
            self.epsilon
            * self.area_cm2
            / depletion_width
        )

        return capacitance


    # ========================================================
    # FULL DEPLETION VOLTAGE
    # ========================================================

    def full_depletion_voltage(self):

        # V_fd =
        #
        # q * N_eff * d^2
        # ---------------- - V_BI
        #      2 * epsilon

        voltage = (
            (
                Q
                * self.n_eff
                * self.thickness_cm ** 2
            )
            /
            (
                2
                * self.epsilon
            )
        ) - self.v_bi

        # Full depletion voltage cannot be negative
        return max(voltage, 0.0)