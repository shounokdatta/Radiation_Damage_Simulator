from constants import K_B_EV, EG_SI, T_REF_K
import numpy as np
def temperature_factor(T):
    return (T/T_REF_K)**2*np.exp((-EG_SI/(2*K_B_EV))*(1/T-1/T_REF_K))
