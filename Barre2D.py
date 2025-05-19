import numpy as np
from vector3D import Vector3D as V3D
import matplotlib.pyplot as plt
from Forces import *

class Barre:
    def __init__(self, mass=1, long=1, theta=0, pos=V3D(), fixed=False, color='red', nom='barre'):
        self.nom = nom
        self.mass = mass
        self.L = long
        self.theta = theta
        self.pos = pos
        self.fixed = fixed
        self.color = color

        self.vel = V3D()      # Vitesse linéaire
        self.acc = V3D()      # Accélération linéaire
        self.omega = 0.0      # Vitesse angulaire
        self.alpha = 0.0      # Accélération angulaire
        self.forces = []

        self.history = []

    def __str__(self):
        msg = 'Barre ('+str(self.mass)+', '+str(self.long)+', '+str(self.theta)+', '+str(self.pos)+', "'+self.name+'", "'+str(self.color)+'" )'
        return msg
    
    def __repr__(self):
        return str(self)
    
    def applyForce(self, force, point):
        if not isinstance(force, V3D):
            raise ValueError("force doit être un vecteur de type Vector3D")
        if not -1 <= point <= 1:
            raise ValueError("point doit être compris entre -1 et 1")
    
        self.forces.append((force, point))


    def getInertia(self):
        return (1/12) * self.mass * self.L**2
    
    def simulate(self,step):
        self.pfd(step)
    

    def pfd(self, step):
        if self.fixed:
            # Si la barre est fixe : pas de mouvement
            self.acc = V3D()
            self.vel = V3D()
            self.alpha = 0.0
            self.omega = 0.0
            return

        # === Initialisation ===
        total_force = V3D()
        total_moment = 0.0
        dir_barre = V3D(np.cos(self.theta), np.sin(self.theta), 0)

        # === Calcul des forces et moments en une seule boucle ===
        for (f, p_rel) in self.forces:
            total_force += f

            # Moment (r × F) où r est la position relative le long de la barre
            r = (p_rel * self.L / 2) * dir_barre
            moment = r.x * f.y - r.y * f.x  # composante z du produit vectoriel
            total_moment += moment

        # === Translation ===
        a = total_force * (1 / self.mass)
        v = self.vel + a * step
        p = self.pos + self.vel * step + 0.5 * a * step**2

        self.acc = a
        self.vel = v
        self.pos = p
        self.history.append(self.pos)

        # === Rotation ===
        alpha = total_moment / self.getInertia()
        omega = self.omega + alpha * step
        theta = self.theta + self.omega * step + 0.5 * alpha * step**2

        self.alpha = alpha
        self.omega = omega
        self.theta = theta

        # === Réinitialisation des forces ===
        self.forces = []



    def plot(self):
        from pylab import plot
        X = []
        Y = []
        for pos in self.history:
            X.append(pos.x)
            Y.append(pos.y)

        return plot(X, Y, color=self.color, label=self.nom) + plot(X[-1], Y[-1], 'o', color=self.color)

    def gameDraw(self, scale, screen):
        import pygame
        if not screen:
            return

        # Position du centre (sans inversion ici)
        cx = self.pos.x * scale
        cy = self.pos.y * scale

        # Longueur en pixels (moitié de chaque côté)
        demi_L = (self.L / 2) * scale
        dx = demi_L * np.cos(self.theta)
        dy = demi_L * np.sin(self.theta)

        # Coordonnées des extrémités
        x1, y1 = int(cx - dx), int(cy - dy)
        x2, y2 = int(cx + dx), int(cy + dy)

        pygame.draw.line(screen, pygame.Color(self.color), (x1, y1), (x2, y2), width=4)
        pygame.draw.circle(screen, pygame.Color(self.color), (int(cx), int(cy)), 5)


