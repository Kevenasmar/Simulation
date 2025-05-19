from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
from Particule import Particule
from math import radians
import pygame

if __name__ == "__main__":
    U = Univers(game=True)

    # === Particules fixes A et B ===
    A = Particule(fix=True, p0=V3D(30, 30, 0), color="blue")
    B = Particule(fix=True, p0=V3D(70, 30, 0), color="red")
    U.addEntity(A, B)

    # === Barres pendulaires ===
    b1 = Barre(mass=1, p0=V3D(30, 40, 0), t0=radians(90), long=20, color='blue')
    b2 = Barre(mass=1, p0=V3D(70, 40, 0), t0=radians(90), long=20, color='red')
    U.addEntity(b1, b2)

    # === Forces ===
    gravity = Gravity()
    pivotA = Pivot(b1, A, point=-1, k=1000, c=100)
    pivotB = Pivot(b2, B, point=-1, k=1000, c=100)
    link = SpringDamperBarre(b1, 1, b2, 1, k=5, c=0.1)

    # Force à activer dynamiquement (sur appui ESPACE)
    force = ForceSelectBarre(V3D(10, 0, 0), b1, 1, active = False)
    force2 = ForceSelectBarre(V3D(-10,0,0), b2, 1, active = False)

    # Ajout au simulateur
    U.addGenerators(gravity, pivotA, pivotB, link, force, force2)

    # Interaction clavier (appui sur ESPACE)
    def interaction(events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                force.active = True
                force2.active = True
                print("Forces activées !")

    # Injecter la fonction d’interaction
    U.gameInteraction = interaction

    # === Lancer la simulation Pygame ===
    U.simulateRealTime()
