"""This is a demo to show how to calculate the signal from the acquired DLTS data from DLTS_config program."""

from DLTS_config import DLTS_exp
import numpy as np
import scipy.constants as C
from sympy import *
device_id = "dev4625"
frequency = 1e6
amp_AC = 0.05
amp_pulse = 1.8
TC = 1e-6
Rate_DT = 800e3
Duration_pulse = 0.001
Duty_cycle_pulse = 0.1
Window_burst = 700e-6
Percent_relaxation = 0.8
args = [device_id,
        frequency,
        amp_AC,
        amp_pulse,
        TC, Rate_DT,
        Duration_pulse,
        Duty_cycle_pulse,
        Window_burst,
        Percent_relaxation]

result = DLTS_exp.DLTS_setting(*args)


def DLTS_tau():
    C_delta = max(result[1]) - min(result[1])
    #print(C_delta)
    C_tau = max(result[1]) - C_delta * (np.e-1) / np.e
    difference_C = np.absolute(result[1]-C_tau)
    index = difference_C.argmin()
    #print(index)
    #print(result[1][index])
    #print(result[0][index])
    tau = result[0][index] - Window_burst * (1-Percent_relaxation)
    #print(tau)
    return tau



class DLTS_processing():

    def DLTS_signal(rate_T1:float,rate_T2:float):
        tau = DLTS_tau()
        t_1 = tau * rate_T1
        t_2 = t_1 * rate_T2

        C_delta = max(result[1])-min(result[1])

        print("The delta C equals to %.5g Farad" % C_delta)
        print("Tau equals to  %.3g s, T1 equals to %.3g s, T2 equals to %.3g s." % (tau, t_1 , t_2))

        C_DLTS = C_delta * (np.exp(-1 * t_1/tau)-np.exp(-1 * t_2/tau))
        print("The DLTS signal equals to %.5g Farad." % C_DLTS)

    def emission_rate_window(rate_T1:float,rate_T2:float):
        tau = DLTS_tau()
        t_1 = tau * rate_T1
        t_2 = t_1 * rate_T2
        e_rate = np.log(t_2/t_1)/(t_2-t_1)
        print("The emission rate is %.5f" % e_rate)


    def emission_rate(Temp:float):
        episilon_1 =100  #Minority carrier capture cross section in cm^2
        v_th = np.sqrt(8*C.k*Temp/(C.pi*C.electron_mass))* 100 # The thermal velocity in cm/s
        print("Velocity is %.2g" % v_th)
        N_1 = 10^14 #  The effective density of the states, need database
        g_degen = 1 # The degeneracy of the trap
        E_delta = 0.2 * C.electron_volt # The energy separation between the tarap and the minority carrier band edge,unit:eV
        #Temp = 300  # Temperature of the sample in degree celsius.

        emission = episilon_1 * v_th * N_1 / g_degen *np.exp(-1*E_delta/(C.k * Temp))
        print(emission)
        return emission


class Equations_Semicon():

    def Energy_k(wavelength:float):
        E_K = C.hbar**2 * pow ((2*C.pi/wavelength),2)/(2*C.electron_mass)
        return E_K


    def density_Energy(Energy:float):
        g_E = 8 * C.pi * np.sqrt(2)/pow(C.h,3)* pow( C.electron_mass,2) * np.sqrt(Energy)
        return g_E

    def density_conductance_Energy(Energy:float , Energy_c:float):
        g_c_E = 8 * C.pi * np.sqrt(2) / pow(C.h, 3) * pow(C.electron_mass, 2) * np.sqrt(Energy-Energy_c)
        return g_c_E

    def density_valence_Energy(Energy:float , Energy_v:float):
        g_v_E = 8 * C.pi * np.sqrt(2) / pow(C.h, 3) * pow(C.electron_mass, 2) * np.sqrt(Energy-Energy_v)
        return g_v_E


    def prob_f_E(Energy:float, level_fermi:float,T:float):
        f_E = 1 /(1 + np.exp((Energy-level_fermi)/(C.k*T)))
        return f_E

    def prob_E_donor (Energy_donor:float, level_fermi:float, T:float):
        f_prob_donor_E = 1 / (1 + 0.5 * np.exp((Energy_donor - level_fermi) / (C.k * T)))
        return f_prob_donor_E

    def prob_E_acceptor(Energy:float, level_fermi:float,T:float):
        f_prob_acceptor_E = 1/ (np.exp((Energy-level_fermi)/(C.k*T)))
        return f_prob_acceptor_E

    def n_E(Energy:float, Energy_c:float, level_fermi:float, T:float):
        g_c_E = Equations_Semicon.density_conductance_Energy(Energy, Energy_c)
        f_E = Equations_Semicon.prob_f_E(Energy, level_fermi,T)
        return (g_c_E * f_E)

    def p_E(Energy:float, Energy_v:float, level_fermi:float, T:float):
        g_v_E = Equations_Semicon.density_valence_Energy(Energy,Energy_v)
        f_E = Equations_Semicon.prob_f_E(Energy, level_fermi,T)
        return (g_v_E * (1-f_E))




#DLTS_processing.DLTS_signal(5,5)
#DLTS_processing.emission_rate_window(5,5)
DLTS_processing.emission_rate(300)
