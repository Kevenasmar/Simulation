import numpy as np
import matplotlib.pyplot as plt

class MoteurCC:
    def __init__(self, R, L, k_c, k_e, J, f):
        # Caractéristiques physiques
        self.R = R
        self.L = L
        self.k_c = k_c
        self.k_e = k_e
        self.J = J
        self.f = f

        # Entrées
        self.Um = 0
        self.load_inertia = 0
        self.external_torque = 0
        self.viscosity = 0

        # Sorties
        self.i = 0
        self.Omega = 0
        self.Gamma = 0
        self.position = 0

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
        total_inertia = self.J + self.load_inertia
        total_friction = self.f + self.viscosity
        dOmega_dt = (self.Gamma - self.external_torque - total_friction * self.Omega) / total_inertia
        self.Omega += dOmega_dt * step
        self.position += self.Omega * step

def solution_analytique(time, Um, R, k_c, k_e, J, f):
    K = k_c / (k_e * k_c + R * f)
    tau = (R * J) / (k_e * k_c + R * f)
    return K * (1 - np.exp(-time / tau)) * Um

# Paramètres moteurs
R = 1.0      # résistance de l’induit [Ohm]
L = 0.001    # inductance de l’induit [H] ≈ 0
k_c = 0.01   # constante de couple [Nm/A]
k_e = 0.01   # constante de fcem [V.s]
J = 0.01     # inertie du rotor [kg.m²]
f = 0.1      # frottement visqueux interne [Nms]
Um = 1.0

# Paramètres extérieurs (à mettre à 0 s'il le faut)
load_inertia = 0.005           # inertie de charge [kg.m²]
external_torque = 0.002        # couple extérieur constant [Nm]
viscosity = 0.05               # viscosité du milieu [Nms]

# Création du moteur
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
    moteur.simule(step)
    temps.append(t)
    vitesses_num.append(moteur.getSpeed())


# Solution analytique
temps_array = np.array(temps)
vitesses_theo = solution_analytique(temps_array, Um, R, k_c, k_e, J, f)

# Tracé des deux courbes
plt.figure(figsize=(10, 6))
plt.plot(temps_array, vitesses_theo, label='Solution analytique', linewidth=2)
plt.plot(temps_array, vitesses_num, '--', label='Simulation numérique')
plt.xlabel('Temps (s)')
plt.ylabel('Vitesse Ω(t) [rad/s]')
plt.title('Comparaison : théorie vs simulation numérique avec enrichissement')
plt.grid(True)
plt.legend()
plt.show()
    