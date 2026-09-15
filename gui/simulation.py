import csv
import inspect
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import config
from constants import K_B_EV, EG_SI, T_REF_K
from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent


class SimulationMixin:
    def read_parameters(

            self

        ):



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

                )

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

                    "Maximum voltage must be greater than minimum voltage."

                )



            if parameters["vstep"] <= 0:

                raise ValueError(

                    "Voltage step must be greater than zero."

                )



            return parameters


    @staticmethod

    def _validate_sweep(initial, final, steps, name):

            if initial <= 0 or final <= 0:

                raise ValueError(

                    f"{name} initial and final values must be greater than zero."

                )



            if final < initial:

                raise ValueError(

                    f"{name} final value must be greater than or equal to "

                    f"the initial value."

                )



            if steps < 2:

                raise ValueError(

                    f"{name} steps must be at least 2."

                )



    def get_doping_study_values(self):

            try:

                initial = float(self.doping_initial_var.get())

                final = float(self.doping_final_var.get())

                steps = int(self.doping_steps_var.get())

            except ValueError as error:

                raise ValueError(

                    "Initial doping, final doping and steps must be valid values."

                ) from error



            self._validate_sweep(

                initial,

                final,

                steps,

                "Doping"

            )



            # Doping is normally compared on a logarithmic scale.

            return np.geomspace(

                initial,

                final,

                steps

            )



    def get_thickness_study_values(self):

            try:

                initial = float(self.thickness_initial_var.get())

                final = float(self.thickness_final_var.get())

                steps = int(self.thickness_steps_var.get())

            except ValueError as error:

                raise ValueError(

                    "Initial thickness, final thickness and steps must be "

                    "valid values."

                ) from error



            self._validate_sweep(

                initial,

                final,

                steps,

                "Thickness"

            )



            return np.linspace(

                initial,

                final,

                steps

            )



    def get_temperature_study_values(self):

            try:

                initial = float(self.temperature_initial_var.get())

                final = float(self.temperature_final_var.get())

                steps = int(self.temperature_steps_var.get())

            except ValueError as error:

                raise ValueError(

                    "Initial temperature, final temperature and steps "

                    "must be valid values."

                ) from error



            self._validate_sweep(

                initial,

                final,

                steps,

                "Temperature"

            )



            return np.linspace(

                initial,

                final,

                steps

            )



    def refresh_comparison_controls(self):

            # The entire comparison section is controlled by one

            # checkbox: "Compare Values".

            self.study_box.pack_forget()



            comparison_enabled = self.compare_values_var.get()



            if comparison_enabled:

                # Comparison Values remains before the graph-related controls.

                self.study_box.pack(

                    before=self.button_box,

                    fill="x",

                    pady=5

                )



            options = ["Empty"] + list(self.BASE_GRAPH_OPTIONS)



            if comparison_enabled:

                options.extend(self.DOPING_GRAPH_OPTIONS)

                options.extend(self.THICKNESS_GRAPH_OPTIONS)

                options.extend(self.TEMPERATURE_GRAPH_OPTIONS)



            # Update all four dropdowns independently.

            for index, combo in enumerate(self.graph_combos):

                current_graph = self.graph_vars[index].get()

                combo["values"] = options



                if index == 0:

                    if current_graph not in options or current_graph == "Empty":

                        self.graph_vars[index].set(self.BASE_GRAPH_OPTIONS[0])

                else:

                    if current_graph not in options:

                        self.graph_vars[index].set("Empty")



            # Redraw immediately after enabling/disabling Compare Values.

            self.update_graph(show_errors=False)



    def create_detector(

            self,

            params,

            thickness=None,

            doping=None,

            area=None

        ):



            if thickness is None:

                thickness = params["thickness"]



            if doping is None:

                doping = params["doping"]



            if area is None:

                area = params["area"]



            silicon = Silicon()



            detector = Detector(



                material=silicon,



                thickness_um=thickness,



                area_cm2=area,



                v_bi=params["vbi"],



                n_eff=doping

            )



            return detector



    def create_leakage_model(

            self,

            params

        ):



            return LeakageCurrent(

                alpha=params["alpha"]

            )



    def temperature_factor(

            temperature

        ):



            return (



                (

                    temperature

                    / T_REF_K

                ) ** 2



                *



                np.exp(



                    (

                        -EG_SI

                        /

                        (

                            2.0

                            * K_B_EV

                        )

                    )



                    *



                    (

                        1.0 / temperature

                        - 1.0 / T_REF_K

                    )

                )

            )



    def calculate_leakage(

            self,

            leakage_model,

            fluence,

            area,

            width,

            temperature

        ):



            # ----------------------------------------------------

            # Try the temperature-aware leakage model first.

            # ----------------------------------------------------



            try:



                signature = inspect.signature(

                    leakage_model.calculate

                )



                if "temperature_k" in signature.parameters:



                    return leakage_model.calculate(



                        fluence=fluence,



                        area_cm2=area,



                        thickness_cm=width,



                        temperature_k=temperature

                    )



            except (

                TypeError,

                ValueError

            ):



                pass



            # ----------------------------------------------------

            # Compatibility with older LeakageCurrent class.

            #

            # Older model:

            #

            # I = alpha × fluence × volume

            #

            # ----------------------------------------------------



            reference_current = leakage_model.calculate(



                fluence=fluence,



                area_cm2=area,



                thickness_cm=width

            )



            # Apply temperature dependence here when the older

            # leakage-current class is being used.

            factor = self.temperature_factor(

                temperature

            )



            return (

                np.asarray(

                    reference_current,

                    dtype=float

                )

                * factor

            )



    def run_simulation(

            self,

            params

        ):



            detector = self.create_detector(

                params

            )



            leakage_model = self.create_leakage_model(

                params

            )



            # ----------------------------------------------------

            # Reverse-bias voltage

            # ----------------------------------------------------



            voltage = np.arange(



                params["vmin"],



                params["vmax"]

                + params["vstep"] * 0.5,



                params["vstep"]

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



            # ----------------------------------------------------

            # Depletion width

            # ----------------------------------------------------



            width = detector.depletion_width(

                voltage

            )



            # ----------------------------------------------------

            # Capacitance

            # ----------------------------------------------------



            capacitance = detector.capacitance(

                width

            )



            # ----------------------------------------------------

            # Leakage current

            # ----------------------------------------------------



            leakage = self.calculate_leakage(



                leakage_model=leakage_model,



                fluence=params["final_fluence"],



                area=params["area"],



                width=width,



                temperature=params["temperature"]

            )



            return {



                "voltage": np.asarray(

                    voltage,

                    dtype=float

                ),



                "width": np.asarray(

                    width,

                    dtype=float

                ),



                "capacitance": np.asarray(

                    capacitance,

                    dtype=float

                ),



                "leakage": np.asarray(

                    leakage,

                    dtype=float

                ),



                "detector": detector,



                "leakage_model": leakage_model,



                "parameters": params

            }



    def update_results(

            self,

            result

        ):



            detector = result["detector"]



            self.vfd_var.set(

                f"{detector.full_depletion_voltage():.3f} V"

            )



            self.width_var.set(

                f"{result['width'][-1] * 1e4:.3f} µm"

            )



            self.capacitance_var.set(

                f"{result['capacitance'][-1] * 1e12:.4f} pF"

            )



            self.current_var.set(

                f"{result['leakage'][-1] * 1e3:.6g} mA"

            )



    def reset_parameters(

            self

        ):



            self.thickness_var.set(

                str(config.THICKNESS_UM)

            )



            self.area_var.set(

                str(config.AREA_CM2)

            )



            self.doping_var.set(

                f"{config.N_EFF:.6g}"

            )



            self.vbi_var.set(

                str(config.V_BI)

            )



            self.temperature_var.set(

                str(config.TEMPERATURE_K)

            )



            self.initial_fluence_var.set(

                f"{config.INITIAL_FLUENCE:.6g}"

            )



            self.final_fluence_var.set(

                f"{config.FINAL_FLUENCE:.6g}"

            )



            self.alpha_var.set(

                f"{config.ALPHA:.6g}"

            )



            self.vmin_var.set(

                str(config.REVERSE_VOLTAGE_MIN)

            )



            self.vmax_var.set(

                str(config.REVERSE_VOLTAGE_MAX)

            )



            if hasattr(

                config,

                "REVERSE_VOLTAGE_STEP"

            ):



                self.vstep_var.set(

                    str(config.REVERSE_VOLTAGE_STEP)

                )



            # Reset the complete comparison section.

            self.compare_values_var.set(False)



            doping_values = config.DOPING_STUDY_VALUES



            self.doping_initial_var.set(

                f"{min(doping_values):.6g}"

            )



            self.doping_final_var.set(

                f"{max(doping_values):.6g}"

            )



            self.doping_steps_var.set(

                str(len(doping_values))

            )



            thickness_values = config.THICKNESS_STUDY_VALUES_UM



            self.thickness_initial_var.set(

                str(min(thickness_values))

            )



            self.thickness_final_var.set(

                str(max(thickness_values))

            )



            self.thickness_steps_var.set(

                str(len(thickness_values))

            )



            temperature_values = config.TEMPERATURE_STUDY_VALUES_K



            self.temperature_initial_var.set(

                str(temperature_values[0])

            )



            self.temperature_final_var.set(

                str(temperature_values[-1])

            )



            self.temperature_steps_var.set(

                str(len(temperature_values))

            )



            self.refresh_comparison_controls()



            for index, graph_var in enumerate(self.graph_vars):

                graph_var.set(

                    self.BASE_GRAPH_OPTIONS[0]

                    if index == 0

                    else "Empty"

                )



            self.update_graph()
