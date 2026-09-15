import numpy as np
def logarithmic_values(initial, final, steps): return np.geomspace(initial, final, int(steps))
def linear_values(initial, final, steps): return np.linspace(initial, final, int(steps))
