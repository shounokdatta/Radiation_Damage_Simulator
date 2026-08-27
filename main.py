# ============================================================
# RADIATION DAMAGE SIMULATOR
# ============================================================

import numpy as np
import config

from materials.silicon import Silicon
from physics.detector import Detector
from detector.leakage_current import LeakageCurrent

from analysis.plots import plot_combined


# ============================================================
# CREATE SILICON MATERIAL
# ============================================================

silicon = Silicon()


# ============================================================
# CREATE DETECTOR
# ============================================================

detector = Detector(
    material=silicon,
    thickness_um=config.THICKNESS_UM,
    area_cm2=config.AREA_CM2,
    v_bi=config.V_BI,
    n_eff=config.N_EFF
)


# ============================================================
# CREATE LEAKAGE CURRENT MODEL
# ============================================================

leakage_model = LeakageCurrent(
    alpha=config.ALPHA
)


# ============================================================
# REVERSE BIAS VOLTAGE
# ============================================================

reverse_voltage = np.linspace(
    config.REVERSE_VOLTAGE_MIN,
    config.REVERSE_VOLTAGE_MAX,
    config.REVERSE_VOLTAGE_POINTS
)


# ============================================================
# DEPLETION WIDTH
# ============================================================

depletion_width = detector.depletion_width(
    reverse_voltage
)


# ============================================================
# CAPACITANCE
# ============================================================

capacitance = detector.capacitance(
    depletion_width
)


# ============================================================
# LEAKAGE CURRENT
# ============================================================

current = leakage_model.calculate(
    fluence=config.FINAL_FLUENCE,
    area_cm2=config.AREA_CM2,
    thickness_cm=detector.thickness_cm
)


# ============================================================
# FULL DEPLETION VOLTAGE
# ============================================================

full_depletion_voltage = (
    detector.full_depletion_voltage()
)


# ============================================================
# FINAL VALUES
# ============================================================

final_depletion_width_um = (
    depletion_width[-1] * 1e4
)

final_capacitance_pf = (
    capacitance[-1] * 1e12
)

final_current_a = current

final_current_ma = (
    final_current_a * 1e3
)


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print()

print("=" * 60)
print("       RADIATION DAMAGE SIMULATOR")
print("=" * 60)

print()

print(
    f"Material       : {silicon.name}"
)

print(
    f"Thickness      : "
    f"{config.THICKNESS_UM:.1f} µm"
)

print(
    f"Area           : "
    f"{config.AREA_CM2:.1f} cm²"
)

print(
    f"Temperature    : "
    f"{config.TEMPERATURE_K:.2f} K"
)

print()

print(
    f"Initial fluence : "
    f"{config.INITIAL_FLUENCE:.2e} neq/cm²"
)

print(
    f"Final fluence   : "
    f"{config.FINAL_FLUENCE:.2e} neq/cm²"
)

print()

print(
    f"Effective doping : "
    f"{config.N_EFF:.2e} cm^-3"
)

print(
    f"Damage constant  : "
    f"{config.ALPHA:.2e} A/cm"
)

print()

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

print("Simulation complete.")

print("=" * 60)


# ============================================================
# COMBINED PLOT
# ============================================================

# Leakage current is constant with reverse bias in the
# simple I = alpha × fluence × volume model.

current_list = np.full(
    len(reverse_voltage),
    current
)


plot_combined(
    reverse_voltage,
    capacitance,
    current_list
)