import numpy as np
import matplotlib.pyplot as plt


def plot_combined(
    reverse_voltage,
    capacitance_list,
    current_list
):

    ############################################################
    # COMBINED PLOT:
    # Capacitance & Leakage Current vs Reverse Bias
    ############################################################

    fig, ax1 = plt.subplots(figsize=(9, 6))

    # ----------------------------------------------------------
    # LEFT Y-AXIS : CAPACITANCE
    # ----------------------------------------------------------

    ax1.plot(
        reverse_voltage,
        np.array(capacitance_list) * 1e12,
        color="blue",
        linewidth=3,
        label="Capacitance"
    )

    ax1.set_xlabel(
        "Reverse Bias Voltage (V)",
        fontsize=12
    )

    ax1.set_ylabel(
        "Capacitance (pF)",
        fontsize=12,
        color="blue"
    )

    ax1.tick_params(
        axis="y",
        labelcolor="blue"
    )

    ax1.grid(True)


    # ----------------------------------------------------------
    # RIGHT Y-AXIS : LEAKAGE CURRENT
    # ----------------------------------------------------------

    ax2 = ax1.twinx()

    ax2.plot(
        reverse_voltage,
        np.array(current_list) * 1e3,
        color="red",
        linewidth=3,
        label="Leakage Current"
    )

    ax2.set_ylabel(
        "Leakage Current (mA)",
        fontsize=12,
        color="red"
    )

    ax2.tick_params(
        axis="y",
        labelcolor="red"
    )


    # ----------------------------------------------------------
    # COMBINED LEGEND
    # ----------------------------------------------------------

    lines1, labels1 = (
        ax1.get_legend_handles_labels()
    )

    lines2, labels2 = (
        ax2.get_legend_handles_labels()
    )

    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="best"
    )


    # ----------------------------------------------------------
    # TITLE
    # ----------------------------------------------------------

    plt.title(
        "Capacitance and Leakage Current vs Reverse Bias Voltage",
        fontsize=14
    )

    plt.tight_layout()

    plt.show()