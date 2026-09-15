# ============================================================
# RADIATION DAMAGE SIMULATOR - GUI
# ============================================================
#
# Interactive GUI for:
#
#   1. Capacitance vs Reverse Bias
#   2. Leakage Current vs Reverse Bias
#   3. Capacitance and Leakage Current vs Reverse Bias
#   4. Capacitance vs Reverse Bias - Different Doping
#   5. Leakage Current vs Reverse Bias - Different Doping
#   6. Capacitance vs Reverse Bias - Additional/High-Resolution Doping
#   7. Leakage Current vs Reverse Bias - Additional/High-Resolution Doping
#   8. Capacitance vs Reverse Bias - Different Thickness
#   9. Leakage Current vs Reverse Bias - Different Thickness
#  10. Capacitance vs Reverse Bias - Different Temperature
#  11. Leakage Current vs Reverse Bias - Different Temperature
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
import sys
from pathlib import Path

# ------------------------------------------------------------
# Add the project root to Python's import path.
#
# This makes the GUI work both with:
#     python -m gui.app
# and with:
#     python gui/app.py
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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

    # The first three graphs are always available.
    BASE_GRAPH_OPTIONS = [
        "Capacitance vs Reverse Bias",
        "Leakage Current vs Reverse Bias",
        "Combined Capacitance & Leakage Current vs Reverse Bias"
    ]

    DOPING_GRAPH_OPTIONS = [
        "Capacitance vs Reverse Bias - Different Doping",
        "Leakage Current vs Reverse Bias - Different Doping",
        "Capacitance vs Reverse Bias - Additional/High-Resolution Doping",
        "Leakage Current vs Reverse Bias - Additional/High-Resolution Doping"
    ]

    THICKNESS_GRAPH_OPTIONS = [
        "Capacitance vs Reverse Bias - Different Thickness",
        "Leakage Current vs Reverse Bias - Different Thickness"
    ]

    TEMPERATURE_GRAPH_OPTIONS = [
        "Capacitance vs Reverse Bias - Different Temperature",
        "Leakage Current vs Reverse Bias - Different Temperature"
    ]

    # Kept as the complete list for reference.  The actual graph
    # dropdown is generated dynamically from the selected studies.
    GRAPH_OPTIONS = (
        BASE_GRAPH_OPTIONS
        + DOPING_GRAPH_OPTIONS
        + THICKNESS_GRAPH_OPTIONS
        + TEMPERATURE_GRAPH_OPTIONS
    )


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
        # One master checkbox controls the complete comparison
        # section.  When enabled, all comparison value controls
        # become available together.
        self.compare_values_var = tk.BooleanVar(
            value=False
        )

        # Doping concentration sweep
        self.doping_initial_var = tk.StringVar(
            value=f"{min(config.DOPING_STUDY_VALUES):.6g}"
        )

        self.doping_final_var = tk.StringVar(
            value=f"{max(config.DOPING_STUDY_VALUES):.6g}"
        )

        self.doping_steps_var = tk.StringVar(
            value=str(len(config.DOPING_STUDY_VALUES))
        )

        # Detector thickness sweep
        self.thickness_initial_var = tk.StringVar(
            value=str(min(config.THICKNESS_STUDY_VALUES_UM))
        )

        self.thickness_final_var = tk.StringVar(
            value=str(max(config.THICKNESS_STUDY_VALUES_UM))
        )

        self.thickness_steps_var = tk.StringVar(
            value=str(len(config.THICKNESS_STUDY_VALUES_UM))
        )

        # Temperature sweep
        temperature_values = config.TEMPERATURE_STUDY_VALUES_K

        self.temperature_initial_var = tk.StringVar(
            value=str(temperature_values[0])
        )

        self.temperature_final_var = tk.StringVar(
            value=str(temperature_values[-1])
        )

        self.temperature_steps_var = tk.StringVar(
            value=str(len(temperature_values))
        )

        # ----------------------------------------------------
        # Selected graph
        # ----------------------------------------------------

        self.graph_var = tk.StringVar(
            value=self.BASE_GRAPH_OPTIONS[0]
        )

        # Four independent graph selections.
        # Window 1 defaults to the first graph; the other windows start empty.
        self.graph_vars = [
            self.graph_var,
            tk.StringVar(value="Empty"),
            tk.StringVar(value="Empty"),
            tk.StringVar(value="Empty")
        ]

        self.graph_combos = []
        self.graph_figures = []
        self.graph_canvases = []
        self.graph_toolbars = []
        self.expanded_windows = {}

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

        # Initialize the unified comparison section after graph_combo exists.
        self.refresh_comparison_controls()



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

        # Master checkbox.  This is the only comparison tick mark.
        ttk.Checkbutton(
            content,
            text="Compare Values",
            variable=self.compare_values_var,
            command=self.refresh_comparison_controls
        ).pack(
            anchor="w",
            pady=(5, 2)
        )

        # One unified comparison section.  It is shown only when
        # "Compare Values" is checked.
        self.study_box = ttk.LabelFrame(
            content,
            text="Comparison Values",
            padding=8
        )

        # ----------------------------------------------------
        # DOPING
        # ----------------------------------------------------

        doping_row = ttk.Frame(
            self.study_box
        )
        doping_row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            doping_row,
            text="Doping Concentration (cm⁻³)"
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(0, 3)
        )

        ttk.Label(
            doping_row,
            text="Initial:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 3)
        )

        self.doping_initial_combo = ttk.Combobox(
            doping_row,
            textvariable=self.doping_initial_var,
            values=[
                f"{10 ** exponent:.0e}"
                for exponent in range(11, 16)
            ],
            state="readonly",
            width=12
        )
        self.doping_initial_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            doping_row,
            text="Final:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=(0, 3)
        )

        self.doping_final_combo = ttk.Combobox(
            doping_row,
            textvariable=self.doping_final_var,
            values=[
                f"{10 ** exponent:.0e}"
                for exponent in range(11, 16)
            ],
            state="readonly",
            width=12
        )
        self.doping_final_combo.grid(
            row=1,
            column=3,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            doping_row,
            text="Steps:"
        ).grid(
            row=1,
            column=4,
            sticky="w",
            padx=(0, 3)
        )

        self.doping_steps_combo = ttk.Combobox(
            doping_row,
            textvariable=self.doping_steps_var,
            values=[
                "2", "3", "4", "5", "6", "7", "8", "9", "10",
                "12", "15", "20"
            ],
            state="readonly",
            width=7
        )
        self.doping_steps_combo.grid(
            row=1,
            column=5,
            sticky="ew"
        )

        for column in (1, 3, 5):
            doping_row.columnconfigure(column, weight=1)

        # ----------------------------------------------------
        # THICKNESS
        # ----------------------------------------------------

        thickness_row = ttk.Frame(
            self.study_box
        )
        thickness_row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            thickness_row,
            text="Detector Thickness (µm)"
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(0, 3)
        )

        ttk.Label(
            thickness_row,
            text="Initial:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 3)
        )

        self.thickness_initial_combo = ttk.Combobox(
            thickness_row,
            textvariable=self.thickness_initial_var,
            values=[
                "25", "50", "75", "100", "150", "200",
                "250", "300", "400", "500", "750", "1000"
            ],
            state="readonly",
            width=12
        )
        self.thickness_initial_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            thickness_row,
            text="Final:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=(0, 3)
        )

        self.thickness_final_combo = ttk.Combobox(
            thickness_row,
            textvariable=self.thickness_final_var,
            values=[
                "25", "50", "75", "100", "150", "200",
                "250", "300", "400", "500", "750", "1000"
            ],
            state="readonly",
            width=12
        )
        self.thickness_final_combo.grid(
            row=1,
            column=3,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            thickness_row,
            text="Steps:"
        ).grid(
            row=1,
            column=4,
            sticky="w",
            padx=(0, 3)
        )

        self.thickness_steps_combo = ttk.Combobox(
            thickness_row,
            textvariable=self.thickness_steps_var,
            values=[
                "2", "3", "4", "5", "6", "7", "8", "9", "10",
                "12", "15", "20"
            ],
            state="readonly",
            width=7
        )
        self.thickness_steps_combo.grid(
            row=1,
            column=5,
            sticky="ew"
        )

        for column in (1, 3, 5):
            thickness_row.columnconfigure(column, weight=1)

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        temperature_row = ttk.Frame(
            self.study_box
        )
        temperature_row.pack(
            fill="x",
            pady=3
        )

        ttk.Label(
            temperature_row,
            text="Operating Temperature (K)"
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(0, 3)
        )

        temperature_values = [
            "233.15", "243.15", "253.15", "263.15",
            "273.15", "283.15", "293.15", "303.15",
            "313.15", "323.15", "333.15", "343.15",
            "353.15", "363.15", "373.15"
        ]

        ttk.Label(
            temperature_row,
            text="Initial:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 3)
        )

        self.temperature_initial_combo = ttk.Combobox(
            temperature_row,
            textvariable=self.temperature_initial_var,
            values=temperature_values,
            state="readonly",
            width=12
        )
        self.temperature_initial_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            temperature_row,
            text="Final:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=(0, 3)
        )

        self.temperature_final_combo = ttk.Combobox(
            temperature_row,
            textvariable=self.temperature_final_var,
            values=temperature_values,
            state="readonly",
            width=12
        )
        self.temperature_final_combo.grid(
            row=1,
            column=3,
            sticky="ew",
            padx=(0, 8)
        )

        ttk.Label(
            temperature_row,
            text="Steps:"
        ).grid(
            row=1,
            column=4,
            sticky="w",
            padx=(0, 3)
        )

        self.temperature_steps_combo = ttk.Combobox(
            temperature_row,
            textvariable=self.temperature_steps_var,
            values=[
                "2", "3", "4", "5", "6", "7", "8", "9", "10",
                "12", "15", "20"
            ],
            state="readonly",
            width=7
        )
        self.temperature_steps_combo.grid(
            row=1,
            column=5,
            sticky="ew"
        )

        for column in (1, 3, 5):
            temperature_row.columnconfigure(column, weight=1)

        # ====================================================
        # GRAPH SELECTION
        # ====================================================

        # Graphs are selected independently from the dropdown placed
        # directly underneath each graph in the 2x2 graph grid.
        ttk.Checkbutton(
            content,
            text="Auto update while editing",
            variable=self.auto_update_var
        ).pack(
            anchor="w",
            pady=5
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        self.button_box = ttk.Frame(
            content
        )

        self.button_box.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            self.button_box,
            text="UPDATE GRAPH",
            style="Run.TButton",
            command=self.update_graph
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            self.button_box,
            text="RESET DEFAULTS",
            command=self.reset_parameters
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            self.button_box,
            text="SAVE GRAPH",
            command=self.save_graph
        ).pack(
            fill="x",
            pady=3
        )

        ttk.Button(
            self.button_box,
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

        # 2 x 2 grid of independent graph windows.
        grid = ttk.Frame(graph_box)
        grid.pack(
            fill="both",
            expand=True
        )

        for row in range(2):
            grid.rowconfigure(row, weight=1)
        for column in range(2):
            grid.columnconfigure(column, weight=1)

        for index in range(4):
            cell = ttk.LabelFrame(
                grid,
                text=f"Graph {index + 1}",
                padding=5
            )
            cell.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=4,
                pady=4
            )
            cell.rowconfigure(1, weight=1)
            cell.columnconfigure(0, weight=1)

            # Small expand button in the top-right corner of each graph.
            expand_button = ttk.Button(
                cell,
                text="↗",
                width=3,
                command=lambda i=index: self.expand_graph(i)
            )
            expand_button.grid(
                row=0,
                column=0,
                sticky="e",
                padx=2,
                pady=(0, 2)
            )

            figure = Figure(
                figsize=(5, 3),
                dpi=100
            )

            canvas = FigureCanvasTkAgg(
                figure,
                master=cell
            )

            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(
                row=1,
                column=0,
                sticky="nsew"
            )

            combo = ttk.Combobox(
                cell,
                textvariable=self.graph_vars[index],
                state="readonly"
            )
            combo.grid(
                row=2,
                column=0,
                sticky="ew",
                pady=(5, 0)
            )

            combo.bind(
                "<<ComboboxSelected>>",
                lambda event, i=index: self.update_graph()
            )

            self.graph_figures.append(figure)
            self.graph_canvases.append(canvas)
            self.graph_combos.append(combo)

        # Keep the original single-graph attributes pointing to Graph 1
        # so the existing drawing functions continue to work unchanged.
        self.figure = self.graph_figures[0]
        self.canvas = self.graph_canvases[0]
        self.graph_var = self.graph_vars[0]

    # ========================================================
    # EXPANDED GRAPH WINDOW
    # ========================================================

    def expand_graph(self, index):
        """Open one graph in a large, detailed window."""

        existing = self.expanded_windows.get(index)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.focus_force()
                    return
            except tk.TclError:
                self.expanded_windows.pop(index, None)

        graph_name = self.graph_vars[index].get()

        if graph_name in ("", "Empty"):
            messagebox.showinfo(
                "No Graph Selected",
                f"Graph {index + 1} is empty. Select a graph first."
            )
            return

        if self.last_result is None:
            self.update_graph(show_errors=False)

        if self.last_result is None:
            return

        detail = tk.Toplevel(self.root)
        detail.title(f"Graph {index + 1} - {graph_name}")
        detail.geometry("1100x760")
        detail.minsize(850, 600)
        self.expanded_windows[index] = detail

        header = ttk.Frame(detail, padding=(12, 10, 12, 4))
        header.pack(fill="x")

        ttk.Label(
            header,
            text=f"Graph {index + 1}",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        detail_var = tk.StringVar(value=graph_name)
        detail_combo = ttk.Combobox(
            header,
            textvariable=detail_var,
            state="readonly",
            width=65
        )
        detail_combo.pack(side="right", fill="x", expand=True, padx=(20, 0))
        detail_combo["values"] = self.graph_combos[index]["values"]

        plot_frame = ttk.Frame(detail, padding=(12, 4, 12, 8))
        plot_frame.pack(fill="both", expand=True)

        figure = Figure(figsize=(10, 6), dpi=100)
        canvas = FigureCanvasTkAgg(figure, master=plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = ttk.Frame(detail)
        toolbar_frame.pack(fill="x", padx=12, pady=(0, 8))
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame, pack_toolbar=False)
        toolbar.pack(side="left")

        def redraw_detail(*_args):
            selected = detail_var.get()
            self.graph_vars[index].set(selected)

            figure.clear()
            previous_figure = self.figure
            previous_canvas = self.canvas

            try:
                self.figure = figure
                self.canvas = canvas
                self._draw_selected_graph(
                    selected,
                    self.last_result,
                    self.last_result["parameters"]
                )
                figure.tight_layout(
                    rect=(0.02, 0.10, 0.98, 0.96)
                )
                canvas.draw_idle()
            finally:
                self.figure = previous_figure
                self.canvas = previous_canvas

            detail.title(f"Graph {index + 1} - {selected}")

        def select_from_detail(_event=None):
            self.update_graph(show_errors=False)
            redraw_detail()

        detail_combo.bind(
            "<<ComboboxSelected>>",
            select_from_detail
        )

        def on_close():
            self.expanded_windows.pop(index, None)
            detail.destroy()

        detail.protocol("WM_DELETE_WINDOW", on_close)
        redraw_detail()


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

            self.doping_initial_var,

            self.doping_final_var,

            self.doping_steps_var,

            self.thickness_initial_var,

            self.thickness_final_var,

            self.thickness_steps_var,

            self.temperature_initial_var,

            self.temperature_final_var,

            self.temperature_steps_var
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
    # COMPARISON STUDY VALUES
    # ========================================================

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


    # ========================================================
    # COMPARISON CONTROL VISIBILITY / GRAPH OPTIONS
    # ========================================================

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

    def _draw_selected_graph(
        self,
        graph_name,
        result,
        params
    ):
        """Draw one selected graph using the existing drawing methods."""
        if graph_name in ("", "Empty"):
            return

        if graph_name == "Capacitance vs Reverse Bias":
            self.draw_basic_capacitance(result)

        elif graph_name == "Leakage Current vs Reverse Bias":
            self.draw_basic_leakage(result)

        elif graph_name == "Combined Capacitance & Leakage Current vs Reverse Bias":
            self.draw_combined(result)

        elif graph_name == "Capacitance vs Reverse Bias - Different Doping":
            values = self.get_doping_study_values()
            self.draw_doping_capacitance(result, values)

        elif graph_name == "Leakage Current vs Reverse Bias - Different Doping":
            values = self.get_doping_study_values()
            self.draw_doping_leakage(result, values, params)

        elif graph_name == "Capacitance vs Reverse Bias - Additional/High-Resolution Doping":
            values = self.get_doping_study_values()
            self.draw_high_resolution_doping_capacitance(
                result, values, params
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Additional/High-Resolution Doping":
            values = self.get_doping_study_values()
            self.draw_high_resolution_doping_leakage(
                result, values, params
            )

        elif graph_name == "Capacitance vs Reverse Bias - Different Thickness":
            values = self.get_thickness_study_values()
            self.draw_thickness_capacitance(
                result, values, params
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Different Thickness":
            values = self.get_thickness_study_values()
            self.draw_thickness_leakage(
                result, values, params
            )

        elif graph_name == "Capacitance vs Reverse Bias - Different Temperature":
            values = self.get_temperature_study_values()
            self.draw_temperature_capacitance(
                result, values
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Different Temperature":
            values = self.get_temperature_study_values()
            self.draw_temperature_leakage(
                result, values, params
            )

    # ========================================================
    # UPDATE GRAPH
    # ========================================================

    def update_graph(
        self,
        show_errors=True
    ):
        try:
            # Read the current values from the GUI fields.
            params = self.read_parameters()

            # Run the simulation only once, then use the result
            # for all four graph windows.
            result = self.run_simulation(params)
            self.last_result = result

            for index in range(4):
                figure = self.graph_figures[index]
                canvas = self.graph_canvases[index]
                graph_name = self.graph_vars[index].get()

                # Existing drawing functions use self.figure and
                # self.canvas, so point them at the current window.
                self.figure = figure
                self.canvas = canvas

                figure.clear()

                self._draw_selected_graph(
                    graph_name,
                    result,
                    params
                )

                # Reserve a little room for comparison legends placed
                # below the plot so they never cover the data.
                figure.tight_layout(
                    rect=(0.02, 0.12, 0.98, 0.96)
                )
                canvas.draw()
                canvas.flush_events()

            # Keep Graph 1 as the active figure for save-graph support
            # and compatibility with the existing drawing code.
            self.figure = self.graph_figures[0]
            self.canvas = self.graph_canvases[0]
            self.graph_var = self.graph_vars[0]

            self.update_results(result)

            selected = [
                name for name in self.graph_vars
                if name.get() not in ("", "Empty")
            ]

            if selected:
                self.status_var.set(
                    f"Updated: {len(selected)} graph(s)"
                )
            else:
                self.status_var.set("No graphs selected")

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
            fontsize=11,
            fontweight="bold",
            pad=8
        )

        ax.set_xlabel(
            "Reverse Bias Voltage (V)",
            fontsize=9
        )

        ax.set_ylabel(
            ylabel,
            fontsize=9
        )

        ax.tick_params(
            labelsize=8,
            pad=2
        )

        ax.grid(
            True,
            linestyle="--",
            linewidth=0.7,
            alpha=0.25
        )

        ax.margins(
            x=0.03,
            y=0.08
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def style_legend(
        self,
        ax,
        ncol=3,
        fontsize=7
    ):
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.24),
            ncol=ncol,
            fontsize=fontsize,
            frameon=False,
            borderaxespad=0.0
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

            "Capacitance vs Reverse Bias",

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

            "Leakage Current vs Reverse Bias",

            "Leakage Current (mA)"
        )


    # ========================================================
    # GRAPH 3
    # ========================================================

    def draw_combined(self, result):

        self.figure.clear()

        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()

        line1 = ax1.plot(
            result["voltage"],
            result["capacitance"] * 1e12,
            color="blue",
            linewidth=2.5,
            label="Capacitance"
        )

        line2 = ax2.plot(
            result["voltage"],
            result["leakage"] * 1e3,
            color="red",
            linewidth=2.5,
            label="Leakage Current"
        )

        ax1.set_xlabel("Reverse Bias Voltage (V)", fontsize=9)
        ax1.set_ylabel("Capacitance (pF)", color="blue", fontsize=9)
        ax2.set_ylabel("Leakage Current (mA)", color="red", fontsize=9)

        ax1.tick_params(axis="y", labelcolor="blue", labelsize=8)
        ax2.tick_params(axis="y", labelcolor="red", labelsize=8)
        ax1.tick_params(axis="x", labelsize=8)

        ax1.set_ylim(0, max(result["capacitance"] * 1e12) * 1.08)
        ax2.set_ylim(0, max(result["leakage"] * 1e3) * 1.08)

        ax1.set_title(
            "Capacitance & Leakage Current vs Reverse Bias",
            fontsize=11,
            fontweight="bold",
            pad=8
        )

        ax1.grid(True, linestyle="--", linewidth=0.7, alpha=0.25)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        lines = line1 + line2
        ax1.legend(
            lines,
            [l.get_label() for l in lines],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.22),
            ncol=2,
            fontsize=7,
            frameon=False
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
            "Different Doping",

            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
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
            "Different Doping",

            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
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
            "Different Thickness",

            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
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
            "Different Thickness",

            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )


    # ========================================================
    # GRAPH 6 - ADDITIONAL / HIGH-RESOLUTION DOPING
    # ========================================================

    def _high_resolution_doping_values(self, values):

        # Build a denser logarithmic doping grid from the user-selected
        # doping range. This keeps Graph 6 independent from Graph 4 while
        # preserving the same physical parameter range.
        low = min(values)
        high = max(values)

        if low == high:
            return np.array([low], dtype=float)

        return np.geomspace(low, high, 15)


    def _high_resolution_voltage(self, params):

        # Use a finer voltage grid for the additional/high-resolution study.
        points = max(501, int(round((params["vmax"] - params["vmin"]) / params["vstep"])) * 5 + 1)

        return np.linspace(
            params["vmin"],
            params["vmax"],
            points
        )


    def draw_high_resolution_doping_capacitance(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        voltage = self._high_resolution_voltage(params)
        doping_values = self._high_resolution_doping_values(values)

        for doping in doping_values:

            width = result["detector"].depletion_width_for_doping(
                voltage,
                doping
            )

            capacitance = result["detector"].capacitance(width)

            ax.plot(
                voltage,
                capacitance * 1e12,
                linewidth=1.5,
                label=f"{doping:.2e} cm⁻³"
            )

        self.style_axis(
            ax,
            "Capacitance vs Reverse Bias\n"
            "High-Resolution Doping",
            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=2,
            fontsize=6.5
        )


    # ========================================================
    # GRAPH 7 - ADDITIONAL / HIGH-RESOLUTION DOPING
    # ========================================================

    def draw_high_resolution_doping_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        voltage = self._high_resolution_voltage(params)
        doping_values = self._high_resolution_doping_values(values)

        leakage_model = result["leakage_model"]

        for doping in doping_values:

            width = result["detector"].depletion_width_for_doping(
                voltage,
                doping
            )

            leakage = self.calculate_leakage(
                leakage_model=leakage_model,
                fluence=params["final_fluence"],
                area=params["area"],
                width=width,
                temperature=params["temperature"]
            )

            ax.plot(
                voltage,
                leakage * 1e3,
                linewidth=1.5,
                label=f"{doping:.2e} cm⁻³"
            )

        self.style_axis(
            ax,
            "Leakage Current vs Reverse Bias\n"
            "High-Resolution Doping",
            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=2,
            fontsize=6.5
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
            "Different Temperature",

            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
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
            "Different Temperature",

            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
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