import numpy as np
import matplotlib.pyplot as plt
import pygame
from Classes.vector3D import Vector3D as v
from Classes.MoteurCC import MoteurCC


if __name__ =="__main__":
    
    # Motor parameters
    R = 1.0      # Armature resistance [Ohm]
    L = 0.001    # Armature inductance [H] ≈ 0
    k_c = 0.01   # Torque constant [Nm/A]
    k_e = 0.01   # Back EMF constant [V.s]
    J = 0.01     # Rotor inertia [kg.m²]
    f = 0.1      # Internal viscous friction [Nms]
    Um = 1.0     # Voltage across the motor [V]

    # External parameters (set to 0 if not needed)
    load_inertia = 0.005           # Load inertia [kg.m²]
    external_torque = 0.002        # Constant external torque [Nm]
    viscosity = 0.05               # Medium viscosity [Nms]

    # Create the motor
    moteur = MoteurCC(R, L, k_c, k_e, J, f)
    moteur.setLoadInertia(load_inertia)
    moteur.setExternalTorque(external_torque)
    moteur.setViscosity(viscosity)

    # Simulation
    t = 0
    step = 0.01
    temps = [t]
    vitesses_num = [moteur.getSpeed()]

    while t < 2:
        t += step
        moteur.setVoltage(Um)
        moteur.simulate(step)
        temps.append(t)
        vitesses_num.append(moteur.getSpeed())

    # Analytical solution
    temps_array = np.array(temps)
    vitesses_theo = moteur.solution_analytique(temps_array, Um, R, k_c, k_e, J, f)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.axhline(y=0.1, color='gray', linestyle='--', label='Consigne (0.1 rad/s)')
    plt.plot(temps_array, vitesses_theo, label='Solution analytique', linewidth=2)
    plt.plot(temps_array, vitesses_num, '--', label='Simulation numérique')
    plt.xlabel('Temps (s)')
    plt.ylabel('Vitesse Ω(t) [rad/s]')
    plt.title('Comparaison : théorie vs simulation numérique avec enrichissement')
    plt.grid(True)
    plt.legend()
    plt.show()
