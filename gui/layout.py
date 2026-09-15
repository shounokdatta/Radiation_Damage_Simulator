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


class LayoutMixin:
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

                "233", "243", "253", "263",

                "273", "283", "293", "303",

                "313", "323", "333", "343",

                "353", "363", "373"

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
