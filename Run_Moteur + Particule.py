# === Import des modules nécessaires ===
from random import random, randint                 # (non utilisé ici, mais importé)
from vector3D import Vector3D as V3D               # Vecteur 3D utilisé pour positions et forces
from Particule import Particule                    # Classe de particule libre ou fixe
import pygame                                      # Pour la visualisation en temps réel
from pygame.locals import *                        # Pour les constantes comme QUIT
from types import MethodType                       # (non utilisé ici)
from MoteurCC import MoteurCC                      # Modèle du moteur à courant continu
from Forces import *                               # Toutes les classes de forces (gravité, ressorts, moteur...)
from Barre2D import Barre                          # (non utilisé ici)
import math                                        # Pour les fonctions mathématiques
from Univers_Officiel import Univers               # Classe qui gère les entités et la simulation

# === Point d'entrée principal ===
if __name__ == '__main__':
    from pylab import figure, show, legend         # Pour affichage éventuel (non utilisé ici)

    # === Paramètres physiques du moteur CC ===
    R = 1.0           # Résistance [Ω]
    L = 0.001         # Inductance [H] (supposée négligeable)
    k_c = 0.01        # Constante de couple [Nm/A]
    k_e = 0.01        # Constante de FEM [V/(rad/s)]
    J = 0.01          # Inertie du rotor [kg·m²]
    f = 0.1           # Coefficient de frottement visqueux [Nms/rad]
    Um = 1.0          # Tension appliquée (non utilisée, on utilise directement 220V)
    P = V3D(50, 50, 0)  # Position du moteur sur le plan 2D

    # === Création de l’univers de simulation ===
    monUnivers = Univers(game=True)  # Mode temps réel activé (affichage Pygame)

    # === Création des entités ===
    particule = Particule(p0=V3D(40, 50, 0))         # Particule placée à gauche du moteur
    moteur = MoteurCC(R, L, k_c, k_e, J, f, P)       # Moteur à la position définie
    moteur.setVoltage(220)                          # Tension d'alimentation de 220V

    # === Ajout des entités dans l’univers ===
    monUnivers.addEntity(particule)
    monUnivers.addEntity(moteur)

    # === Définition des forces agissant sur la particule ===
    gravity = Gravity()                                             # Gravité (non utilisée ici)
    bounce_x = Bounce_x()                                           # Rebond mur vertical (non utilisée ici)
    bounce_y = Bounce_y()                                           # Rebond mur horizontal (non utilisée ici)
    force_moteur = ForceMoteur(moteur, particule)                   # Force tangentielle générée par le moteur
    force_ressort = SpringDamperMoteur(moteur, particule, k=50, c=1)  # Liaison élastique moteur-particule

    # === Ajout des forces à l’univers ===
    monUnivers.addGenerators(force_moteur, force_ressort)  # La particule subira ces deux forces

    # === Simulation temps réel avec affichage Pygame ===
    monUnivers.simulateRealTime()
