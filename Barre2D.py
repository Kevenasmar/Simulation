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
            self.acc = V3D()
            self.alpha = 0.0
            return

        # Initialisation des sommes
        total_force = V3D()
        total_moment = 0.0

        for (f, p) in self.forces:
            # Position réelle du point d'application (dans le référentiel global)
            # Le point est donné en coordonnée normalisée le long de la barre
            # On construit d'abord un vecteur de direction de la barre
            dir_barre = V3D(np.cos(self.theta), np.sin(self.theta), 0)
            r = (p * self.L / 2) * dir_barre  # vecteur du centre jusqu'au point d'application

            # Somme des forces
            total_force += f

            # Moment par rapport au centre : r ^ F (produit vectoriel)
            # Comme tout est dans le plan (x, y), seul le composant z du moment est utile
            moment = r.x * f.y - r.y * f.x
            total_moment += moment

        # Mise à jour des accélérations
        self.acc = total_force *(1/ self.mass)
        self.alpha = total_moment *(1/ self.getInertia())

        # Réinitialisation de la liste des forces (consommées à chaque pas)
        self.forces = []

        # Mise à jour des vitesses et positions
        v_old = self.vel.copy()
        self.vel += self.acc * step
        self.pos += v_old * step + 0.5 * self.acc * step**2



        self.omega += self.alpha * step
        self.theta += self.omega * step
        self.history.append(self.pos)

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


