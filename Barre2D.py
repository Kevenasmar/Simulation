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

        # Translation
        self.position = [p0]
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

        pos = self.position[-1]
        angle = self.theta[-1]
        cx = pos.x * scale
        cy = pos.y * scale
        demi_L = (self.L / 2) * scale
        dx = demi_L * np.cos(angle)
        dy = demi_L * np.sin(angle)

        x1, y1 = int(cx - dx), int(cy - dy)
        x2, y2 = int(cx + dx), int(cy + dy)

        pygame.draw.line(screen, pygame.Color(self.color), (x1, y1), (x2, y2), width=4)
        pygame.draw.circle(screen, pygame.Color(self.color), (int(cx), int(cy)), 5)
