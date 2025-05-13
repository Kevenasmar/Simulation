import numpy as np
import matplotlib.pyplot as plt

class MoteurCC:
    def __init__(self, R, L, k_c, k_e, J, f):
        # Caractéristiques physiques

        self.R = R  # Résistance 
        self.L = L  # Inductance 
        self.k_c = k_c  # Constante de couple
        self.k_e = k_e  # Constante de force électromotrice
        self.J = J  # Inertie du rotor
        self.f = f  # Frottements visqueux

        # Entrées
        self.Um = 0  # Tension d'entrée
        self.load_inertia = 0  # Inertie de la charge ajoutée
        self.external_torque = 0  # Couple extérieur résistif
        self.viscosity = 0  # Viscosité du milieu

        # Sorties
        self.i = 0  # Courant
        self.Omega = 0  # Vitesse du rotor
        self.Gamma = 0  # Couple moteur
        self.position = 0  # Position du rotor

    def __str__(self):
        return (f"MoteurCC(R={self.R}, L={self.L}, k_c={self.k_c}, k_e={self.k_e}, "
                f"J={self.J}, f={self.f})")

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

    def simule(self, step):
        # Simplification avec L ≈ 0
        self.i = (self.Um - self.k_e * self.Omega) / self.R
        self.Gamma = self.k_c * self.i

        # Ajout des effets de la charge, du couple extérieur et de la viscosité
        total_inertia = self.J + self.load_inertia
        total_friction = self.f + self.viscosity
        dOmega_dt = (self.Gamma - self.external_torque - total_friction * self.Omega) / total_inertia
        self.Omega += dOmega_dt * step
        self.position += self.Omega * step

    def plot(self, temps, vitesses):
        plt.plot(temps, vitesses)
        plt.xlabel('Temps (s)')
        plt.ylabel('Vitesse (rad/s)')
        plt.title('Réponse indicielle du moteur CC')
        plt.grid(True)
        plt.show()

# Paramètres du moteur
R = 1.0  # Ohms
L = 0.001  # Henry
k_c = 0.01  # N.m/A
k_e = 0.01  # V.s
J = 0.01  # kg.m^2
f = 0.1  # N.m.s

# Création du moteur
moteur = MoteurCC(R, L, k_c, k_e, J, f)

# Simulation
t = 0
step = 0.01
temps = [t]
vitesses = [moteur.getSpeed()]

while t < 2:
    t += step
    moteur.setVoltage(1)  # Échelon unité de tension
    moteur.simule(step)
    temps.append(t)
    vitesses.append(moteur.getSpeed())

# Tracé de la réponse indicielle
moteur.plot(temps, vitesses)
    