from constants import EPSILON_SI


class Silicon:

    def __init__(self):
        self.name = "Silicon"
        self.permittivity = EPSILON_SI

    def __str__(self):
        return (
            f"Material: {self.name}\n"
            f"Permittivity: {self.permittivity:.4e} F/cm"
        )