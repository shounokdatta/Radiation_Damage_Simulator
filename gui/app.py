# ============================================================
# RADIATION DAMAGE SIMULATOR - GUI
# ============================================================
#
# Interactive GUI for:
#
#   1. Capacitance vs Reverse Bias
#   2. Leakage Current vs Reverse Bias
#   3. Capacitance and Leakage Current vs Reverse Bias
#   4. Capacitance vs Doping
#   5. Leakage Current vs Doping
#   6. Capacitance vs Thickness
#   7. Leakage Current vs Thickness
#   8. Capacitance vs Temperature
#   9. Leakage Current vs Temperature
#
# IMPORTANT:
#
#   config.py = DEFAULT VALUES ONLY
#
#   GUI fields = CURRENT USER INPUT
#
#   UPDATE GRAPH = READ CURRENT INPUT -> RECALCULATE -> REDRAW
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import csv
import inspect
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

import numpy as np

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

import config

from constants import (
    K_B_EV,
    EG_SI,
    T_REF_K
)

from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent


# ============================================================
# MAIN GUI CLASS
# ============================================================

class RadiationDamageGUI:

    # ========================================================
    # GRAPH OPTIONS
    # ========================================================

    GRAPH_OPTIONS = [

        "Capacitance vs Reverse Bias",

        "Leakage Current vs Reverse Bias",

        "Capacitance and Leakage Current",

        "Capacitance vs Doping",

        "Leakage Current vs Doping",

        "Capacitance vs Thickness",

        "Leakage Current vs Thickness",

        "Capacitance vs Temperature",

        "Leakage Current vs Temperature"
    ]


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        root
    ):

        self.root = root

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        self.root.title(
            "Radiation Damage Simulator"
        )

        self.root.geometry(
            "1450x900"
        )

        self.root.minsize(
            1150,
            700
        )

        # ----------------------------------------------------
        # Internal state
        # ----------------------------------------------------

        self.last_result = None

        self.auto_update_job = None

        # ----------------------------------------------------
        # Create GUI variables
        # ----------------------------------------------------

        self.create_variables()

        # ----------------------------------------------------
        # Style
        # ----------------------------------------------------

        self.configure_style()

        # ----------------------------------------------------
        # Build interface
        # ----------------------------------------------------

        self.build_header()

        self.build_main_area()

        self.build_status_bar()

        # ----------------------------------------------------
        # Auto update bindings
        # ----------------------------------------------------

        self.bind_auto_update()

        # ----------------------------------------------------
        # Initial graph
        # ----------------------------------------------------

        self.root.after(
            100,
            lambda: self.update_graph(
                show_errors=False
            )
        )


    # ========================================================
    # GUI VARIABLES
    # ========================================================

    def create_variables(
        self
    ):

        # ----------------------------------------------------
        # Detector
        # ----------------------------------------------------

        self.thickness_var = tk.StringVar(
            value=str(
                config.THICKNESS_UM
            )
        )

        self.area_var = tk.StringVar(
            value=str(
                config.AREA_CM2
            )
        )

        self.doping_var = tk.StringVar(
            value=f"{config.N_EFF:.6g}"
        )

        self.vbi_var = tk.StringVar(
            value=str(
                config.V_BI
            )
        )

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        self.temperature_var = tk.StringVar(
            value=str(
                config.TEMPERATURE_K
            )
        )

        # ----------------------------------------------------
        # Radiation
        # ----------------------------------------------------

        self.initial_fluence_var = tk.StringVar(
            value=f"{config.INITIAL_FLUENCE:.6g}"
        )

        self.final_fluence_var = tk.StringVar(
            value=f"{config.FINAL_FLUENCE:.6g}"
        )

        self.alpha_var = tk.StringVar(
            value=f"{config.ALPHA:.6g}"
        )

        # ----------------------------------------------------
        # Reverse voltage
        # ----------------------------------------------------

        self.vmin_var = tk.StringVar(
            value=str(
                config.REVERSE_VOLTAGE_MIN
            )
        )

        self.vmax_var = tk.StringVar(
            value=str(
                config.REVERSE_VOLTAGE_MAX
            )
        )

        # ----------------------------------------------------
        # Voltage step
        #
        # Supports old config files without
        # REVERSE_VOLTAGE_STEP.
        # ----------------------------------------------------

        if hasattr(
            config,
            "REVERSE_VOLTAGE_STEP"
        ):

            voltage_step = (
                config.REVERSE_VOLTAGE_STEP
            )

        else:

            voltage_step = (
                (
                    config.REVERSE_VOLTAGE_MAX
                    - config.REVERSE_VOLTAGE_MIN
                )
                /
                max(
                    getattr(
                        config,
                        "REVERSE_VOLTAGE_POINTS",
                        101
                    ) - 1,
                    1
                )
            )

        self.vstep_var = tk.StringVar(
            value=str(
                voltage_step
            )
        )

        # ----------------------------------------------------
        # Comparison values
        # ----------------------------------------------------

        self.doping_study_var = tk.StringVar(
            value=", ".join(
                f"{value:.6g}"
                for value in
                config.DOPING_STUDY_VALUES
            )
        )

        self.thickness_study_var = tk.StringVar(
            value=", ".join(
                str(value)
                for value in
                config.THICKNESS_STUDY_VALUES_UM
            )
        )

        self.temperature_study_var = tk.StringVar(
            value=", ".join(
                str(value)
                for value in
                config.TEMPERATURE_STUDY_VALUES_K
            )
        )

        # ----------------------------------------------------
        # Selected graph
        # ----------------------------------------------------

        self.graph_var = tk.StringVar(
            value=self.GRAPH_OPTIONS[0]
        )

        # ----------------------------------------------------
        # Automatic update
        # ----------------------------------------------------

        self.auto_update_var = tk.BooleanVar(
            value=False
        )

        # ----------------------------------------------------
        # Result fields
        # ----------------------------------------------------

        self.vfd_var = tk.StringVar(
            value="-"
        )

        self.width_var = tk.StringVar(
            value="-"
        )

        self.capacitance_var = tk.StringVar(
            value="-"
        )

        self.current_var = tk.StringVar(
            value="-"
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_var = tk.StringVar(
            value="Ready"
        )


    # ========================================================
    # STYLE
    # ========================================================

    def configure_style(
        self
    ):

        style = ttk.Style()

        try:

            style.theme_use(
                "clam"
            )

        except tk.TclError:

            pass

        style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                19,
                "bold"
            )
        )

        style.configure(
            "Run.TButton",
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )

        style.configure(
            "Result.TLabel",
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )


    # ========================================================
    # HEADER
    # ========================================================

    def build_header(
        self
    ):

        header = ttk.Frame(
            self.root,
            padding=(
                15,
                10
            )
        )

        header.pack(
            fill="x"
        )

        ttk.Label(
            header,
            text="RADIATION DAMAGE SIMULATOR",
            style="Title.TLabel"
        ).pack(
            side="left"
        )

        ttk.Label(
            header,
            textvariable=self.status_var
        ).pack(
            side="right"
        )


    # ========================================================
    # MAIN AREA
    # ========================================================

    def build_main_area(
        self
    ):

        paned = ttk.Panedwindow(
            self.root,
            orient="horizontal"
        )

        paned.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # ----------------------------------------------------
        # Left panel
        # ----------------------------------------------------

        left = ttk.Frame(
            paned,
            width=390,
            padding=8
        )

        # ----------------------------------------------------
        # Right panel
        # ----------------------------------------------------

        right = ttk.Frame(
            paned,
            padding=8
        )

        paned.add(
            left,
            weight=0
        )

        paned.add(
            right,
            weight=1
        )

        self.build_input_panel(
            left
        )

        self.build_graph_panel(
            right
        )


    # ========================================================
    # INPUT PANEL
    # ========================================================

    def build_input_panel(
        self,
        parent
    ):

        outer = ttk.LabelFrame(
            parent,
            text="Simulation Parameters",
            padding=8
        )

        outer.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # Scrollable canvas
        # ----------------------------------------------------

        canvas = tk.Canvas(
            outer,
            highlightthickness=0,
            borderwidth=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )

        content = ttk.Frame(
            canvas
        )

        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        # ----------------------------------------------------
        # Update scroll area
        # ----------------------------------------------------

        def update_scroll_region(
            event=None
        ):

            canvas.configure(
                scrollregion=canvas.bbox(
                    "all"
                )
            )

        content.bind(
            "<Configure>",
            update_scroll_region
        )

        # ----------------------------------------------------
        # Match content width
        # ----------------------------------------------------

        def resize_content(
            event
        ):

            canvas.itemconfigure(
                window_id,
                width=event.width
            )

        canvas.bind(
            "<Configure>",
            resize_content
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # ====================================================
        # MOUSE WHEEL
        # ====================================================

        def mouse_wheel(
            event
        ):

            if event.delta:

                canvas.yview_scroll(
                    int(
                        -event.delta / 120
                    ),
                    "units"
                )

        def enter_panel(
            event
        ):

            canvas.bind_all(
                "<MouseWheel>",
                mouse_wheel
            )

        def leave_panel(
            event
        ):

            canvas.unbind_all(
                "<MouseWheel>"
            )

        outer.bind(
            "<Enter>",
            enter_panel
        )

        outer.bind(
            "<Leave>",
            leave_panel
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ====================================================
        # DETECTOR
        # ====================================================

        detector_box = ttk.LabelFrame(
            content,
            text="Detector",
            padding=8
        )

        detector_box.pack(
            fill="x",
            pady=5
        )

        self.add_entry(
            detector_box,
            "Thickness (µm)",
            self.thickness_var
        )

        self.add_entry(
            detector_box,
            "Area (cm²)",
            self.area_var
        )

        self.add_entry(
            detector_box,
            "Doping (cm⁻³)",
            self.doping_var
        )

        self.add_entry(
            detector_box,
            "Built-in voltage (V)",
            self.vbi_var
        )

        # ====================================================
        # RADIATION
        # ====================================================

        radiation_box = ttk.LabelFrame(
            content,
            text="Radiation",
            padding=8
        )

        radiation_box.pack(
            fill="x",
            pady=5
        )

        self.add_entry(
            radiation_box,
            "Initial fluence",
            self.initial_fluence_var
        )

        self.add_entry(
            radiation_box,
            "Final fluence",
            self.final_fluence_var
        )

        self.add_entry(
            radiation_box,
            "Alpha (A/cm)",
            self.alpha_var
        )

        # ====================================================
        # TEMPERATURE
        # ====================================================

        temperature_box = ttk.LabelFrame(
            content,
            text="Operating Temperature",
            padding=8
        )

        temperature_box.pack(
            fill="x",
            pady=5
        )

        self.add_entry(
            temperature_box,
            "Temperature (K)",
            self.temperature_var
        )

        # ====================================================
        # REVERSE BIAS
        # ====================================================

        voltage_box = ttk.LabelFrame(
            content,
            text="Reverse Bias Sweep",
            padding=8
        )

        voltage_box.pack(
            fill="x",
            pady=5
        )

        self.add_entry(
            voltage_box,
            "Minimum voltage (V)",
            self.vmin_var
        )

        self.add_entry(
            voltage_box,
            "Maximum voltage (V)",
            self.vmax_var
        )

        self.add_entry(
            voltage_box,
            "Voltage step (V)",
            self.vstep_var
        )

        # ====================================================
        # COMPARISON VALUES
        # ====================================================

        study_box = ttk.LabelFrame(
            content,
            text="Comparison Values",
            padding=8
        )

        study_box.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            study_box,
            text="Doping values:"
        ).pack(
            anchor="w"
        )

        ttk.Entry(
            study_box,
            textvariable=self.doping_study_var
        ).pack(
            fill="x",
            pady=(2, 6)
        )

        ttk.Label(
            study_box,
            text="Thickness values (µm):"
        ).pack(
            anchor="w"
        )

        ttk.Entry(
            study_box,
            textvariable=self.thickness_study_var
        ).pack(
            fill="x",
            pady=(2, 6)
        )

        ttk.Label(
            study_box,
            text="Temperature values (K):"
        ).pack(
            anchor="w"
        )

        ttk.Entry(
            study_box,
            textvariable=self.temperature_study_var
        ).pack(
            fill="x"
        )

        # ====================================================
        # GRAPH SELECTION
        # ====================================================

        graph_box = ttk.LabelFrame(
            content,
            text="Graph Selection",
            padding=8
        )

        graph_box.pack(
            fill="x",
            pady=5
        )

        self.graph_combo = ttk.Combobox(
            graph_box,
            textvariable=self.graph_var,
            values=self.GRAPH_OPTIONS,
            state="readonly"
        )

        self.graph_combo.pack(
            fill="x"
        )

        self.graph_combo.bind(
            "<<ComboboxSelected>>",
            lambda event:
            self.update_graph()
        )

        ttk.Checkbutton(
            graph_box,
            text="Auto update while editing",
            variable=self.auto_update_var
        ).pack(
            anchor="w",
            pady=5
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        button_box = ttk.Frame(
            content
        )

        button_box.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            button_box,
            text="UPDATE GRAPH",
            style="Run.TButton",
            command=self.update_graph
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            button_box,
            text="RESET DEFAULTS",
            command=self.reset_parameters
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            button_box,
            text="SAVE GRAPH",
            command=self.save_graph
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            button_box,
            text="EXPORT CSV",
            command=self.export_csv
        ).pack(
            fill="x",
            pady=3
        )

        # ====================================================
        # RESULTS
        # ====================================================

        result_box = ttk.LabelFrame(
            content,
            text="Simulation Results",
            padding=8
        )

        result_box.pack(
            fill="x",
            pady=5
        )

        self.add_result(
            result_box,
            "Full depletion voltage",
            self.vfd_var
        )

        self.add_result(
            result_box,
            "Depletion width",
            self.width_var
        )

        self.add_result(
            result_box,
            "Capacitance",
            self.capacitance_var
        )

        self.add_result(
            result_box,
            "Leakage current",
            self.current_var
        )


    # ========================================================
    # ENTRY FIELD
    # ========================================================

    def add_entry(
        self,
        parent,
        label,
        variable
    ):

        row = ttk.Frame(
            parent
        )

        row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            row,
            text=label
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        entry = ttk.Entry(
            row,
            textvariable=variable,
            width=15
        )

        entry.pack(
            side="right"
        )

        entry.bind(
            "<Return>",
            lambda event:
            self.update_graph()
        )


    # ========================================================
    # RESULT FIELD
    # ========================================================

    def add_result(
        self,
        parent,
        label,
        variable
    ):

        row = ttk.Frame(
            parent
        )

        row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            row,
            text=label
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            row,
            textvariable=variable,
            style="Result.TLabel"
        ).pack(
            side="right"
        )


    # ========================================================
    # GRAPH PANEL
    # ========================================================

    def build_graph_panel(
        self,
        parent
    ):

        graph_box = ttk.LabelFrame(
            parent,
            text="Simulation Graph",
            padding=8
        )

        graph_box.pack(
            fill="both",
            expand=True
        )

        self.figure = Figure(
            figsize=(8, 5),
            dpi=100
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=graph_box
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            graph_box,
            pack_toolbar=False
        )

        self.toolbar.update()

        self.toolbar.pack(
            fill="x"
        )


    # ========================================================
    # STATUS BAR
    # ========================================================

    def build_status_bar(
        self
    ):

        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=5
        ).pack(
            fill="x"
        )


    # ========================================================
    # AUTO UPDATE
    # ========================================================

    def bind_auto_update(
        self
    ):

        variables = [

            self.thickness_var,

            self.area_var,

            self.doping_var,

            self.vbi_var,

            self.temperature_var,

            self.initial_fluence_var,

            self.final_fluence_var,

            self.alpha_var,

            self.vmin_var,

            self.vmax_var,

            self.vstep_var,

            self.doping_study_var,

            self.thickness_study_var,

            self.temperature_study_var
        ]

        for variable in variables:

            variable.trace_add(
                "write",
                self.schedule_auto_update
            )


    def schedule_auto_update(
        self,
        *_args
    ):

        if not self.auto_update_var.get():

            return

        if self.auto_update_job is not None:

            try:

                self.root.after_cancel(
                    self.auto_update_job
                )

            except tk.TclError:

                pass

        self.auto_update_job = self.root.after(
            500,
            lambda:
            self.update_graph(
                show_errors=False
            )
        )


    # ========================================================
    # READ CURRENT GUI VALUES
    # ========================================================

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


    # ========================================================
    # PARSE COMPARISON VALUES
    # ========================================================

    @staticmethod
    def parse_values(
        text,
        name
    ):

        try:

            values = [

                float(value.strip())

                for value in text.split(",")

                if value.strip()
            ]

        except ValueError as error:

            raise ValueError(
                f"{name} contains an invalid number."
            ) from error

        if not values:

            raise ValueError(
                f"Enter at least one {name} value."
            )

        if any(
            value <= 0
            for value in values
        ):

            raise ValueError(
                f"All {name} values must be greater than zero."
            )

        return values


    # ========================================================
    # CREATE DETECTOR
    # ========================================================

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


    # ========================================================
    # CREATE LEAKAGE MODEL
    # ========================================================

    def create_leakage_model(
        self,
        params
    ):

        return LeakageCurrent(
            alpha=params["alpha"]
        )


    # ========================================================
    # CALCULATE TEMPERATURE FACTOR
    # ========================================================

    @staticmethod
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


    # ========================================================
    # CALCULATE LEAKAGE CURRENT
    # ========================================================

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


    # ========================================================
    # RUN CURRENT SIMULATION
    # ========================================================

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


    # ========================================================
    # UPDATE GRAPH
    # ========================================================

    def update_graph(
        self,
        show_errors=True
    ):

        try:

            # ------------------------------------------------
            # VERY IMPORTANT:
            #
            # Read the current values from the GUI fields.
            # ------------------------------------------------

            params = self.read_parameters()

            # ------------------------------------------------
            # Recalculate everything.
            # ------------------------------------------------

            result = self.run_simulation(
                params
            )

            self.last_result = result

            graph_name = self.graph_var.get()

            # ------------------------------------------------
            # Completely clear previous figure
            # ------------------------------------------------

            self.figure.clear()

            # ------------------------------------------------
            # Draw selected graph
            # ------------------------------------------------

            if graph_name == (
                "Capacitance vs Reverse Bias"
            ):

                self.draw_basic_capacitance(
                    result
                )

            elif graph_name == (
                "Leakage Current vs Reverse Bias"
            ):

                self.draw_basic_leakage(
                    result
                )

            elif graph_name == (
                "Capacitance and Leakage Current"
            ):

                self.draw_combined(
                    result
                )

            elif graph_name == (
                "Capacitance vs Doping"
            ):

                values = self.parse_values(
                    self.doping_study_var.get(),
                    "Doping"
                )

                self.draw_doping_capacitance(
                    result,
                    values
                )

            elif graph_name == (
                "Leakage Current vs Doping"
            ):

                values = self.parse_values(
                    self.doping_study_var.get(),
                    "Doping"
                )

                self.draw_doping_leakage(
                    result,
                    values,
                    params
                )

            elif graph_name == (
                "Capacitance vs Thickness"
            ):

                values = self.parse_values(
                    self.thickness_study_var.get(),
                    "Thickness"
                )

                self.draw_thickness_capacitance(
                    result,
                    values,
                    params
                )

            elif graph_name == (
                "Leakage Current vs Thickness"
            ):

                values = self.parse_values(
                    self.thickness_study_var.get(),
                    "Thickness"
                )

                self.draw_thickness_leakage(
                    result,
                    values,
                    params
                )

            elif graph_name == (
                "Capacitance vs Temperature"
            ):

                values = self.parse_values(
                    self.temperature_study_var.get(),
                    "Temperature"
                )

                self.draw_temperature_capacitance(
                    result,
                    values
                )

            elif graph_name == (
                "Leakage Current vs Temperature"
            ):

                values = self.parse_values(
                    self.temperature_study_var.get(),
                    "Temperature"
                )

                self.draw_temperature_leakage(
                    result,
                    values,
                    params
                )

            # ------------------------------------------------
            # Redraw
            # ------------------------------------------------

            self.figure.tight_layout()

            self.canvas.draw()

            self.canvas.flush_events()

            # ------------------------------------------------
            # Update values
            # ------------------------------------------------

            self.update_results(
                result
            )

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            self.status_var.set(
                f"Updated: {graph_name}"
            )

        except Exception as error:

            self.status_var.set(
                f"Error: {error}"
            )

            if show_errors:

                messagebox.showerror(
                    "Simulation Error",
                    str(error)
                )


    # ========================================================
    # AXIS FORMAT
    # ========================================================

    @staticmethod
    def style_axis(
        ax,
        title,
        ylabel
    ):

        ax.set_title(
            title,
            fontsize=14
        )

        ax.set_xlabel(
            "Reverse Bias Voltage (V)",
            fontsize=12
        )

        ax.set_ylabel(
            ylabel,
            fontsize=12
        )

        ax.tick_params(
            labelsize=10
        )

        ax.grid(
            True,
            linestyle="--",
            alpha=0.3
        )


    # ========================================================
    # GRAPH 1
    # ========================================================

    def draw_basic_capacitance(
        self,
        result
    ):

        ax = self.figure.add_subplot(
            111
        )

        ax.plot(

            result["voltage"],

            result["capacitance"] * 1e12,

            linewidth=2.5
        )

        self.style_axis(

            ax,

            "Capacitance vs Reverse Bias Voltage",

            "Capacitance (pF)"
        )


    # ========================================================
    # GRAPH 2
    # ========================================================

    def draw_basic_leakage(
        self,
        result
    ):

        ax = self.figure.add_subplot(
            111
        )

        ax.plot(

            result["voltage"],

            result["leakage"] * 1e3,

            linewidth=2.5
        )

        self.style_axis(

            ax,

            "Leakage Current vs Reverse Bias Voltage",

            "Leakage Current (mA)"
        )


    # ========================================================
    # GRAPH 3
    # ========================================================

    def draw_combined(
        self,
        result
    ):

        ax1 = self.figure.add_subplot(
            111
        )

        ax2 = ax1.twinx()

        line1 = ax1.plot(

            result["voltage"],

            result["capacitance"] * 1e12,

            linewidth=2.5,

            label="Capacitance"
        )

        line2 = ax2.plot(

            result["voltage"],

            result["leakage"] * 1e3,

            linewidth=2.5,

            label="Leakage Current"
        )

        ax1.set_xlabel(
            "Reverse Bias Voltage (V)",
            fontsize=12
        )

        ax1.set_ylabel(
            "Capacitance (pF)",
            fontsize=12
        )

        ax2.set_ylabel(
            "Leakage Current (mA)",
            fontsize=12
        )

        ax1.set_title(
            "Capacitance and Leakage Current\n"
            "vs Reverse Bias Voltage",
            fontsize=14
        )

        ax1.grid(
            True,
            linestyle="--",
            alpha=0.3
        )

        lines = line1 + line2

        ax1.legend(

            lines,

            [
                line.get_label()
                for line in lines
            ],

            loc="best"
        )


    # ========================================================
    # GRAPH 4
    # ========================================================

    def draw_doping_capacitance(
        self,
        result,
        values
    ):

        ax = self.figure.add_subplot(
            111
        )

        for doping in values:

            width = (
                result["detector"]
                .depletion_width_for_doping(
                    result["voltage"],
                    doping
                )
            )

            capacitance = (
                result["detector"]
                .capacitance(
                    width
                )
            )

            ax.plot(

                result["voltage"],

                capacitance * 1e12,

                linewidth=2,

                label=f"{doping:.1e} cm⁻³"
            )

        self.style_axis(

            ax,

            "Capacitance vs Reverse Bias\n"
            "for Different Doping Concentrations",

            "Capacitance (pF)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # GRAPH 5
    # ========================================================

    def draw_doping_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(
            111
        )

        for doping in values:

            width = (
                result["detector"]
                .depletion_width_for_doping(
                    result["voltage"],
                    doping
                )
            )

            leakage = self.calculate_leakage(

                leakage_model=
                result["leakage_model"],

                fluence=
                params["final_fluence"],

                area=
                params["area"],

                width=
                width,

                temperature=
                params["temperature"]
            )

            ax.plot(

                result["voltage"],

                leakage * 1e3,

                linewidth=2,

                label=f"{doping:.1e} cm⁻³"
            )

        self.style_axis(

            ax,

            "Leakage Current vs Reverse Bias\n"
            "for Different Doping Concentrations",

            "Leakage Current (mA)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # GRAPH 6
    # ========================================================

    def draw_thickness_capacitance(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(
            111
        )

        for thickness in values:

            detector = self.create_detector(

                params,

                thickness=thickness
            )

            width = detector.depletion_width(
                result["voltage"]
            )

            capacitance = detector.capacitance(
                width
            )

            ax.plot(

                result["voltage"],

                capacitance * 1e12,

                linewidth=2,

                label=f"{thickness:g} µm"
            )

        self.style_axis(

            ax,

            "Capacitance vs Reverse Bias\n"
            "for Different Detector Thicknesses",

            "Capacitance (pF)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # GRAPH 7
    # ========================================================

    def draw_thickness_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(
            111
        )

        for thickness in values:

            detector = self.create_detector(

                params,

                thickness=thickness
            )

            width = detector.depletion_width(
                result["voltage"]
            )

            leakage = self.calculate_leakage(

                leakage_model=
                result["leakage_model"],

                fluence=
                params["final_fluence"],

                area=
                params["area"],

                width=
                width,

                temperature=
                params["temperature"]
            )

            ax.plot(

                result["voltage"],

                leakage * 1e3,

                linewidth=2,

                label=f"{thickness:g} µm"
            )

        self.style_axis(

            ax,

            "Leakage Current vs Reverse Bias\n"
            "for Different Detector Thicknesses",

            "Leakage Current (mA)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # GRAPH 8
    # ========================================================

    def draw_temperature_capacitance(
        self,
        result,
        values
    ):

        ax = self.figure.add_subplot(
            111
        )

        for temperature in values:

            # ------------------------------------------------
            # In the current detector model, capacitance is
            # independent of temperature.
            # ------------------------------------------------

            ax.plot(

                result["voltage"],

                result["capacitance"] * 1e12,

                linewidth=2,

                label=(
                    f"{temperature:.2f} K "
                    f"({temperature - 273.15:.1f} °C)"
                )
            )

        self.style_axis(

            ax,

            "Capacitance vs Reverse Bias\n"
            "for Different Operating Temperatures",

            "Capacitance (pF)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # GRAPH 9
    # ========================================================

    def draw_temperature_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(
            111
        )

        for temperature in values:

            leakage = self.calculate_leakage(

                leakage_model=
                result["leakage_model"],

                fluence=
                params["final_fluence"],

                area=
                params["area"],

                width=
                result["width"],

                temperature=
                temperature
            )

            ax.plot(

                result["voltage"],

                leakage * 1e3,

                linewidth=2,

                label=(
                    f"{temperature:.2f} K "
                    f"({temperature - 273.15:.1f} °C)"
                )
            )

        self.style_axis(

            ax,

            "Leakage Current vs Reverse Bias\n"
            "for Different Operating Temperatures",

            "Leakage Current (mA)"
        )

        ax.legend(
            fontsize=8
        )


    # ========================================================
    # UPDATE RESULT VALUES
    # ========================================================

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


    # ========================================================
    # RESET DEFAULTS
    # ========================================================

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

        self.doping_study_var.set(
            ", ".join(
                f"{value:.6g}"
                for value in
                config.DOPING_STUDY_VALUES
            )
        )

        self.thickness_study_var.set(
            ", ".join(
                str(value)
                for value in
                config.THICKNESS_STUDY_VALUES_UM
            )
        )

        self.temperature_study_var.set(
            ", ".join(
                str(value)
                for value in
                config.TEMPERATURE_STUDY_VALUES_K
            )
        )

        self.graph_var.set(
            self.GRAPH_OPTIONS[0]
        )

        self.update_graph()


    # ========================================================
    # SAVE GRAPH
    # ========================================================

    def save_graph(
        self
    ):

        folder = (

            Path(__file__)
            .resolve()
            .parents[1]
            / "output"
            / "graphs"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        path = filedialog.asksaveasfilename(

            initialdir=folder,

            initialfile=
            "radiation_damage_graph.png",

            defaultextension=".png",

            filetypes=[

                (
                    "PNG image",
                    "*.png"
                ),

                (
                    "PDF",
                    "*.pdf"
                ),

                (
                    "SVG",
                    "*.svg"
                )
            ]
        )

        if not path:
            return

        self.figure.savefig(

            path,

            dpi=300,

            bbox_inches="tight"
        )

        self.status_var.set(
            f"Graph saved: {path}"
        )


    # ========================================================
    # EXPORT CSV
    # ========================================================

    def export_csv(
        self
    ):

        if self.last_result is None:

            messagebox.showwarning(

                "No Data",

                "Run the simulation first."
            )

            return

        folder = (

            Path(__file__)
            .resolve()
            .parents[1]
            / "output"
            / "data"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        path = filedialog.asksaveasfilename(

            initialdir=folder,

            initialfile="simulation.csv",

            defaultextension=".csv",

            filetypes=[
                (
                    "CSV files",
                    "*.csv"
                )
            ]
        )

        if not path:
            return

        result = self.last_result

        with open(

            path,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow([

                "Reverse Bias (V)",

                "Depletion Width (um)",

                "Capacitance (pF)",

                "Leakage Current (mA)"
            ])

            for voltage, width, capacitance, leakage in zip(

                result["voltage"],

                result["width"] * 1e4,

                result["capacitance"] * 1e12,

                result["leakage"] * 1e3

            ):

                writer.writerow([

                    voltage,

                    width,

                    capacitance,

                    leakage
                ])

        self.status_var.set(
            f"CSV saved: {path}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    RadiationDamageGUI(
        root
    )

    root.mainloop()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()