"""
Radiation Damage Simulator
Main entry point.

Run GUI:
    python main.py

Run CLI:
    python main.py --cli
"""

import sys
import config

from gui.simulator import SimulationParameters, run_simulation


def run_cli():
    """Run a default simulation from the command line."""

    parameters = SimulationParameters(
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

    result = run_simulation(parameters)

    print("=" * 60)
    print("RADIATION DAMAGE SIMULATOR")
    print("=" * 60)

    print(f"Material               : {result.detector.material.name}")
    print(f"Thickness              : {parameters.thickness_um:g} um")
    print(f"Area                   : {parameters.area_cm2:g} cm^2")
    print(f"Effective doping       : {parameters.doping_cm3:.3e} cm^-3")
    print(f"Temperature            : {parameters.temperature_k:.2f} K")
    print(f"Fluence                : {parameters.fluence:.3e} neq/cm^2")
    print(
        f"Full depletion voltage : "
        f"{result.full_depletion_voltage:.4f} V"
    )
    print(
        f"Final depletion width  : "
        f"{result.depletion_width_cm[-1] * 1e4:.4f} um"
    )
    print(
        f"Final capacitance      : "
        f"{result.capacitance_f[-1] * 1e12:.4f} pF"
    )
    print(
        f"Final leakage current  : "
        f"{result.leakage_a[-1]:.6e} A"
    )


def main():
    """Application entry point."""

    if "--cli" in sys.argv:
        run_cli()
        return

    # IMPORTANT:
    # Import gui.app as a PACKAGE, not as a standalone script.
    from gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()