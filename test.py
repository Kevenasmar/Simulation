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
    
    b1 = Barre(mass = 1, p0 = V3D(30,30,0),t0=radians(45), long = 10)
    U.addEntity(b1)

    # Forces
    gravity = Gravity()
    U.addGenerators(gravity)


    #Pour voir la simulation
    U.simulateRealTime()


    

