# ============================================================
# SIMULATION ENGINE
# ============================================================

from dataclasses import dataclass

import numpy as np

from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent


# ============================================================
# SIMULATION PARAMETERS
# ============================================================

@dataclass
class SimulationParameters:

    thickness_um: float
    area_cm2: float

    doping_cm3: float
    v_bi: float

    temperature_k: float

    fluence: float
    alpha: float

    voltage_min: float
    voltage_max: float
    voltage_step: float


# ============================================================
# SIMULATION RESULT
# ============================================================

@dataclass
class SimulationResult:

    voltage: np.ndarray
    depletion_width_cm: np.ndarray
    capacitance_f: np.ndarray
    leakage_a: np.ndarray

    full_depletion_voltage: float

    detector: Detector
    leakage_model: LeakageCurrent


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_parameters(params):

    if params.thickness_um <= 0:
        raise ValueError(
            "Thickness must be greater than zero."
        )

    if params.area_cm2 <= 0:
        raise ValueError(
            "Area must be greater than zero."
        )

    if params.doping_cm3 <= 0:
        raise ValueError(
            "Doping must be greater than zero."
        )

    if params.v_bi < 0:
        raise ValueError(
            "Built-in voltage cannot be negative."
        )

    if params.temperature_k <= 0:
        raise ValueError(
            "Temperature must be greater than zero."
        )

    if params.fluence < 0:
        raise ValueError(
            "Fluence cannot be negative."
        )

    if params.alpha <= 0:
        raise ValueError(
            "Alpha must be greater than zero."
        )

    if params.voltage_min < 0:
        raise ValueError(
            "Minimum reverse voltage cannot be negative."
        )

    if params.voltage_max <= params.voltage_min:
        raise ValueError(
            "Maximum voltage must be greater than minimum voltage."
        )

    if params.voltage_step <= 0:
        raise ValueError(
            "Voltage step must be greater than zero."
        )


# ============================================================
# RUN SIMULATION
# ============================================================

def run_simulation(params):

    validate_parameters(
        params
    )

    # --------------------------------------------------------
    # Silicon
    # --------------------------------------------------------

    silicon = Silicon()

    # --------------------------------------------------------
    # Detector
    # --------------------------------------------------------

    detector = Detector(
        material=silicon,
        thickness_um=params.thickness_um,
        area_cm2=params.area_cm2,
        v_bi=params.v_bi,
        n_eff=params.doping_cm3
    )

    # --------------------------------------------------------
    # Leakage model
    # --------------------------------------------------------

    leakage_model = LeakageCurrent(
        alpha=params.alpha
    )

    # --------------------------------------------------------
    # Voltage array
    # --------------------------------------------------------

    voltage = np.arange(
        params.voltage_min,
        params.voltage_max
        + params.voltage_step,
        params.voltage_step
    )

    # Remove accidental point above maximum
    voltage = voltage[
        voltage <= params.voltage_max
    ]

    # --------------------------------------------------------
    # Depletion width
    # --------------------------------------------------------

    depletion_width = detector.depletion_width(
        voltage
    )

    # --------------------------------------------------------
    # Capacitance
    # --------------------------------------------------------

    capacitance = detector.capacitance(
        depletion_width
    )

    # --------------------------------------------------------
    # Leakage current
    # --------------------------------------------------------

    leakage = leakage_model.calculate(
        fluence=params.fluence,
        area_cm2=params.area_cm2,
        thickness_cm=depletion_width,
        temperature_k=params.temperature_k
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return SimulationResult(

        voltage=voltage,

        depletion_width_cm=depletion_width,

        capacitance_f=capacitance,

        leakage_a=np.asarray(
            leakage,
            dtype=float
        ),

        full_depletion_voltage=(
            detector.full_depletion_voltage()
        ),

        detector=detector,

        leakage_model=leakage_model
    )