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

    b1 = Barre(mass=1, p0= V3D(45,40), fix = True)
    b2 = Barre(mass=1, p0=V3D(50,40), t0=np.radians(0))
    U.addEntity(b1, b2)

    pivot = PivotBarre(b1,0,b2,-1)
    U.addGenerators(Gravity(),pivot)


    U.simulateRealTime()