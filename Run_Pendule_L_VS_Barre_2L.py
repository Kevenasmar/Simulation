from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
import matplotlib.pyplot as plt
from Particule import Particule
from math import atan2, degrees
from scipy.signal import find_peaks
import numpy as np

if __name__ == "__main__":
    # Listes pour stocker les angles mesurés et le temps
    theta_p2p3 = []     # Angle du pendule (formé par les particules A et B)
    theta_barre = []    # Angle de la barre rigide
    time_tab = []       # Temps associé à chaque mesure

    # Création de l’univers de simulation avec affichage Pygame
    U = Univers(game=True)

    # Création des particules
    C = Particule(fix=True, p0=V3D(30, 30, 0))   # Point de fixation de la barre rigide
    A = Particule(fix=True, p0=V3D(60, 30, 0))   # Point fixe du pendule ressort
    B = Particule(fix=False, p0=V3D(65, 30, 0))  # Masse mobile du pendule
    U.addEntity(C)
    U.addEntity(A)
    U.addEntity(B)

    # Création de la barre rigide fixée en C
    b1 = Barre(mass=1, p0=V3D(30, 30, 0), t0=0, long=10)
    U.addEntity(b1)

    # Ajout des forces
    gravity = Gravity()                     # Force de gravité
    pivot = Pivot(b1, C, -1, k=1000, c=100) # Liaison pivot entre barre et point C
    link = Link(A, B)                       # Liaison ressort entre A et B
    U.addGenerators(gravity, pivot, link)

    # # === MODE 1 : Visualisation temps réel ===
    # # Décommentez cette ligne pour visualiser l’oscillation dans la fenêtre Pygame :
    # U.simulateRealTime()

    # # === MODE 2 : Mesure des périodes d’oscillation ===
    # # Décommentez les lignes suivantes pour mesurer la période des deux systèmes :

    for _ in range(15000):  # Durée de simulation (~15 s avec step = 0.001)
        U.simulateAll()

        # Vecteurs position pour calcul des angles
        v1 = B.getPosition() - A.getPosition()
        v2 = b1.getPosition() - C.getPosition()

        # Calcul des angles (en degrés) par rapport à la verticale
        theta1 = degrees(atan2(v1.x, v1.y))     # Pendule particules
        theta2 = degrees(atan2(v2.x, v2.y))     # Barre rigide

        # Enregistrement des données
        theta_p2p3.append(theta1)
        theta_barre.append(theta2)
        time_tab.append(U.time[-1])

    # === Affichage des courbes des angles en fonction du temps ===
    plt.figure(figsize=(12, 8))
    plt.plot(time_tab, theta_p2p3, label="θ1(t) (pendule)")
    plt.plot(time_tab, theta_barre, label="θ2(t) (barre rigide)")
    plt.xlabel("Temps (s)")
    plt.ylabel("Angle (°)")
    plt.title("Comparaison des angles θ1(t) et θ2(t)")
    plt.legend()
    plt.grid()
    plt.show()

    # === Analyse des périodes par détection des pics ===
    theta1_array = np.array(theta_p2p3)
    theta2_array = np.array(theta_barre)
    time_array = np.array(time_tab)

    # Détection des pics (maxima locaux)
    peaks1, _ = find_peaks(theta1_array)
    peaks2, _ = find_peaks(theta2_array)

    # Extraction des temps associés
    times1 = time_array[peaks1]
    times2 = time_array[peaks2]

    # Calcul des périodes moyennes
    T1 = np.mean(np.diff(times1)) if len(times1) > 1 else float('nan')
    T2 = np.mean(np.diff(times2)) if len(times2) > 1 else float('nan')
    delta = np.abs(T2 - T1)

    # Affichage console
    print(f"Période θ1 (pendule)   : {T1:.3f} s")
    print(f"Période θ2 (barre)     : {T2:.3f} s")
    print(f"Différence ΔT          : {delta:.3f} s")
