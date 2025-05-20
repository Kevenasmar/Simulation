import numpy as np
import matplotlib.pyplot as plt
import pygame
from vector3D import Vector3D as v
from MoteurCC import MoteurCC

if __name__ == "__main__":

    # === Paramètres physiques du moteur ===
    R = 1.0       # Résistance de l'induit [Ohm]
    L = 0.001     # Inductance de l'induit [H] ≈ 0 (peut être négligée)
    k_c = 0.01    # Constante de couple [Nm/A]
    k_e = 0.01    # Constante de force contre-électromotrice [V.s/rad]
    J = 0.01      # Inertie du rotor [kg.m²]
    f = 0.1       # Frottement visqueux interne [N.m.s]
    Um = 1.0      # Tension d'alimentation du moteur [V]

    # === Paramètres extérieurs (enrichissements) ===
    # Ces valeurs peuvent être fixées à 0 pour désactiver les effets externes
    load_inertia = 0.005          # Inertie de la charge [kg.m²]
    external_torque = 0.002       # Couple résistant externe constant [Nm]
    viscosity = 0.05              # Viscosité du milieu extérieur [N.m.s]

    # === Création et configuration du moteur ===
    moteur = MoteurCC(R, L, k_c, k_e, J, f)
    moteur.setLoadInertia(load_inertia)
    moteur.setExternalTorque(external_torque)
    moteur.setViscosity(viscosity)

    # === Simulation numérique ===
    t = 0
    step = 0.01  # Pas de temps
    temps = [t]
    vitesses_num = [moteur.getSpeed()]

    while t < 2:
        t += step
        moteur.setVoltage(Um)          # Application de la tension constante
        moteur.simulate(step)          # Intégration des équations du moteur
        temps.append(t)
        vitesses_num.append(moteur.getSpeed())

    # === Solution analytique (sans les enrichissements) ===
    temps_array = np.array(temps)
    vitesses_theo = moteur.solution_analytique(temps_array, Um, R, k_c, k_e, J, f)

    # === Affichage graphique ===
    plt.figure(figsize=(10, 6))
    plt.axhline(y=0.1, color='gray', linestyle='--', label='Consigne (0.1 rad/s)')
    plt.plot(temps_array, vitesses_theo, label='Solution analytique', linewidth=2)
    plt.plot(temps_array, vitesses_num, '--', label='Simulation numérique (avec enrichissements)')
    plt.xlabel('Temps (s)')
    plt.ylabel('Vitesse Ω(t) [rad/s]')
    plt.title('Comparaison : théorie vs simulation numérique enrichie')
    plt.grid(True)
    plt.legend()
    plt.show()
