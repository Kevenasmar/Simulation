from random import random,randint
from vector3D import Vector3D as V3D
from Particule import Particule
import pygame
from pygame.locals import *
from types import MethodType
from MoteurCC import MoteurCC
from Forces import *
from Barre2D import Barre
import math
from Univers_Officiel import Univers

if __name__ == '__main__':
    from pylab import figure, show, legend

    R = 1.0
    L = 0.001
    k_c = 0.01
    k_e = 0.01
    J = 0.01
    f = 0.1
    Um = 1.0
    P = V3D(50, 50, 0)

    monUnivers = Univers(game=True)

    particule = Particule(p0=V3D(40, 50, 0))
    moteur = MoteurCC(R, L, k_c, k_e, J, f, P)
    moteur.setVoltage(220)

    # Ajout des entités
    monUnivers.addEntity(particule)
    monUnivers.addEntity(moteur)

    # Générateurs de forces
    gravity = Gravity()
    bounce_x = Bounce_x()
    bounce_y = Bounce_y()
    force_moteur = ForceMoteur(moteur, particule)
    force_ressort = SpringDamperMoteur(moteur, particule, k = 50, c = 1)

    # Ajout des forces à l’univers
    monUnivers.addGenerators(force_moteur, force_ressort)

    # Plot d(Ω)
    

    # Simulation
    monUnivers.simulateRealTime()
