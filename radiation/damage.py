# ============================================================
# RADIATION DAMAGE
# ============================================================


def radiation_damage_current(
    alpha,
    fluence,
    area_cm2,
    depletion_width_cm
):
    """
    Calculate radiation-induced leakage current.

    Parameters
    ----------
    alpha : float
        Radiation damage constant in A/cm.

    fluence : float
        Radiation fluence in neq/cm^2.

    area_cm2 : float
        Detector area in cm^2.

    depletion_width_cm : float
        Depleted detector thickness in cm.

    Returns
    -------
    float
        Leakage current in amperes.
    """

    depleted_volume = (
        area_cm2
        * depletion_width_cm
    )

    current = (
        alpha
        * fluence
        * depleted_volume
    )

    return current