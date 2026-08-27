# ============================================================
# LEAKAGE CURRENT MODEL
# ============================================================


class LeakageCurrent:

    def __init__(self, alpha):
        """
        alpha:
            Radiation damage constant (A/cm)
        """

        self.alpha = alpha

    def calculate(
        self,
        fluence,
        area_cm2,
        thickness_cm
    ):
        """
        Calculate radiation-induced leakage current.

        Formula:

            I = alpha × Phi × V

        where:

            I     = leakage current (A)
            alpha = radiation damage constant (A/cm)
            Phi   = radiation fluence (neq/cm²)
            V     = detector volume (cm³)
        """

        volume = area_cm2 * thickness_cm

        current = (
            self.alpha
            * fluence
            * volume
        )

        return current