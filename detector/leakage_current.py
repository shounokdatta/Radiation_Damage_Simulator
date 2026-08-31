# ============================================================
# RADIATION-INDUCED LEAKAGE CURRENT
# ============================================================


class LeakageCurrent:

    def __init__(self, alpha):

        self.alpha = alpha


    # ========================================================
    # CALCULATE LEAKAGE CURRENT
    # ========================================================

    def calculate(
        self,
        fluence,
        area_cm2,
        thickness_cm
    ):

        # Depleted detector volume:
        #
        # V = Area × Depletion Width

        depleted_volume = (
            area_cm2
            * thickness_cm
        )

        # Radiation-induced leakage current:
        #
        # I = alpha × fluence × volume

        current = (
            self.alpha
            * fluence
            * depleted_volume
        )

        return current