import numpy as np
import matplotlib.pyplot as plt
import pygame
from vector3D import Vector3D as v

class MoteurCC:
    def __init__(self, R, L, k_c, k_e, J, f, p=v()):
        # Physical characteristics
        self.R = R
        self.L = L
        self.k_c = k_c
        self.k_e = k_e
        self.J = J
        self.f = f

        # Inputs
        self.Um = 0
        self.load_inertia = 0
        self.external_torque = 0
        self.viscosity = 0

        # Outputs
        self.i = 0
        self.Omega = 0
        self.Gamma = 0
        self.position = 0

        # Coordinates for display*
        self.p = p
        self.x = p.x
        self.y = p.y

    def __str__(self):
        return (f"MoteurCC(R={self.R}, L={self.L}, k_c={self.k_c}, k_e={self.k_e}, "
                f"J={self.J}, f={self.f}, x={self.x}, y={self.y})")

    def __repr__(self):
        return self.__str__()

    def setVoltage(self, Um):
        self.Um = Um

    def setLoadInertia(self, load_inertia):
        self.load_inertia = load_inertia

    def setExternalTorque(self, external_torque):
        self.external_torque = external_torque

    def setViscosity(self, viscosity):
        self.viscosity = viscosity

    def getPosition(self):
        return self.position

    def getSpeed(self):
        return self.Omega

    def getTorque(self):
        return self.Gamma

    def getIntensity(self):
        return self.i

    def applyForce(self, *args):
        for f in args:
            self.forces += f

    def simulate(self, step):
        # Simplification with L ≈ 0
        self.i = (self.Um - self.k_e * self.Omega) / self.R
        self.Gamma = self.k_c * self.i
        total_inertia = self.J + self.load_inertia
        total_friction = self.f + self.viscosity
        dOmega_dt = (self.Gamma - self.external_torque - total_friction * self.Omega) / total_inertia
        self.Omega += dOmega_dt * step
        self.position += self.Omega * step

    def gameDraw(self, scale, screen):
        # Centre du moteur
        X = self.x * scale
        Y = self.y * scale
        pygame.draw.circle(screen, (0, 0, 0), (int(X), int(Y)), 20)
        pygame.draw.circle(screen, (0, 0, 128), (int(X), int(Y)), 40, width=2)

    def solution_analytique(self,time, Um, R, k_c, k_e, J, f):
        K = k_c / (k_e * k_c + R * f)
        tau = (R * J) / (k_e * k_c + R * f)
        return K * (1 - np.exp(-time / tau)) * Um

