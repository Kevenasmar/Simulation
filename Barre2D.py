import numpy as np
from vector3D import Vector3D as V3D
import matplotlib.pyplot as plt
from Forces import *

class Barre:
    """
    Représente une barre rigide 2D soumise à des forces,
    pouvant se déplacer et tourner librement sauf si fixée.
    """

    def __init__(self, mass=1, p0=V3D(), v0=V3D(), a0=V3D(), t0=0.0, o0=0.0, alpha0=0.0, long=10, fix=False, name="barre", color='red'):
        # Paramètres physiques
        self.mass = mass              # kg
        self.L = long                 # Longueur de la barre (unités simulation)
        self.name = name
        self.color = color
        self.fix = fix                # Si True, la barre est immobile

        # Initialisation de la position centrale
        angle = t0
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)
        p_centre = p0 + (self.L / 2) * dir_barre
        self.position = [p_centre]

        # État de translation (vecteurs par pas de temps)
        self.speed = [v0]            # Vitesse (m/s)
        self.acceleration = [a0]     # Accélération (m/s²)

        # État de rotation (scalaires par pas de temps)
        self.theta = [t0]            # Orientation (rad)
        self.omega = [o0]            # Vitesse angulaire (rad/s)
        self.alpha = [alpha0]        # Accélération angulaire (rad/s²)

        # Forces externes appliquées : liste de tuples (force, point)
        self.forces = []

    def applyForce(self, force, point):
        """
        Applique une force en un point relatif à la barre (entre -1 et 1).
        """
        if not isinstance(force, V3D):
            raise ValueError("force doit être un V3D")
        if not -1 <= point <= 1:
            raise ValueError("point doit être dans [-1, 1]")
        self.forces.append((force, point))

    def getInertia(self):
        """
        Retourne le moment d'inertie (I) d'une barre centrée de masse m et de longueur L.
        """
        return (1 / 12) * self.mass * self.L**2

    def getPoint(self, alpha):
        """
        Renvoie la position réelle d'un point sur la barre donné par alpha ∈ [-1, 1].
        """
        return self.position[-1] + V3D(alpha * self.L / 2, 0).rotZ(self.theta[-1])

    # Accesseurs (état courant)
    def getPosition(self): 
        return self.position[-1]
    
    def getSpeed(self): 
        return self.speed[-1]
    
    def getAngle(self): 
        return self.theta[-1]
    
    def getAngularSpeed(self): 
        return self.omega[-1]

    def simulate(self, step):
        """
        Simule un pas de temps d'intégration (en s).
        """
        self.pfd(step)

    def pfd(self, step):
        """
        Applique le principe fondamental de la dynamique (PFD) pour calculer
        l'évolution de la position et de l'orientation de la barre.
        """

        if self.fix:
            # Si la barre est fixée : aucun mouvement
            self.acceleration.append(V3D())
            self.speed.append(V3D())
            self.position.append(self.position[-1])
            self.alpha.append(0.0)
            self.omega.append(0.0)
            self.theta.append(self.theta[-1])
            return

        total_force = V3D()
        total_moment = 0.0
        dir_barre = V3D(np.cos(self.theta[-1]), np.sin(self.theta[-1]), 0)

        # Somme des forces et moments
        for (f, p_rel) in self.forces:
            total_force += f
            r = (p_rel * self.L / 2) * dir_barre
            moment = r.x * f.y - r.y * f.x  # produit vectoriel 2D
            total_moment += moment

        # Translation : position et vitesse linéaire
        a = total_force * (1 / self.mass)
        v = self.speed[-1] + a * step
        p = self.position[-1] + self.speed[-1] * step + 0.5 * a * step**2

        self.acceleration.append(a)
        self.speed.append(v)
        self.position.append(p)

        # Rotation : angle et vitesse angulaire
        alpha = total_moment / self.getInertia()
        omega = self.omega[-1] + alpha * step
        theta = self.theta[-1] + self.omega[-1] * step + 0.5 * alpha * step**2

        self.alpha.append(alpha)
        self.omega.append(omega)
        self.theta.append(theta)

        # Nettoyage des forces pour le prochain pas
        self.forces = []

    def plot(self):
        """
        Trace la trajectoire du centre de la barre (matplotlib).
        """
        from pylab import plot
        X = [pos.x for pos in self.position]
        Y = [pos.y for pos in self.position]
        return plot(X, Y, color=self.color, label=self.name) + plot(X[-1], Y[-1], 'o', color=self.color)

    def gameDraw(self, scale, screen):
        """
        Affichage graphique dans Pygame (barre + vitesse linéaire).
        """
        import pygame
        if not screen:
            return

        angle = self.getAngle()
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)
        
        # Calcul des extrémités
        pos_left = self.getPosition() - (self.L / 2) * dir_barre
        pos_right = self.getPosition() + (self.L / 2) * dir_barre

        x1 = int(pos_left.x * scale)
        y1 = int(pos_left.y * scale)
        x2 = int(pos_right.x * scale)
        y2 = int(pos_right.y * scale)

        # Vecteur vitesse au centre
        VX = int(scale * self.getSpeed().x)
        VY = int(scale * self.getSpeed().y)
        Xc = int(self.getPosition().x * scale)
        Yc = int(self.getPosition().y * scale)

        # Dessin
        pygame.draw.line(screen, pygame.Color(self.color), (x1, y1), (x2, y2), width=4)
        pygame.draw.circle(screen, pygame.Color(self.color), (Xc, Yc), 5)
        pygame.draw.line(screen, 'blue', (Xc, Yc), (Xc + VX, Yc + VY), 3)
