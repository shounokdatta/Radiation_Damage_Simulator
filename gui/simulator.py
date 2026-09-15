"""
Radiation Damage Simulator
Simulation backend and GUI simulation mixin.
"""

from dataclasses import dataclass
import inspect

import numpy as np

import config

from constants import (
    K_B_EV,
    EG_SI,
    T_REF_K,
)

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
    vmin: float
    vmax: float
    points: int


# ============================================================
# SIMULATION RESULT
# ============================================================

@dataclass
class SimulationResult:
    detector: object
    voltage: np.ndarray
    depletion_width_cm: np.ndarray
    capacitance_f: np.ndarray
    leakage_a: np.ndarray
    full_depletion_voltage: float


# ============================================================
# TEMPERATURE FACTOR
# ============================================================

def temperature_factor(temperature):
    """
    Temperature correction factor used by the
    radiation-damage leakage-current model.
    """

    return (
        (temperature / T_REF_K) ** 2
        *
        np.exp(
            (
                -EG_SI
                /
                (2.0 * K_B_EV)
            )
            *
            (
                1.0 / temperature
                - 1.0 / T_REF_K
            )
        )
    )


# ============================================================
# CREATE DETECTOR
# ============================================================

def create_detector(
    params,
    thickness=None,
    doping=None,
    area=None,
):
    """
    Create the silicon detector from simulation parameters.
    """

    if thickness is None:
        thickness = params.thickness_um

    if doping is None:
        doping = params.doping_cm3

    if area is None:
        area = params.area_cm2

    silicon = Silicon()

    detector = Detector(
        material=silicon,
        thickness_um=thickness,
        area_cm2=area,
        v_bi=params.v_bi,
        n_eff=doping,
    )

    return detector


# ============================================================
# CREATE LEAKAGE MODEL
# ============================================================

def create_leakage_model(params):
    """
    Create the leakage-current model.
    """

    return LeakageCurrent(
        alpha=params.alpha
    )


# ============================================================
# CALCULATE LEAKAGE CURRENT
# ============================================================

def calculate_leakage(
    leakage_model,
    fluence,
    area,
    width,
    temperature,
):
    """
    Calculate radiation-induced leakage current.

    Supports both the newer temperature-aware
    LeakageCurrent implementation and the older
    implementation.
    """

    # --------------------------------------------------------
    # Try temperature-aware leakage model first
    # --------------------------------------------------------

    try:

        signature = inspect.signature(
            leakage_model.calculate
        )

        if "temperature_k" in signature.parameters:

            return leakage_model.calculate(
                fluence=fluence,
                area_cm2=area,
                thickness_cm=width,
                temperature_k=temperature,
            )

    except (
        TypeError,
        ValueError,
    ):
        pass

    # --------------------------------------------------------
    # Older leakage-current implementation
    #
    # I = alpha × fluence × volume
    # --------------------------------------------------------

    reference_current = leakage_model.calculate(
        fluence=fluence,
        area_cm2=area,
        thickness_cm=width,
    )

    factor = temperature_factor(
        temperature
    )

    return (
        np.asarray(
            reference_current,
            dtype=float,
        )
        * factor
    )


# ============================================================
# RUN SIMULATION
# ============================================================

def run_simulation(p):
    """
    Run the complete detector simulation.

    Returns a SimulationResult object.
    """

    # --------------------------------------------------------
    # Create detector
    # --------------------------------------------------------

    detector = create_detector(
        p
    )

    # --------------------------------------------------------
    # Create leakage model
    # --------------------------------------------------------

    leakage_model = create_leakage_model(
        p
    )

    # --------------------------------------------------------
    # Reverse-bias voltage
    # --------------------------------------------------------

    voltage = np.linspace(
        p.vmin,
        p.vmax,
        p.points,
    )

    if len(voltage) < 2:
        raise ValueError(
            "Voltage range must contain at least "
            "two voltage points."
        )

    # --------------------------------------------------------
    # Depletion width
    # --------------------------------------------------------

    width = detector.depletion_width(
        voltage
    )

    # --------------------------------------------------------
    # Capacitance
    # --------------------------------------------------------

    capacitance = detector.capacitance(
        width
    )

    # --------------------------------------------------------
    # Leakage current
    # --------------------------------------------------------

    leakage = calculate_leakage(
        leakage_model=leakage_model,
        fluence=p.fluence,
        area=p.area_cm2,
        width=width,
        temperature=p.temperature_k,
    )

    # --------------------------------------------------------
    # Full depletion voltage
    # --------------------------------------------------------

    full_depletion_voltage = (
        detector.full_depletion_voltage()
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return SimulationResult(
        detector=detector,
        voltage=np.asarray(
            voltage,
            dtype=float,
        ),
        depletion_width_cm=np.asarray(
            width,
            dtype=float,
        ),
        capacitance_f=np.asarray(
            capacitance,
            dtype=float,
        ),
        leakage_a=np.asarray(
            leakage,
            dtype=float,
        ),
        full_depletion_voltage=float(
            full_depletion_voltage
        ),
    )


# ============================================================
# GUI SIMULATION MIXIN
# ============================================================

class SimulationMixin:

    # ========================================================
    # READ GUI PARAMETERS
    # ========================================================

    def read_parameters(self):

        parameters = {

            "thickness": float(
                self.thickness_var.get().strip()
            ),

            "area": float(
                self.area_var.get().strip()
            ),

            "doping": float(
                self.doping_var.get().strip()
            ),

            "vbi": float(
                self.vbi_var.get().strip()
            ),

            "temperature": float(
                self.temperature_var.get().strip()
            ),

            "initial_fluence": float(
                self.initial_fluence_var.get().strip()
            ),

            "final_fluence": float(
                self.final_fluence_var.get().strip()
            ),

            "alpha": float(
                self.alpha_var.get().strip()
            ),

            "vmin": float(
                self.vmin_var.get().strip()
            ),

            "vmax": float(
                self.vmax_var.get().strip()
            ),

            "vstep": float(
                self.vstep_var.get().strip()
            ),
        }

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if parameters["thickness"] <= 0:
            raise ValueError(
                "Thickness must be greater than zero."
            )

        if parameters["area"] <= 0:
            raise ValueError(
                "Area must be greater than zero."
            )

        if parameters["doping"] <= 0:
            raise ValueError(
                "Doping must be greater than zero."
            )

        if parameters["vbi"] < 0:
            raise ValueError(
                "Built-in voltage cannot be negative."
            )

        if parameters["temperature"] <= 0:
            raise ValueError(
                "Temperature must be greater than zero."
            )

        if parameters["initial_fluence"] < 0:
            raise ValueError(
                "Initial fluence cannot be negative."
            )

        if parameters["final_fluence"] < 0:
            raise ValueError(
                "Final fluence cannot be negative."
            )

        if parameters["alpha"] <= 0:
            raise ValueError(
                "Alpha must be greater than zero."
            )

        if parameters["vmin"] < 0:
            raise ValueError(
                "Minimum reverse voltage cannot be negative."
            )

        if parameters["vmax"] <= parameters["vmin"]:
            raise ValueError(
                "Maximum voltage must be greater than "
                "minimum voltage."
            )

        if parameters["vstep"] <= 0:
            raise ValueError(
                "Voltage step must be greater than zero."
            )

        return parameters

    # ========================================================
    # VALIDATE SWEEP
    # ========================================================

    @staticmethod
    def _validate_sweep(
        initial,
        final,
        steps,
        name,
    ):

        if initial <= 0 or final <= 0:
            raise ValueError(
                f"{name} initial and final values "
                "must be greater than zero."
            )

        if final < initial:
            raise ValueError(
                f"{name} final value must be greater than "
                "or equal to the initial value."
            )

        if steps < 2:
            raise ValueError(
                f"{name} steps must be at least 2."
            )

    # ========================================================
    # DOPING STUDY
    # ========================================================

    def get_doping_study_values(self):

        try:

            initial = float(
                self.doping_initial_var.get()
            )

            final = float(
                self.doping_final_var.get()
            )

            steps = int(
                self.doping_steps_var.get()
            )

        except ValueError as error:

            raise ValueError(
                "Initial doping, final doping and steps "
                "must be valid values."
            ) from error

        self._validate_sweep(
            initial,
            final,
            steps,
            "Doping",
        )

        return np.geomspace(
            initial,
            final,
            steps,
        )

    # ========================================================
    # THICKNESS STUDY
    # ========================================================

    def get_thickness_study_values(self):

        try:

            initial = float(
                self.thickness_initial_var.get()
            )

            final = float(
                self.thickness_final_var.get()
            )

            steps = int(
                self.thickness_steps_var.get()
            )

        except ValueError as error:

            raise ValueError(
                "Initial thickness, final thickness and "
                "steps must be valid values."
            ) from error

        self._validate_sweep(
            initial,
            final,
            steps,
            "Thickness",
        )

        return np.linspace(
            initial,
            final,
            steps,
        )

    # ========================================================
    # TEMPERATURE STUDY
    # ========================================================

    def get_temperature_study_values(self):

        try:

            initial = float(
                self.temperature_initial_var.get()
            )

            final = float(
                self.temperature_final_var.get()
            )

            steps = int(
                self.temperature_steps_var.get()
            )

        except ValueError as error:

            raise ValueError(
                "Initial temperature, final temperature "
                "and steps must be valid values."
            ) from error

        self._validate_sweep(
            initial,
            final,
            steps,
            "Temperature",
        )

        return np.linspace(
            initial,
            final,
            steps,
        )

    # ========================================================
    # CREATE DETECTOR FOR GUI
    # ========================================================

    def create_detector(
        self,
        params,
        thickness=None,
        doping=None,
        area=None,
    ):

        if thickness is None:
            thickness = params["thickness"]

        if doping is None:
            doping = params["doping"]

        if area is None:
            area = params["area"]

        silicon = Silicon()

        return Detector(
            material=silicon,
            thickness_um=thickness,
            area_cm2=area,
            v_bi=params["vbi"],
            n_eff=doping,
        )

    # ========================================================
    # CREATE GUI LEAKAGE MODEL
    # ========================================================

    def create_leakage_model(
        self,
        params,
    ):

        return LeakageCurrent(
            alpha=params["alpha"]
        )

    # ========================================================
    # TEMPERATURE FACTOR
    # ========================================================

    @staticmethod
    def temperature_factor(
        temperature,
    ):

        return temperature_factor(
            temperature
        )

    # ========================================================
    # GUI LEAKAGE CALCULATION
    # ========================================================

    def calculate_leakage(
        self,
        leakage_model,
        fluence,
        area,
        width,
        temperature,
    ):

        return calculate_leakage(
            leakage_model=leakage_model,
            fluence=fluence,
            area=area,
            width=width,
            temperature=temperature,
        )

    # ========================================================
    # GUI RUN SIMULATION
    # ========================================================

    def run_simulation(
        self,
        params,
    ):

        detector = self.create_detector(
            params
        )

        leakage_model = self.create_leakage_model(
            params
        )

        voltage = np.arange(
            params["vmin"],
            params["vmax"]
            + params["vstep"] * 0.5,
            params["vstep"],
        )

        voltage = voltage[
            voltage <=
            params["vmax"] + 1e-12
        ]

        if len(voltage) < 2:
            raise ValueError(
                "Voltage range must contain at least "
                "two voltage points."
            )

        width = detector.depletion_width(
            voltage
        )

        capacitance = detector.capacitance(
            width
        )

        leakage = self.calculate_leakage(
            leakage_model=leakage_model,
            fluence=params["final_fluence"],
            area=params["area"],
            width=width,
            temperature=params["temperature"],
        )

        return {
            "voltage": np.asarray(
                voltage,
                dtype=float,
            ),

            "width": np.asarray(
                width,
                dtype=float,
            ),

            "capacitance": np.asarray(
                capacitance,
                dtype=float,
            ),

            "leakage": np.asarray(
                leakage,
                dtype=float,
            ),

            "detector": detector,

            "leakage_model": leakage_model,

            "parameters": params,
        }