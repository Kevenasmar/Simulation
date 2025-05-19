from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *


if __name__ == "__main__":
    U = Univers(game=True)

    # Particule fixe : centre de rotation
    p = Particule(fix=True, p0 = V3D(40,50,0))
    U.addEntity(p)
    
    b = Barre(mass = 1, p0 = V3D(45,50,0),t0 = 0, long = 10)
    U.addEntity(b)

    # Forces
    gravity = Gravity()
    pivot = Pivot(b,p,-1)
    U.addGenerators(gravity, pivot)

    U.simulateRealTime()
    U.plot()