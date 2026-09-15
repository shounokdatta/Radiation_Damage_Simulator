"""Reusable numerical simulation helpers."""
import numpy as np

def voltage_grid(vmin, vmax, step):
    v=np.arange(vmin, vmax+step*0.5, step)
    return v[v<=vmax+1e-12]
