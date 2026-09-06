# Radiation Damage Simulator

A Python-based Silicon Detector Radiation Damage Simulator with an interactive GUI.

## Features

The simulator provides:

- Capacitance vs Reverse Bias
- Leakage Current vs Reverse Bias
- Capacitance and Leakage Current vs Reverse Bias
- Capacitance vs Reverse Bias for Different Doping Concentrations
- Leakage Current vs Reverse Bias for Different Doping Concentrations
- Capacitance vs Reverse Bias for Different Detector Thicknesses
- Leakage Current vs Reverse Bias for Different Detector Thicknesses
- Capacitance vs Reverse Bias for Different Operating Temperatures
- Leakage Current vs Reverse Bias for Different Operating Temperatures

The GUI reads the current values entered by the user and recalculates the simulation when **UPDATE GRAPH** is pressed. An optional Auto Update mode is also available.

## Project Structure

```
Radiation_Damage_Simulator/
│
├── main.py
├── config.py
├── constants.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── analysis/
│   ├── __init__.py
│   └── plots.py
│
├── detector/
│   ├── __init__.py
│   └── leakage_current.py
│
├── gui/
│   ├── __init__.py
│   ├── app.py
│   └── simulator.py
│
├── materials/
│   ├── __init__.py
│   └── silicon.py
│
├── physics/
│   ├── __init__.py
│   └── detector.py
│
├── tests/
│   ├── __init__.py
│   ├── test_detector.py
│   └── test_leakage_current.py
│
└── output/
    ├── graphs/
    └── data/
```

## Requirements

**Recommended Python version:** Python 3.11 or newer

**Python packages:**
- numpy>=1.24
- matplotlib>=3.7
- pandas>=2.0
- pytest>=7.4

*Tkinter is normally included with the standard Windows Python installation.*

## Installation on Windows

### 1. Open PowerShell

Go to the project directory.

Example:
```powershell
cd "C:\Users\S\Downloads\Radiation_Damage_Simulator_complete\Radiation_Damage_Simulator_complete"
```

Replace the path with your actual project location.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

If `.venv` already exists, skip this command.

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

The terminal should then look similar to:
```
(.venv) PS C:\Users\S\Downloads\Radiation_Damage_Simulator_complete\Radiation_Damage_Simulator_complete>
```

If PowerShell blocks the script, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install all dependencies

Use:
```powershell
python -m pip install -r requirements.txt
```

Or install them directly:
```powershell
python -m pip install numpy matplotlib pandas pytest
```

**Do not upgrade the global Python installation just to run this project.**

## Verify the Installation

**Check which Python is being used:**
```powershell
python -c "import sys; print(sys.executable)"
```

The result should contain: `.venv\Scripts\python.exe`

**Check the required packages:**
```powershell
python -c "import numpy, matplotlib, pandas; print('Dependencies installed successfully')"
```

**Check versions:**
```powershell
python -c "import numpy, matplotlib, pandas; print('NumPy:', numpy.__version__); print('Matplotlib:', matplotlib.__version__); print('Pandas:', pandas.__version__)"
```

## Run the GUI

The GUI is the main application.

Run:
```powershell
python -m gui.app
```

or:
```powershell
python main.py
```

The GUI should open with the simulation controls and graph area.

## Using the GUI

The GUI contains input fields for:

- **Detector Parameters:**
  - Thickness (µm)
  - Area (cm²)
  - Effective doping (cm⁻³)
  - Built-in voltage (V)
  - Temperature (K)

- **Radiation Damage:**
  - Initial fluence
  - Final fluence
  - Damage constant alpha

- **Voltage Range:**
  - Minimum reverse voltage
  - Maximum reverse voltage
  - Voltage step

The GUI also provides comparison-value fields for:
- Doping
- Thickness
- Temperature

### Update the Simulation

1. Enter your values
2. Select the graph
3. Press **UPDATE GRAPH**

The calculation flow is:
```
Current GUI Input
       ↓
Detector Parameters
       ↓
Depletion Width
       ↓
Capacitance
       ↓
Leakage Current
       ↓
Graph Redraw
       ↓
Result Values Update
```

The GUI also has an **Auto update while editing** option. When enabled, the graph is recalculated automatically after input changes.

## Recommended First Test

Use these parameters:

```
Thickness       = 300
Area            = 1.0
Doping          = 1e15
Built-in Voltage = 0.70

Temperature     = 293.15

Initial Fluence = 1e12
Final Fluence   = 1e16
Alpha           = 4e-17

Minimum Voltage = 0
Maximum Voltage = 500
Voltage Step    = 5
```

Select: **Capacitance vs Reverse Bias** and press **UPDATE GRAPH**

Then change: `Doping = 1e14` and press **UPDATE GRAPH** again.

The graph should be recalculated using the new input.

## Comparison Studies

### Doping Study

Example values: `1e14, 1e15, 1e16, 1e17, 1e18`

Graphs:
- Capacitance vs Doping
- Leakage Current vs Doping

### Thickness Study

Example values: `50, 100, 150, 200, 250, 300, 500`

Graphs:
- Capacitance vs Thickness
- Leakage Current vs Thickness

### Temperature Study

Example values: `253.15, 273.15, 288.15, 300.15, 313.15`

Graphs:
- Capacitance vs Temperature
- Leakage Current vs Temperature

## Save Graphs

Use: **SAVE GRAPH**

Available formats:
- PNG
- PDF
- SVG

Graphs are normally stored in: `output/graphs/`

## Export Simulation Data

Use: **EXPORT CSV**

The exported data contains:
- Reverse Bias (V)
- Depletion Width (um)
- Capacitance (pF)
- Leakage Current (mA)

Data is normally stored in: `output/data/`

## Run Tests

Run:
```powershell
pytest -q
```

The tests check detector and leakage-current behavior such as:
- depletion width limits
- positive capacitance
- non-negative full-depletion voltage
- fluence dependence
- temperature dependence

## Command-Line Mode

To run the simulator without the GUI:

```powershell
python main.py --cli
```

This prints the simulation parameters and final calculated values in the terminal.

## Configuration

`config.py` contains the default values used when the program starts and when **RESET DEFAULTS** is selected.

Example:
```python
THICKNESS_UM = 300.0
AREA_CM2 = 1.0

N_EFF = 1e15
V_BI = 0.70

TEMPERATURE_K = 293.15

INITIAL_FLUENCE = 1e12
FINAL_FLUENCE = 1e16

ALPHA = 4e-17

REVERSE_VOLTAGE_MIN = 0.0
REVERSE_VOLTAGE_MAX = 500.0
REVERSE_VOLTAGE_STEP = 5.0
```

**Important:** `config.py` provides defaults only. When the user changes a value in the GUI, the current GUI value is passed to the simulation. The program does not need to modify `config.py`.

## Physics Model

**Detector depletion width:**
```
W = sqrt[
    2 * epsilon * (V_R + V_BI)
    ─────────────────────────
           q * N_eff
]
```

The depletion width is limited by the physical detector thickness.

**Capacitance:**
```
C = epsilon * A / W
```

**Radiation-induced leakage current:**
```
I = alpha * fluence * depleted_volume

where: depleted_volume = area * depletion_width
```

The leakage-current model also supports the temperature dependence used by the temperature study.

## Troubleshooting

### NumPy is not found

Activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

Then:
```powershell
python -m pip install numpy
```

### Matplotlib is not found

```powershell
python -m pip install matplotlib
```

### Pandas is not found

```powershell
python -m pip install pandas
```

### Pytest is not found

```powershell
python -m pip install pytest
```

### VS Code says "Import could not be resolved"

1. Open: `Ctrl + Shift + P`
2. Select: **Python: Select Interpreter**
3. Choose: `.venv\Scripts\python.exe`
4. Do not select the global: `C:\Python311\python.exe`

## Quick Start

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m gui.app
```

Run tests:
```powershell
pytest -q
```

Run command-line mode:
```powershell
python main.py --cli
```

## Git

**Do not commit:**
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`

These should be excluded by `.gitignore`.

**Typical Git commands:**
```powershell
git status
git add .
git commit -m "Update radiation damage simulator"
git push
```

## Future Improvements

Possible future additions:
- Multiple detector-material models
- Radiation type selection
- Bias-voltage slider
- Additional radiation-damage models
- Improved temperature-dependent semiconductor physics
- Batch simulation
- Automatic report generation
- GUI dashboard
- Interactive parameter studies
