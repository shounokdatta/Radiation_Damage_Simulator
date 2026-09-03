"""Command-line entry point.

Default: launch the interactive GUI.
Use `python main.py --cli` to print a default simulation summary.
"""

import sys
import config
from gui.simulator import SimulationParameters, run_simulation


def run_cli():
    p = SimulationParameters(
        thickness_um=config.THICKNESS_UM,
        area_cm2=config.AREA_CM2,
        doping_cm3=config.N_EFF,
        v_bi=config.V_BI,
        temperature_k=config.TEMPERATURE_K,
        fluence=config.FLUENCE,
        alpha=config.ALPHA,
        vmin=config.REVERSE_VOLTAGE_MIN,
        vmax=config.REVERSE_VOLTAGE_MAX,
        points=config.REVERSE_VOLTAGE_POINTS,
    )
    r = run_simulation(p)

    print("=" * 60)
    print("RADIATION DAMAGE SIMULATOR")
    print("=" * 60)
    print(f"Material               : {r.detector.material.name}")
    print(f"Thickness              : {p.thickness_um:g} um")
    print(f"Area                   : {p.area_cm2:g} cm^2")
    print(f"Effective doping       : {p.doping_cm3:.3e} cm^-3")
    print(f"Temperature            : {p.temperature_k:.2f} K")
    print(f"Fluence                : {p.fluence:.3e} neq/cm^2")
    print(f"Full depletion voltage : {r.full_depletion_voltage:.4f} V")
    print(f"Final depletion width  : {r.depletion_width_cm[-1] * 1e4:.4f} um")
    print(f"Final capacitance      : {r.capacitance_f[-1] * 1e12:.4f} pF")
    print(f"Final leakage current  : {r.leakage_a[-1]:.6e} A")


def main():
    if "--cli" in sys.argv:
        run_cli()
    else:
        from gui.app import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
