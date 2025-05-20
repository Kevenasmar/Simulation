from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
import matplotlib.pyplot as plt
from Particule import Particule
from math import atan2, radians
from scipy.signal import find_peaks
import numpy as np

if __name__ == "__main__":

    U = Univers(game=True)

    p1 = Particule(p0=V3D(50,60),fix=True)
    b1 = Barre(mass = 1, p0=V3D(45,40))
    # Ajout des entités
    U.addEntity(p1, b1)

    # Liaison glissière le long de l'axe horizontal
    glissiere = GlissiereBarreParticule(b1, p1, axis=V3D(1, 0, 0))
    force = ForceSelectBarre(V3D(5,0,0),b1,-1)
    U.addGenerators(glissiere)

    U.simulateRealTime()