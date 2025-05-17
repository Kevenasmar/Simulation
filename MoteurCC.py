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

        # Coordinates for display
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

def solution_analytique(time, Um, R, k_c, k_e, J, f):
    K = k_c / (k_e * k_c + R * f)
    tau = (R * J) / (k_e * k_c + R * f)
    return K * (1 - np.exp(-time / tau)) * Um

# Motor parameters
R = 1.0      # Armature resistance [Ohm]
L = 0.001    # Armature inductance [H] ≈ 0
k_c = 0.01   # Torque constant [Nm/A]
k_e = 0.01   # Back EMF constant [V.s]
J = 0.01     # Rotor inertia [kg.m²]
f = 0.1      # Internal viscous friction [Nms]
Um = 1.0     # Voltage across the motor [V]

# External parameters (set to 0 if not needed)
load_inertia = 0.005           # Load inertia [kg.m²]
external_torque = 0.002        # Constant external torque [Nm]
viscosity = 0.05               # Medium viscosity [Nms]

# Create the motor
moteur = MoteurCC(R, L, k_c, k_e, J, f)
moteur.setLoadInertia(load_inertia)
moteur.setExternalTorque(external_torque)
moteur.setViscosity(viscosity)

# Simulation
t = 0
step = 0.01
temps = [t]
vitesses_num = [moteur.getSpeed()]

while t < 2:
    t += step
    moteur.setVoltage(Um)
    moteur.simulate(step)
    temps.append(t)
    vitesses_num.append(moteur.getSpeed())

# Analytical solution
temps_array = np.array(temps)
vitesses_theo = solution_analytique(temps_array, Um, R, k_c, k_e, J, f)

# Decommenter la suite quand vous executer ce code, sinon recomenter pour eviter de revoir cette fenetre a chaque autre executuion 


# # Plotting
# plt.figure(figsize=(10, 6))
# plt.axhline(y=0.1, color='gray', linestyle='--', label='Consigne (0.1 rad/s)')
# plt.plot(temps_array, vitesses_theo, label='Solution analytique', linewidth=2)
# plt.plot(temps_array, vitesses_num, '--', label='Simulation numérique')
# plt.xlabel('Temps (s)')
# plt.ylabel('Vitesse Ω(t) [rad/s]')
# plt.title('Comparaison : théorie vs simulation numérique avec enrichissement')
# plt.grid(True)
# plt.legend()
# plt.show()
