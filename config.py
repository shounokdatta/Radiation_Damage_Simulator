# ============================================================
# SILICON DETECTOR SIMULATION CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# Detector type
# ------------------------------------------------------------

DETECTOR_TYPE = "N+ - P Silicon Detector"

BULK_TYPE = "P-type"


# ------------------------------------------------------------
# Silicon parameters
# ------------------------------------------------------------

# P-type bulk doping concentration
Nd = 1e15                 # cm^-3

# Temperature
T = 300                   # K

# Silicon bandgap
Eg = 1.12                 # eV

# Built-in voltage
Vbi = 0.70                # V


# ------------------------------------------------------------
# Detector geometry
# ------------------------------------------------------------

# Detector thickness
THICKNESS_UM = 300        # µm

# Detector area
AREA_CM2 = 1.0            # cm²


# ------------------------------------------------------------
# Reverse bias voltage sweep
# ------------------------------------------------------------

REVERSE_VOLTAGE_MIN = 0

REVERSE_VOLTAGE_MAX = 500

REVERSE_VOLTAGE_STEP = 5