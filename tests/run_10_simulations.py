"""
Radiation Damage Simulator
Automated 10-case test runner.

Place this file at:
    Radiation_Damage_Simulator/tests/run_10_simulations.py

Run from the project root:
    python tests/run_10_simulations.py

Output:
    output/test_results/
        Test_01_Baseline/
            graph_01_capacitance_vs_bias.png
            ...
            graph_11_leakage_vs_temperature.png
        ...
        Test_10_Extreme_Conditions/
        summary.csv

Each test case generates all 11 graphs.
"""

from pathlib import Path
import csv
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Project root = Radiation_Damage_Simulator/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from constants import K_B_EV, EG_SI, T_REF_K
from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent


# ============================================================
# 10 TEST CASES
# ============================================================

TEST_CASES = [
    {
        "name": "Baseline",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e12,
        "temperature": 293.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Low_Temperature",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e12,
        "temperature": 253.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "High_Temperature",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e12,
        "temperature": 353.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Thin_Detector",
        "thickness": 100,
        "area": 1.0,
        "doping": 1e13,
        "temperature": 293.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Thick_Detector",
        "thickness": 500,
        "area": 1.0,
        "doping": 1e13,
        "temperature": 293.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Low_Doping",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e11,
        "temperature": 293.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "High_Doping",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e14,
        "temperature": 293.15,
        "initial_fluence": 1e12,
        "final_fluence": 1e16,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Low_Fluence",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e12,
        "temperature": 293.15,
        "initial_fluence": 1e10,
        "final_fluence": 1e12,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "High_Fluence",
        "thickness": 300,
        "area": 1.0,
        "doping": 1e12,
        "temperature": 293.15,
        "initial_fluence": 1e16,
        "final_fluence": 1e18,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
    {
        "name": "Extreme_Conditions",
        "thickness": 150,
        "area": 2.0,
        "doping": 1e13,
        "temperature": 333.15,
        "initial_fluence": 1e14,
        "final_fluence": 1e17,
        "alpha": config.ALPHA,
        "vbi": 0.70,
        "vmin": 0,
        "vmax": 1000,
        "vstep": 10,
    },
]


# ============================================================
# STUDY VALUES — these produce graphs 4–11
# ============================================================

DOPING_VALUES = np.array(
    [1e11, 1e12, 1e13, 1e14, 1e15],
    dtype=float
)

THICKNESS_VALUES_UM = np.array(
    [50, 100, 150, 200, 250, 300, 500],
    dtype=float
)

# Temperature study uses Initial / Final / Steps.
TEMP_INITIAL_K = 253.15
TEMP_FINAL_K = 353.15
TEMP_STEPS = 6

Nd_CASE3 = 1e13


# ============================================================
# PHYSICS HELPERS
# ============================================================

def temperature_factor(temperature):
    return (
        (temperature / T_REF_K) ** 2
        * np.exp(
            (-EG_SI / (2.0 * K_B_EV))
            * (1.0 / temperature - 1.0 / T_REF_K)
        )
    )


def calculate_leakage(leakage_model, fluence, area, width, temperature):
    """
    Compatible with both:
      calculate(..., temperature_k=...)
    and older:
      calculate(...) + temperature factor
    """
    try:
        return leakage_model.calculate(
            fluence=fluence,
            area_cm2=area,
            thickness_cm=width,
            temperature_k=temperature,
        )
    except (TypeError, ValueError):
        reference_current = leakage_model.calculate(
            fluence=fluence,
            area_cm2=area,
            thickness_cm=width,
        )
        return np.asarray(reference_current, dtype=float) * temperature_factor(
            temperature
        )


def create_detector(params, thickness=None, doping=None, area=None):
    if thickness is None:
        thickness = params["thickness"]
    if doping is None:
        doping = params["doping"]
    if area is None:
        area = params["area"]

    return Detector(
        material=Silicon(),
        thickness_um=thickness,
        area_cm2=area,
        v_bi=params["vbi"],
        n_eff=doping,
    )


def run_simulation(params):
    detector = create_detector(params)
    leakage_model = LeakageCurrent(alpha=params["alpha"])

    voltage = np.arange(
        params["vmin"],
        params["vmax"] + params["vstep"] * 0.5,
        params["vstep"],
    )
    voltage = voltage[voltage <= params["vmax"] + 1e-12]

    width = np.asarray(
        detector.depletion_width(voltage),
        dtype=float
    )

    capacitance = np.asarray(
        detector.capacitance(width),
        dtype=float
    )

    leakage = np.asarray(
        calculate_leakage(
            leakage_model,
            params["final_fluence"],
            params["area"],
            width,
            params["temperature"],
        ),
        dtype=float,
    )

    return {
        "voltage": voltage,
        "width": width,
        "capacitance": capacitance,
        "leakage": leakage,
        "detector": detector,
        "leakage_model": leakage_model,
    }


# ============================================================
# GRAPH HELPERS
# ============================================================

def finish_and_save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def style_axis(ax, title, ylabel):
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Reverse Bias Voltage (V)", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.tick_params(labelsize=9)


# ============================================================
# GRAPH 1
# ============================================================

def graph_01(result, out):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(
        result["voltage"],
        result["capacitance"] * 1e12,
        linewidth=2.5,
    )
    style_axis(
        ax,
        "Capacitance vs Reverse Bias Voltage",
        "Capacitance (pF)",
    )
    finish_and_save(fig, out / "graph_01_capacitance_vs_bias.png")


# ============================================================
# GRAPH 2
# ============================================================

def graph_02(result, out):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(
        result["voltage"],
        result["leakage"] * 1e3,
        linewidth=2.5,
    )
    style_axis(
        ax,
        "Leakage Current vs Reverse Bias Voltage",
        "Leakage Current (mA)",
    )
    finish_and_save(fig, out / "graph_02_leakage_vs_bias.png")


# ============================================================
# GRAPH 3
# ============================================================

def graph_03(result, out):
    fig, ax1 = plt.subplots(figsize=(9, 6))
    ax2 = ax1.twinx()

    line1 = ax1.plot(
        result["voltage"],
        result["capacitance"] * 1e12,
        linewidth=2.5,
        label="Capacitance",
    )

    line2 = ax2.plot(
        result["voltage"],
        result["leakage"] * 1e3,
        linewidth=2.5,
        label="Leakage Current",
    )

    ax1.set_xlabel("Reverse Bias Voltage (V)")
    ax1.set_ylabel("Capacitance (pF)")
    ax2.set_ylabel("Leakage Current (mA)")

    ax1.set_title(
        "Capacitance and Leakage Current vs Reverse Bias Voltage"
    )
    ax1.grid(True, linestyle="--", alpha=0.3)

    lines = line1 + line2
    ax1.legend(
        lines,
        [line.get_label() for line in lines],
        loc="best",
    )

    finish_and_save(
        fig,
        out / "graph_03_combined_capacitance_leakage.png"
    )


# ============================================================
# GRAPH 4
# ============================================================

def graph_04(result, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    for doping in DOPING_VALUES:
        width = result["detector"].depletion_width_for_doping(
            result["voltage"],
            doping,
        )
        capacitance = result["detector"].capacitance(width)

        ax.plot(
            result["voltage"],
            capacitance * 1e12,
            linewidth=2,
            label=f"{doping:.1e} cm⁻³",
        )

    style_axis(
        ax,
        "Capacitance vs Reverse Bias\nfor Different Doping Concentrations",
        "Capacitance (pF)",
    )
    ax.legend(fontsize=8)

    finish_and_save(
        fig,
        out / "graph_04_capacitance_different_doping.png"
    )


# ============================================================
# GRAPH 5
# ============================================================

def graph_05(result, params, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    for doping in DOPING_VALUES:
        width = result["detector"].depletion_width_for_doping(
            result["voltage"],
            doping,
        )

        leakage = calculate_leakage(
            result["leakage_model"],
            params["final_fluence"],
            params["area"],
            width,
            params["temperature"],
        )

        ax.plot(
            result["voltage"],
            np.asarray(leakage) * 1e3,
            linewidth=2,
            label=f"{doping:.1e} cm⁻³",
        )

    style_axis(
        ax,
        "Leakage Current vs Reverse Bias\nfor Different Doping Concentrations",
        "Leakage Current (mA)",
    )
    ax.legend(fontsize=8)

    finish_and_save(
        fig,
        out / "graph_05_leakage_different_doping.png"
    )


# ============================================================
# GRAPH 6
# ============================================================

def graph_06(result, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    doping_values = np.geomspace(
        DOPING_VALUES.min(),
        DOPING_VALUES.max(),
        15,
    )

    # Same high-resolution voltage concept used by the GUI.
    points = max(
        501,
        int(round(
            (result["voltage"][-1] - result["voltage"][0])
            / (result["voltage"][1] - result["voltage"][0])
        )) * 5 + 1,
    )

    voltage = np.linspace(
        result["voltage"][0],
        result["voltage"][-1],
        points,
    )

    for doping in doping_values:
        width = result["detector"].depletion_width_for_doping(
            voltage,
            doping,
        )
        capacitance = result["detector"].capacitance(width)

        ax.plot(
            voltage,
            capacitance * 1e12,
            linewidth=1.5,
            label=f"{doping:.2e} cm⁻³",
        )

    style_axis(
        ax,
        "Capacitance vs Reverse Bias\nAdditional / High-Resolution Doping Study",
        "Capacitance (pF)",
    )
    ax.legend(fontsize=7, ncol=2)

    finish_and_save(
        fig,
        out / "graph_06_capacitance_high_resolution_doping.png"
    )


# ============================================================
# GRAPH 7
# ============================================================

def graph_07(result, params, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    doping_values = np.geomspace(
        DOPING_VALUES.min(),
        DOPING_VALUES.max(),
        15,
    )

    points = max(
        501,
        int(round(
            (result["voltage"][-1] - result["voltage"][0])
            / (result["voltage"][1] - result["voltage"][0])
        )) * 5 + 1,
    )

    voltage = np.linspace(
        result["voltage"][0],
        result["voltage"][-1],
        points,
    )

    for doping in doping_values:
        width = result["detector"].depletion_width_for_doping(
            voltage,
            doping,
        )

        leakage = calculate_leakage(
            result["leakage_model"],
            params["final_fluence"],
            params["area"],
            width,
            params["temperature"],
        )

        ax.plot(
            voltage,
            np.asarray(leakage) * 1e3,
            linewidth=1.5,
            label=f"{doping:.2e} cm⁻³",
        )

    style_axis(
        ax,
        "Leakage Current vs Reverse Bias\nAdditional / High-Resolution Doping Study",
        "Leakage Current (mA)",
    )
    ax.legend(fontsize=7, ncol=2)

    finish_and_save(
        fig,
        out / "graph_07_leakage_high_resolution_doping.png"
    )


# ============================================================
# GRAPH 8 — THICKNESS CAPACITANCE
# Case-3 condition: Nd = 1e13 cm^-3
# ============================================================

def graph_08(result, params, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    for thickness_um in THICKNESS_VALUES_UM:
        detector = create_detector(
            params,
            thickness=thickness_um,
            doping=Nd_CASE3,
        )

        width = detector.depletion_width(result["voltage"])
        capacitance = detector.capacitance(width)

        ax.plot(
            result["voltage"],
            np.asarray(capacitance) * 1e12,
            linewidth=2,
            label=f"{thickness_um:g} µm",
        )

    style_axis(
        ax,
        "Capacitance vs Reverse Bias\nfor Different Detector Thicknesses",
        "Capacitance (pF)",
    )
    ax.legend(title="Thickness", fontsize=8)

    finish_and_save(
        fig,
        out / "graph_08_capacitance_different_thickness.png"
    )


# ============================================================
# GRAPH 9 — THICKNESS LEAKAGE
# Case-3 condition: Nd = 1e13 cm^-3
# ============================================================

def graph_09(result, params, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    for thickness_um in THICKNESS_VALUES_UM:
        detector = create_detector(
            params,
            thickness=thickness_um,
            doping=Nd_CASE3,
        )

        width = detector.depletion_width(result["voltage"])

        leakage = calculate_leakage(
            result["leakage_model"],
            params["final_fluence"],
            params["area"],
            width,
            params["temperature"],
        )

        ax.plot(
            result["voltage"],
            np.asarray(leakage) * 1e3,
            linewidth=2,
            label=f"{thickness_um:g} µm",
        )

    style_axis(
        ax,
        "Leakage Current vs Reverse Bias\nfor Different Detector Thicknesses",
        "Leakage Current (mA)",
    )
    ax.legend(title="Thickness", fontsize=8)

    finish_and_save(
        fig,
        out / "graph_09_leakage_different_thickness.png"
    )


# ============================================================
# GRAPH 10 — TEMPERATURE CAPACITANCE
# Current detector model makes capacitance temperature-independent.
# ============================================================

def graph_10(result, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    temperatures = np.linspace(
        TEMP_INITIAL_K,
        TEMP_FINAL_K,
        TEMP_STEPS,
    )

    for temperature in temperatures:
        ax.plot(
            result["voltage"],
            result["capacitance"] * 1e12,
            linewidth=2,
            label=(
                f"{temperature:.2f} K "
                f"({temperature - 273.15:.1f} °C)"
            ),
        )

    style_axis(
        ax,
        "Capacitance vs Reverse Bias\nfor Different Operating Temperatures",
        "Capacitance (pF)",
    )
    ax.legend(fontsize=8)

    finish_and_save(
        fig,
        out / "graph_10_capacitance_different_temperature.png"
    )


# ============================================================
# GRAPH 11 — TEMPERATURE LEAKAGE
# ============================================================

def graph_11(result, params, out):
    fig, ax = plt.subplots(figsize=(9, 6))

    temperatures = np.linspace(
        TEMP_INITIAL_K,
        TEMP_FINAL_K,
        TEMP_STEPS,
    )

    for temperature in temperatures:
        leakage = calculate_leakage(
            result["leakage_model"],
            params["final_fluence"],
            params["area"],
            result["width"],
            temperature,
        )

        ax.plot(
            result["voltage"],
            np.asarray(leakage) * 1e3,
            linewidth=2,
            label=(
                f"{temperature:.2f} K "
                f"({temperature - 273.15:.1f} °C)"
            ),
        )

    style_axis(
        ax,
        "Leakage Current vs Reverse Bias\nfor Different Operating Temperatures",
        "Leakage Current (mA)",
    )
    ax.legend(fontsize=8)

    finish_and_save(
        fig,
        out / "graph_11_leakage_different_temperature.png"
    )


# ============================================================
# RUN ONE TEST
# ============================================================

def run_one_test(case_number, params, results_root):
    folder = results_root / f"Test_{case_number:02d}_{params['name']}"
    folder.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 70)
    print(f"TEST {case_number:02d}: {params['name']}")
    print("=" * 70)

    result = run_simulation(params)

    graph_01(result, folder)
    graph_02(result, folder)
    graph_03(result, folder)
    graph_04(result, folder)
    graph_05(result, params, folder)
    graph_06(result, folder)
    graph_07(result, params, folder)
    graph_08(result, params, folder)
    graph_09(result, params, folder)
    graph_10(result, folder)
    graph_11(result, params, folder)

    final_width_um = result["width"][-1] * 1e4
    final_cap_pf = result["capacitance"][-1] * 1e12
    final_current_ma = result["leakage"][-1] * 1e3

    try:
        vfd = result["detector"].full_depletion_voltage()
    except Exception:
        vfd = float("nan")

    print(f"Thickness       : {params['thickness']} µm")
    print(f"Area            : {params['area']} cm²")
    print(f"Doping          : {params['doping']:.3e} cm⁻³")
    print(f"Temperature     : {params['temperature']:.2f} K")
    print(f"Final fluence   : {params['final_fluence']:.3e} neq/cm²")
    print(f"Full depletion  : {vfd:.6g} V")
    print(f"Final width     : {final_width_um:.6f} µm")
    print(f"Final capacitance: {final_cap_pf:.6f} pF")
    print(f"Final leakage   : {final_current_ma:.6g} mA")
    print(f"Saved graphs    : 11")
    print(f"Folder          : {folder}")

    return {
        "test": case_number,
        "name": params["name"],
        "thickness_um": params["thickness"],
        "area_cm2": params["area"],
        "doping_cm-3": params["doping"],
        "temperature_K": params["temperature"],
        "initial_fluence": params["initial_fluence"],
        "final_fluence": params["final_fluence"],
        "full_depletion_voltage_V": vfd,
        "final_width_um": final_width_um,
        "final_capacitance_pF": final_cap_pf,
        "final_leakage_mA": final_current_ma,
        "graphs_saved": 11,
        "status": "PASS",
    }


# ============================================================
# MAIN
# ============================================================

def main():
    results_root = PROJECT_ROOT / "output" / "test_results"
    results_root.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 70)
    print("RADIATION DAMAGE SIMULATOR - 10 AUTOMATED TEST CASES")
    print("=" * 70)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Output folder: {results_root}")
    print("Each test will generate 11 graphs.")
    print(f"Total expected PNG files: {len(TEST_CASES) * 11}")
    print()

    summary = []
    failed = 0

    for number, params in enumerate(TEST_CASES, start=1):
        try:
            row = run_one_test(
                number,
                params,
                results_root,
            )
            summary.append(row)
        except Exception as error:
            failed += 1
            print()
            print(f"TEST {number:02d} FAILED: {error}")
            summary.append({
                "test": number,
                "name": params["name"],
                "status": f"FAIL: {error}",
            })

    # Save summary CSV.
    summary_file = results_root / "summary.csv"

    fieldnames = [
        "test",
        "name",
        "thickness_um",
        "area_cm2",
        "doping_cm-3",
        "temperature_K",
        "initial_fluence",
        "final_fluence",
        "full_depletion_voltage_V",
        "final_width_um",
        "final_capacitance_pF",
        "final_leakage_mA",
        "graphs_saved",
        "status",
    ]

    with open(
        summary_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(summary)

    print()
    print("=" * 70)
    print("TEST RUN COMPLETE")
    print("=" * 70)
    print(f"Total tests : {len(TEST_CASES)}")
    print(f"Passed      : {len(TEST_CASES) - failed}")
    print(f"Failed      : {failed}")
    print(f"Expected PNG: {len(TEST_CASES) * 11}")
    print(f"Results     : {results_root}")
    print(f"Summary CSV : {summary_file}")
    print("=" * 70)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
