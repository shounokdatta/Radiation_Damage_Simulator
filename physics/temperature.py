# physics/temperature.py


def temperature_factor(temperature_k, reference_temperature=293.15):
    """
    Simple temperature correction factor.

    This is intentionally a basic model for Version 1.
    """

    return (temperature_k / reference_temperature) ** 2