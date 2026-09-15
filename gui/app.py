import tkinter as tk
from .layout import LayoutMixin
from .simulation import SimulationMixin
from .graphs import GraphMixin
from .io import IOMixin

class RadiationDamageGUI(LayoutMixin, SimulationMixin, GraphMixin, IOMixin):
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
    GRAPH_OPTIONS = BASE_GRAPH_OPTIONS + DOPING_GRAPH_OPTIONS + THICKNESS_GRAPH_OPTIONS + TEMPERATURE_GRAPH_OPTIONS

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

def main():
    root=tk.Tk()
    RadiationDamageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
