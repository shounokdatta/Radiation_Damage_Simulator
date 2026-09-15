import numpy as np
from matplotlib.figure import Figure


class GraphMixin:

    # ============================================================
    # GRAPH DISPATCHER
    # ============================================================

    def _draw_selected_graph(self, graph_name, result, params):

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
                result,
                values,
                params
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Additional/High-Resolution Doping":
            values = self.get_doping_study_values()
            self.draw_high_resolution_doping_leakage(
                result,
                values,
                params
            )

        elif graph_name == "Capacitance vs Reverse Bias - Different Thickness":
            values = self.get_thickness_study_values()
            self.draw_thickness_capacitance(
                result,
                values,
                params
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Different Thickness":
            values = self.get_thickness_study_values()
            self.draw_thickness_leakage(
                result,
                values,
                params
            )

        elif graph_name == "Capacitance vs Reverse Bias - Different Temperature":
            values = self.get_temperature_study_values()
            self.draw_temperature_capacitance(
                result,
                values
            )

        elif graph_name == "Leakage Current vs Reverse Bias - Different Temperature":
            values = self.get_temperature_study_values()
            self.draw_temperature_leakage(
                result,
                values,
                params
            )

    # ============================================================
    # UPDATE ALL FOUR MINI GRAPHS
    # ============================================================

    def update_graph(self, show_errors=True):

        try:

            params = self.read_parameters()

            result = self.run_simulation(params)

            self.last_result = result

            for index in range(4):

                figure = self.graph_figures[index]
                canvas = self.graph_canvases[index]

                graph_name = self.graph_vars[index].get()

                self.figure = figure
                self.canvas = canvas

                figure.clear()

                self._draw_selected_graph(
                    graph_name,
                    result,
                    params
                )

                # Normal layout first
                figure.tight_layout(
                    rect=(0.02, 0.12, 0.98, 0.96)
                )

                # Then make the actual plot SMALL
                self.compact_mini_graph(figure)

                canvas.draw()
                canvas.flush_events()

            # Keep Graph 1 active
            self.figure = self.graph_figures[0]
            self.canvas = self.graph_canvases[0]
            self.graph_var = self.graph_vars[0]

            self.update_results(result)

            selected = [
                name
                for name in self.graph_vars
                if name.get() not in ("", "Empty")
            ]

            if selected:
                self.status_var.set(
                    f"Updated: {len(selected)} graph(s)"
                )
            else:
                self.status_var.set(
                    "No graphs selected"
                )

        except Exception as error:

            self.status_var.set(
                f"Error: {error}"
            )

            if show_errors:

                from tkinter import messagebox

                messagebox.showerror(
                    "Simulation Error",
                    str(error)
                )

    # ============================================================
    # MINIATURE GRAPH STYLE
    # ============================================================

    @staticmethod
    def compact_mini_graph(figure):

        """
        Front/dashboard graph.

        IMPORTANT:
        The miniature graph contains ONLY:
            - curve
            - numeric X scale
            - numeric Y scale

        It does NOT contain:
            - title
            - X-axis label
            - Y-axis label
            - legend
            - grid
        """

        if not figure.axes:
            return

        for ax in figure.axes:

            # ----------------------------------------------------
            # Remove all text
            # ----------------------------------------------------

            ax.set_title("")
            ax.set_xlabel("")
            ax.set_ylabel("")

            # ----------------------------------------------------
            # Remove grid
            # ----------------------------------------------------

            ax.grid(False)

            # ----------------------------------------------------
            # Remove legend
            # ----------------------------------------------------

            legend = ax.get_legend()

            if legend is not None:
                legend.remove()

            # ----------------------------------------------------
            # Small numeric tick labels
            # ----------------------------------------------------

            ax.tick_params(
                axis="both",
                which="both",
                labelsize=7,
                length=3,
                width=0.8,
                pad=2
            )

            # ----------------------------------------------------
            # Keep the graph border
            # ----------------------------------------------------

            for spine in ax.spines.values():
                spine.set_visible(True)

            # ----------------------------------------------------
            # THIS controls the FRONT GRAPH SIZE
            # ----------------------------------------------------
            #
            # Smaller width + smaller height
            # gives the compact graph shown in your reference.
            #
            # left   = 0.32
            # bottom = 0.22
            # width  = 0.36
            # height = 0.56
            #
            # ----------------------------------------------------

            ax.set_position([
                0.32,
                0.22,
                0.36,
                0.56
            ])

    # ============================================================
    # FULL / EXPANDED GRAPH AXIS STYLE
    # ============================================================

    @staticmethod
    def style_axis(ax, title, ylabel):

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

    # ============================================================
    # LEGEND
    # ============================================================

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

    # ============================================================
    # GRAPH 1
    # CAPACITANCE VS REVERSE BIAS
    # ============================================================

    def draw_basic_capacitance(self, result):

        ax = self.figure.add_subplot(111)

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

    # ============================================================
    # GRAPH 2
    # LEAKAGE CURRENT VS REVERSE BIAS
    # ============================================================

    def draw_basic_leakage(self, result):

        ax = self.figure.add_subplot(111)

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

    # ============================================================
    # GRAPH 3
    # COMBINED CAPACITANCE + LEAKAGE
    # ============================================================

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

        ax1.set_xlabel(
            "Reverse Bias Voltage (V)",
            fontsize=9
        )

        ax1.set_ylabel(
            "Capacitance (pF)",
            color="blue",
            fontsize=9
        )

        ax2.set_ylabel(
            "Leakage Current (mA)",
            color="red",
            fontsize=9
        )

        ax1.tick_params(
            axis="y",
            labelcolor="blue",
            labelsize=8
        )

        ax2.tick_params(
            axis="y",
            labelcolor="red",
            labelsize=8
        )

        ax1.tick_params(
            axis="x",
            labelsize=8
        )

        cap = result["capacitance"] * 1e12
        leak = result["leakage"] * 1e3

        ax1.set_ylim(
            0,
            max(cap) * 1.08
        )

        ax2.set_ylim(
            0,
            max(leak) * 1.08
        )

        ax1.set_title(
            "Capacitance & Leakage Current vs Reverse Bias",
            fontsize=11,
            fontweight="bold",
            pad=8
        )

        ax1.grid(
            True,
            linestyle="--",
            linewidth=0.7,
            alpha=0.25
        )

        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        lines = line1 + line2

        ax1.legend(
            lines,
            [line.get_label() for line in lines],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.22),
            ncol=2,
            fontsize=7,
            frameon=False
        )

    # ============================================================
    # GRAPH 4
    # CAPACITANCE - DIFFERENT DOPING
    # ============================================================

    def draw_doping_capacitance(
        self,
        result,
        values
    ):

        ax = self.figure.add_subplot(111)

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
                .capacitance(width)
            )

            ax.plot(
                result["voltage"],
                capacitance * 1e12,
                linewidth=2,
                label=f"{doping:.1e} cm⁻³"
            )

        self.style_axis(
            ax,
            "Capacitance vs Reverse Bias\nDifferent Doping",
            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )

    # ============================================================
    # GRAPH 5
    # LEAKAGE - DIFFERENT DOPING
    # ============================================================

    def draw_doping_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        for doping in values:

            width = (
                result["detector"]
                .depletion_width_for_doping(
                    result["voltage"],
                    doping
                )
            )

            leakage = self.calculate_leakage(
                leakage_model=result["leakage_model"],
                fluence=params["final_fluence"],
                area=params["area"],
                width=width,
                temperature=params["temperature"]
            )

            ax.plot(
                result["voltage"],
                leakage * 1e3,
                linewidth=2,
                label=f"{doping:.1e} cm⁻³"
            )

        self.style_axis(
            ax,
            "Leakage Current vs Reverse Bias\nDifferent Doping",
            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )

    # ============================================================
    # GRAPH 6
    # HIGH-RESOLUTION DOPING - CAPACITANCE
    # ============================================================

    def _high_resolution_doping_values(self, values):

        low = min(values)
        high = max(values)

        if low == high:
            return np.array(
                [low],
                dtype=float
            )

        return np.geomspace(
            low,
            high,
            15
        )

    # ============================================================
    # HIGH-RESOLUTION VOLTAGE
    # ============================================================

    def _high_resolution_voltage(self, params):

        points = max(
            501,
            int(
                round(
                    (
                        params["vmax"]
                        - params["vmin"]
                    )
                    / params["vstep"]
                )
            ) * 5 + 1
        )

        return np.linspace(
            params["vmin"],
            params["vmax"],
            points
        )

    # ============================================================
    # GRAPH 6
    # HIGH-RESOLUTION DOPING CAPACITANCE
    # ============================================================

    def draw_high_resolution_doping_capacitance(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        voltage = self._high_resolution_voltage(
            params
        )

        doping_values = (
            self._high_resolution_doping_values(
                values
            )
        )

        for doping in doping_values:

            width = (
                result["detector"]
                .depletion_width_for_doping(
                    voltage,
                    doping
                )
            )

            capacitance = (
                result["detector"]
                .capacitance(width)
            )

            ax.plot(
                voltage,
                capacitance * 1e12,
                linewidth=1.5,
                label=f"{doping:.2e} cm⁻³"
            )

        self.style_axis(
            ax,
            "Capacitance vs Reverse Bias\nHigh-Resolution Doping",
            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=2,
            fontsize=6.5
        )

    # ============================================================
    # GRAPH 7
    # HIGH-RESOLUTION DOPING LEAKAGE
    # ============================================================

    def draw_high_resolution_doping_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        voltage = self._high_resolution_voltage(
            params
        )

        doping_values = (
            self._high_resolution_doping_values(
                values
            )
        )

        leakage_model = result["leakage_model"]

        for doping in doping_values:

            width = (
                result["detector"]
                .depletion_width_for_doping(
                    voltage,
                    doping
                )
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
            "Leakage Current vs Reverse Bias\nHigh-Resolution Doping",
            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=2,
            fontsize=6.5
        )

    # ============================================================
    # GRAPH 8
    # CAPACITANCE - DIFFERENT THICKNESS
    # ============================================================

    def draw_thickness_capacitance(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

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
            "Capacitance vs Reverse Bias\nDifferent Thickness",
            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )

    # ============================================================
    # GRAPH 9
    # LEAKAGE - DIFFERENT THICKNESS
    # ============================================================

    def draw_thickness_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        for thickness in values:

            detector = self.create_detector(
                params,
                thickness=thickness
            )

            width = detector.depletion_width(
                result["voltage"]
            )

            leakage = self.calculate_leakage(
                leakage_model=result["leakage_model"],
                fluence=params["final_fluence"],
                area=params["area"],
                width=width,
                temperature=params["temperature"]
            )

            ax.plot(
                result["voltage"],
                leakage * 1e3,
                linewidth=2,
                label=f"{thickness:g} µm"
            )

        self.style_axis(
            ax,
            "Leakage Current vs Reverse Bias\nDifferent Thickness",
            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )

    # ============================================================
    # GRAPH 10
    # CAPACITANCE - DIFFERENT TEMPERATURE
    # ============================================================

    def draw_temperature_capacitance(
        self,
        result,
        values
    ):

        ax = self.figure.add_subplot(111)

        for temperature in values:

            # Current detector capacitance model is
            # independent of temperature.

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
            "Capacitance vs Reverse Bias\nDifferent Temperature",
            "Capacitance (pF)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )

    # ============================================================
    # GRAPH 11
    # LEAKAGE - DIFFERENT TEMPERATURE
    # ============================================================

    def draw_temperature_leakage(
        self,
        result,
        values,
        params
    ):

        ax = self.figure.add_subplot(111)

        for temperature in values:

            leakage = self.calculate_leakage(
                leakage_model=result["leakage_model"],
                fluence=params["final_fluence"],
                area=params["area"],
                width=result["width"],
                temperature=temperature
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
            "Leakage Current vs Reverse Bias\nDifferent Temperature",
            "Leakage Current (mA)"
        )

        self.style_legend(
            ax,
            ncol=3,
            fontsize=7
        )