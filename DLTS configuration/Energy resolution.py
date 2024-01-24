"""This is a simple tool to calculate the relation between the density of the state and the resolution of the energy

"""
import scipy.constants as C
import numpy as np


"""
def Energy_resolution(Energy_level:float, Concentration):
    # The unit of the state of the density of the state: cm^-3
    Density_state = 1 / pow((C.pi),2) * pow( 2*C.electron_mass/(C.hbar*C.hbar) , 1.5) * pow (C.electron_volt*Energy_level,0.5) / 1e6
    Fermi_level = pow(C.hbar,2)/(2*C.electron_mass) * pow(3*pow((C.pi),2) * Concentration  *1e6, 2/3)
    print(Fermi_level/C.electron_volt)
    Voltage_applied = Concentration * C.electron_volt * 10e-9 / (100e-12)
    print(Voltage_applied)
    energy_change = (C.k * 300 * np.log(1e7))/C.electron_volt * 1000
    print("Energy change equals to %f" % energy_change)
    voltage = 1000
    Energy_creation = 7.7 * C.electron_volt
    E_pulser = voltage * Energy_creation * 1 / C.electron_volt
    print(C.elementary_charge)
    print(E_pulser)
"""

def emission_rate(Temp):
    episilon_1 =100  #Minority carrier capture cross section in cm^2
    v_th = np.sqrt(8 * C.k * Temp/( C.pi* C.electron_mass))* 100 # The thermal velocity in cm/s
    print(C.k , C.electron_mass)
    print("Velocity is %.2g" % v_th)
    N_1 = 10^14 #  The effective density of the states
    g_degen = 1 # The degeneracy of the trap
    E_delta = 0.2 * C.electron_volt # The energy separation between the tarap and the minority carrier band edge
    #Temp = 300  # Temperature of the sample in degree celsius.

    emission = episilon_1 * v_th * N_1 / g_degen *np.exp(-1*E_delta/(C.k * Temp))
    print(emission)
    return emission

emission_rate(300)






