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


class IOMixin:
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
