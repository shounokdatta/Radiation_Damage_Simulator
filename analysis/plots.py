"""Standalone plotting helpers for scripts/reports.

The GUI does not call plt.show(); it embeds Matplotlib directly.
These helpers are useful when running the command-line main.py.
"""

import matplotlib.pyplot as plt

FIGSIZE = (8, 5)
DPI = 150


def plot_capacitance_vs_reverse_bias(voltage, capacitance_f, show=True):
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.plot(voltage, capacitance_f * 1e12, linewidth=2)
    ax.set_xlabel("Reverse Bias Voltage (V)")
    ax.set_ylabel("Capacitance (pF)")
    ax.set_title("Capacitance vs Reverse Bias")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    if show:
        plt.show()
    return fig, ax


def plot_leakage_current_vs_reverse_bias(voltage, leakage_a, show=True):
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.plot(voltage, leakage_a * 1e3, linewidth=2)
    ax.set_xlabel("Reverse Bias Voltage (V)")
    ax.set_ylabel("Leakage Current (mA)")
    ax.set_title("Leakage Current vs Reverse Bias")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    if show:
        plt.show()
    return fig, ax
