# Radiation Damage Simulator

Interactive Python/Tkinter simulator for a reverse-biased planar silicon detector.

## Features

- Depletion width vs reverse bias
- Capacitance vs reverse bias
- Radiation-induced leakage current vs reverse bias
- Doping comparison
- Thickness comparison
- Temperature comparison
- Live/automatic GUI graph updates
- CSV export and graph saving
- Basic tests with pytest

## Physics used

Depletion width:

`W = sqrt(2 eps (Vbi + Vr) / (q Neff))`, limited by detector thickness.

Capacitance:

`C = eps A / W`

Radiation-induced leakage at reference temperature:

`I = alpha * fluence * A * W`

Temperature scaling is applied relative to 293.15 K using a standard silicon leakage-current scaling factor proportional to `T^2 exp(-Eg/(2 k T))`.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run GUI

```powershell
python main.py
```

or

```powershell
python -m gui.app
```

## Run command-line summary

```powershell
python main.py --cli
```

## Run tests

```powershell
pytest -q
```
