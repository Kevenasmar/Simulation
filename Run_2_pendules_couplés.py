from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
from Particule import Particule
from math import radians

if __name__ == "__main__":
    U = Univers(game=True)

    # === Particules fixes A et B ===
    A = Particule(fix=True, p0=V3D(30, 30, 0), color = "blue")
    B = Particule(fix=True, p0=V3D(70, 30, 0), color = "red")

    U.addEntity(A, B)

    # === Barres pendulaires ===


    b1 = Barre(mass=1, p0=V3D(30, 40, 0), t0=radians(90), long=20, color='blue')
    b2 = Barre(mass=1, p0=V3D(70, 40, 0), t0=radians(90), long=20, color='red')


    U.addEntity(b1, b2)

    # === Forces ===
    gravity = Gravity()

    # Liaison pivot entre le haut de chaque barre et sa particule fixe
    pivotA = Pivot(b1, A, point=-1, k=1000, c=100)
    pivotB = Pivot(b2, B, point=-1, k=1000, c=100)

    # Ressort amorti entre les extrémités inférieures des barres (point = +1)
    link = SpringDamperBarre(b1, 1, b2, 1, k=10, c=0.1)
    U.addGenerators(link)

    force = 


    # Ajouter au simulateur
    U.addGenerators(gravity, pivotA, pivotB, link)

    # === Lancer la simulation temps réel ===
    U.simulateRealTime()
