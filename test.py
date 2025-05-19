from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *


# === MAIN SIMULATION ===
if __name__ == "__main__":
    U = Univers(game=True)

    #Entités dans mon univers
    barre = Barre(mass = 1, long = 10, theta = 0, pos = V3D(50,50,0), fixed = False, color = 'red', nom = 'barre1')
    U.addEntity(barre)

    p = Particule(mass = 1, p0 = V3D(30,50,0))
    U.addEntity(p)

    # Forces dans mon univers
    gravity = Gravity()
    U.addGenerators(gravity)

    U.addEntity(barre)
    U.simulateRealTime()
    U.plot()