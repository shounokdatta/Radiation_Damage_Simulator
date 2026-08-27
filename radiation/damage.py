# ============================================================
# RADIATION DAMAGE
# ============================================================


class RadiationDamage:

    def __init__(self, alpha):

        self.alpha = alpha


    # ========================================================
    # LEAKAGE CURRENT AT FULL DEPLETION
    # ========================================================

    def leakage_current(
        self,
        fluence,
        area_cm2,
        thickness_cm
    ):

        volume = (
            area_cm2
            * thickness_cm
        )

        current = (
            self.alpha
            * fluence
            * volume
        )

        return current