import numpy as np
from vector3D import Vector3D as V3D
import matplotlib.pyplot as plt
from Forces import *

class Barre:
    def __init__(self, mass=1, p0=V3D(), v0=V3D(), a0=V3D(), t0=0.0, o0=0.0, alpha0=0.0, long=10, fix=False, name="barre", color='red'):
        self.mass = mass
        self.L = long
        self.name = name
        self.color = color
        self.fix = fix

        angle = t0  
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)
        p_centre = p0 + (self.L / 2) * dir_barre  

        self.position = [p_centre]

        # Translation
        self.speed = [v0]
        self.acceleration = [a0]

        # Rotation
        self.theta = [t0]
        self.omega = [o0]
        self.alpha = [alpha0]

        # Liste des forces appliquées à chaque pas
        self.forces = []

    def applyForce(self, force, point):
        if not isinstance(force, V3D):
            raise ValueError("force doit être un V3D")
        if not -1 <= point <= 1:
            raise ValueError("point doit être dans [-1, 1]")
        self.forces.append((force, point))

    def getInertia(self):
        return (1 / 12) * self.mass * self.L**2
    
    def getPoint(self, alpha):
        return self.position[-1] + V3D(alpha * self.L / 2, 0).rotZ(self.t0[-1])

    def getPosition(self):
        return self.position[-1]

    def getSpeed(self):
        return self.speed[-1]

    def getAngle(self):
        return self.theta[-1]

    def getAngularSpeed(self):
        return self.omega[-1]

    def simulate(self, step):
        self.pfd(step)

    def pfd(self, step):
        if self.fix:
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

        for (f, p_rel) in self.forces:
            total_force += f
            r = (p_rel * self.L / 2) * dir_barre
            moment = r.x * f.y - r.y * f.x
            total_moment += moment

        # Translation
        a = total_force * (1 / self.mass)
        v = self.speed[-1] + a * step
        p = self.position[-1] + self.speed[-1] * step + 0.5 * a * step**2

        self.acceleration.append(a)
        self.speed.append(v)
        self.position.append(p)

        # Rotation
        alpha = total_moment / self.getInertia()
        omega = self.omega[-1] + alpha * step
        theta = self.theta[-1] + self.omega[-1] * step + 0.5 * alpha * step**2

        self.alpha.append(alpha)
        self.omega.append(omega)
        self.theta.append(theta)

        # Reset des forces
        self.forces = []

    def plot(self):
        from pylab import plot
        X = [pos.x for pos in self.position]
        Y = [pos.y for pos in self.position]
        return plot(X, Y, color=self.color, label=self.name) + plot(X[-1], Y[-1], 'o', color=self.color)

    def gameDraw(self, scale, screen):
        import pygame
        if not screen:
            return

        angle = self.getAngle()
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)
        
        # Extrémité gauche (référence visuelle)
        pos_left = self.getPosition() - (self.L / 2) * dir_barre
        pos_right = self.getPosition() + (self.L / 2) * dir_barre

        x1 = int(pos_left.x * scale)
        y1 = int(pos_left.y * scale)
        x2 = int(pos_right.x * scale)
        y2 = int(pos_right.y * scale)

        # Vitesse au centre
        VX = int(scale * self.getSpeed().x)
        VY = int(scale * self.getSpeed().y)

        # Dessin de la barre
        pygame.draw.line(screen, pygame.Color(self.color), (x1, y1), (x2, y2), width=4)

        # Vecteur vitesse au centre
        Xc = int(self.getPosition().x * scale)
        Yc = int(self.getPosition().y * scale)
        
        # Cercle à gauche (référence)
        pygame.draw.circle(screen, pygame.Color(self.color), (Xc, Yc), 5)

        pygame.draw.line(screen, 'blue', (Xc, Yc), (Xc + VX, Yc + VY), 3)

        

