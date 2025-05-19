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
    theta_p2p3 = []
    theta_barre = []
    time_tab = []
 
    U = Univers(game=True)

    # Particule fixe : centre de rotation
    C = Particule(fix=True, p0 = V3D(30,30,0))
    A = Particule(fix=True, p0 = V3D(60,30,0))
    B = Particule(fix=False, p0 = V3D(65,30,0))
    U.addEntity(C)
    U.addEntity(A)
    U.addEntity(B)
    
    b1 = Barre(mass = 1, p0 = V3D(35,30,0),t0 = 0, long = 10)
    U.addEntity(b1)

    # Forces
    gravity = Gravity()
    pivot = Pivot(b1,C,-1,k=1000, c= 100)
    link = Link(A,B)
    U.addGenerators(gravity, pivot, link)


    #Pour voir la simulation
    # U.simulateAll()


    #Pour voir le graphes theta(t)
    # Simulation manuelle pour enregistrer les angles
    for _ in range(15000): # CHANGER LE TEMPS SI NECESSAIRE
        U.simulateAll()

        v1 = B.getPosition() - A.getPosition()
        v2 = b1.getPosition() - C.getPosition()
        theta1 = degrees(atan2(v1.x, v1.y))
        theta2 = degrees(atan2(v2.x, v2.y))
    
    
        theta_p2p3.append(theta1)
        theta_barre.append(theta2)
        time_tab.append(U.time[-1])



    plt.figure(figsize=(12,8))
    plt.plot(time_tab, theta_p2p3, label="θ1(t) (AB)")
    plt.plot(time_tab, theta_barre, label="θ2(t) (barre b1)")
    plt.xlabel("Temps (s)")
    plt.ylabel("Angle (°)")
    plt.title("Angles θ1(t) et θ2(t)")
    plt.legend()
    plt.grid()
    plt.show()

    # Convertir en tableau numpy
    theta1_array = np.array(theta_p2p3)
    theta2_array = np.array(theta_barre)
    time_array = np.array(time_tab)

    # Trouver les pics (maxima locaux)
    peaks1, _ = find_peaks(theta1_array)
    peaks2, _ = find_peaks(theta2_array)

    # Extraire les temps associés
    times1 = time_array[peaks1]
    times2 = time_array[peaks2]

    # Calculer les différences de temps entre pics successifs
    T1 = np.mean(np.diff(times1)) if len(times1) > 1 else float('nan')
    T2 = np.mean(np.diff(times2)) if len(times2) > 1 else float('nan')
    delta = np.abs(T2 - T1)

    # Affichage des périodes
    print(f"Période θ1 (AB): {T1:.3f} s")
    print(f"Période θ2 (barre): {T2:.3f} s")
    print(f"dT = {delta:.3f} s")

