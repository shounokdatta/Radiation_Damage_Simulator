# ============================================================
# PLOTTING FUNCTIONS
# ============================================================

import matplotlib.pyplot as plt


def plot_combined(
    reverse_voltage,
    capacitance,
    current_list
):

    # ========================================================
    # CREATE FIGURE
    # ========================================================

    fig, ax1 = plt.subplots(
        figsize=(10, 6)
    )


    # ========================================================
    # CAPACITANCE
    # LEFT Y-AXIS
    # ========================================================

    line1 = ax1.plot(
        reverse_voltage,
        capacitance * 1e12,
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


    # ========================================================
    # GRID
    # ========================================================

    ax1.grid(
        True,
        linestyle="--",
        alpha=0.6
    )


    # ========================================================
    # LEAKAGE CURRENT
    # RIGHT Y-AXIS
    # ========================================================

    ax2 = ax1.twinx()

    line2 = ax2.plot(
        reverse_voltage,
        current_list * 1e3,
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


    # ========================================================
    # COMBINED LEGEND
    # ========================================================

    lines = line1 + line2

    labels = [
        line.get_label()
        for line in lines
    ]

    ax1.legend(
        lines,
        labels,
        loc="best"
    )


    # ========================================================
    # TITLE
    # ========================================================

    plt.title(
        "Capacitance and Leakage Current vs Reverse Bias Voltage",
        fontsize=14
    )


    # ========================================================
    # FINAL SETTINGS
    # ========================================================

    plt.tight_layout()

    plt.show()