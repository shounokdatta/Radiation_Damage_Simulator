# ============================================================
# SILICON DETECTOR PHYSICS
# ============================================================

import numpy as np

from constants import Q


class Detector:
    """
    Silicon semiconductor detector model.

    Calculates:
        1. Full depletion voltage
        2. Depletion width
        3. Detector capacitance
    """

    def __init__(
        self,
        material,
        thickness_um,
        area_cm2,
        v_bi,
        n_eff
    ):
        # ----------------------------------------------------
        # Material
        # ----------------------------------------------------

        self.material = material

        # ----------------------------------------------------
        # Detector geometry
        # ----------------------------------------------------

        self.thickness_um = thickness_um

        # Convert micrometers to centimeters
        #
        # 1 µm = 1e-4 cm
        #
        self.thickness_cm = thickness_um * 1e-4

        self.area_cm2 = area_cm2

        # ----------------------------------------------------
        # Electrical parameters
        # ----------------------------------------------------

        self.v_bi = v_bi

        # Effective doping concentration
        # units: cm^-3
        self.n_eff = n_eff

        # ----------------------------------------------------
        # Material permittivity
        # ----------------------------------------------------

        self.epsilon = material.permittivity


    # ========================================================
    # FULL DEPLETION VOLTAGE
    # ========================================================

    def full_depletion_voltage(self):
        """
        Calculate the voltage required to fully deplete
        the silicon detector.

        Formula:

            V_fd = (q * N_eff * d²)
                   / (2 * epsilon) - V_bi

        Returns:
            Full depletion voltage in volts.
        """

        voltage = (
            Q
            * self.n_eff
            * self.thickness_cm ** 2
            /
            (2 * self.epsilon)
        )

        voltage = voltage - self.v_bi

        # Voltage cannot be negative
        return max(voltage, 0.0)


    # ========================================================
    # DEPLETION WIDTH
    # ========================================================

    def depletion_width(self, reverse_voltage):
        """
        Calculate depletion width for a given reverse bias.

        Formula:

            W = sqrt[
                2 * epsilon * (V_bi + V_R)
                --------------------------------
                q * N_eff
            ]

        The depletion width cannot exceed the physical
        detector thickness.

        Parameters:
            reverse_voltage:
                Reverse bias voltage in volts.

        Returns:
            Depletion width in cm.
        """

        reverse_voltage = np.asarray(
            reverse_voltage,
            dtype=float
        )

        width = np.sqrt(
            (
                2
                * self.epsilon
                * (self.v_bi + reverse_voltage)
            )
            /
            (
                Q
                * self.n_eff
            )
        )

        # ----------------------------------------------------
        # Physical limit:
        # depletion width cannot exceed detector thickness
        # ----------------------------------------------------

        width = np.minimum(
            width,
            self.thickness_cm
        )

        return width


    # ========================================================
    # CAPACITANCE
    # ========================================================

    def capacitance(self, depletion_width):
        """
        Calculate detector junction capacitance.

        Formula:

            C = epsilon * A / W

        Parameters:
            depletion_width:
                Depletion width in cm.

        Returns:
            Capacitance in Farads.
        """

        # Avoid division by zero
        depletion_width = np.maximum(
            depletion_width,
            1e-20
        )

        capacitance = (
            self.epsilon
            * self.area_cm2
            / depletion_width
        )

        return capacitance