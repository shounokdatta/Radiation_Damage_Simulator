# ============================================================
# RADIATION DAMAGE SIMULATOR
# ============================================================
#
# Calculates:
#
#   1. Depletion width
#   2. Capacitance
#   3. Radiation-induced leakage current
#   4. Full depletion voltage
#
# Produces:
#
#   1. Capacitance vs Reverse Bias Voltage
#   2. Leakage Current vs Reverse Bias Voltage
#   3. Capacitance and Leakage Current
#      vs Reverse Bias Voltage
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import numpy as np
import config

from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent

from analysis.plots import (
    plot_capacitance_vs_reverse_bias,
    plot_leakage_current_vs_reverse_bias,
    plot_combined
)


# ============================================================
# 1. CREATE SILICON MATERIAL
# ============================================================

silicon = Silicon()


# ============================================================
# 2. CREATE DETECTOR
# ============================================================

detector = Detector(
    material=silicon,
    thickness_um=config.THICKNESS_UM,
    area_cm2=config.AREA_CM2,
    v_bi=config.V_BI,
    n_eff=config.N_EFF
)


# ============================================================
# 3. CREATE LEAKAGE CURRENT MODEL
# ============================================================

leakage_model = LeakageCurrent(
    alpha=config.ALPHA
)


# ============================================================
# 4. CREATE REVERSE BIAS VOLTAGE ARRAY
# ============================================================

reverse_voltage = np.linspace(
    config.REVERSE_VOLTAGE_MIN,
    config.REVERSE_VOLTAGE_MAX,
    config.REVERSE_VOLTAGE_POINTS
)


# ============================================================
# 5. CALCULATE DEPLETION WIDTH
# ============================================================

depletion_width = detector.depletion_width(
    reverse_voltage
)


# ============================================================
# 6. CALCULATE CAPACITANCE
# ============================================================

capacitance = detector.capacitance(
    depletion_width
)


# ============================================================
# 7. CALCULATE LEAKAGE CURRENT
# ============================================================

current_list = []

for width in depletion_width:

    current = leakage_model.calculate(
        fluence=config.FINAL_FLUENCE,
        area_cm2=config.AREA_CM2,
        thickness_cm=width
    )

    current_list.append(current)


# Convert leakage current list to NumPy array
current_list = np.array(
    current_list
)


# ============================================================
# 8. FULL DEPLETION VOLTAGE
# ============================================================

full_depletion_voltage = (
    detector.full_depletion_voltage()
)


# ============================================================
# 9. FINAL VALUES
# ============================================================

final_depletion_width_um = (
    depletion_width[-1] * 1e4
)

final_capacitance_pf = (
    capacitance[-1] * 1e12
)

final_current_a = (
    current_list[-1]
)

final_current_ma = (
    final_current_a * 1e3
)


# ============================================================
# 10. DISPLAY RESULTS
# ============================================================

print()

print("=" * 65)
print("                 RADIATION DAMAGE SIMULATOR")
print("=" * 65)

print()

print("DETECTOR PARAMETERS")
print("-" * 65)

print(
    f"Material               : {silicon.name}"
)

print(
    f"Thickness              : "
    f"{config.THICKNESS_UM:.1f} µm"
)

print(
    f"Area                   : "
    f"{config.AREA_CM2:.2f} cm²"
)

print(
    f"Temperature            : "
    f"{config.TEMPERATURE_K:.2f} K"
)

print()

print("RADIATION PARAMETERS")
print("-" * 65)

print(
    f"Initial fluence        : "
    f"{config.INITIAL_FLUENCE:.2e} neq/cm²"
)

print(
    f"Final fluence          : "
    f"{config.FINAL_FLUENCE:.2e} neq/cm²"
)

print(
    f"Damage constant        : "
    f"{config.ALPHA:.2e} A/cm"
)

print()

print("JUNCTION PARAMETERS")
print("-" * 65)

print(
    f"Built-in voltage       : "
    f"{config.V_BI:.2f} V"
)

print(
    f"Effective doping       : "
    f"{config.N_EFF:.2e} cm⁻³"
)

print()

print("SIMULATION RESULTS")
print("-" * 65)

print(
    f"Full depletion voltage : "
    f"{full_depletion_voltage:.2f} V"
)

print(
    f"Final depletion width  : "
    f"{final_depletion_width_um:.2f} µm"
)

print(
    f"Final capacitance      : "
    f"{final_capacitance_pf:.4f} pF"
)

print(
    f"Final leakage current  : "
    f"{final_current_a:.4e} A"
)

print(
    f"Final leakage current  : "
    f"{final_current_ma:.4f} mA"
)

print()

print("=" * 65)
print("Simulation complete.")
print("=" * 65)


# ============================================================
# 11. PLOT RESULTS
# ============================================================

# ------------------------------------------------------------
# GRAPH 1
# Capacitance vs Reverse Bias
# ------------------------------------------------------------

plot_capacitance_vs_reverse_bias(
    reverse_voltage,
    capacitance
)


# ------------------------------------------------------------
# GRAPH 2
# Leakage Current vs Reverse Bias
# ------------------------------------------------------------

plot_leakage_current_vs_reverse_bias(
    reverse_voltage,
    current_list
)


# ------------------------------------------------------------
# GRAPH 3
# Capacitance and Leakage Current vs Reverse Bias
# ------------------------------------------------------------

plot_combined(
    reverse_voltage,
    capacitance,
    current_list
)