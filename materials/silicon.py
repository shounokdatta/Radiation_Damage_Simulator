from constants import EPSILON_SI, EG_SI


class Silicon:
    """Basic silicon material properties used by the simulator."""

    def __init__(self):
        self.name = "Silicon"
        self.relative_permittivity = 11.7
        self.permittivity = EPSILON_SI
        self.band_gap_ev = EG_SI

    def __repr__(self):
        return (
            f"Silicon(relative_permittivity={self.relative_permittivity}, "
            f"band_gap_ev={self.band_gap_ev})"
        )
