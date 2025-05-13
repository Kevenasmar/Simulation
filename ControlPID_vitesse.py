import matplotlib.pyplot as plt
import numpy as np
from MoteurCC import MoteurCC

class ControlPID_vitesse:
    def __init__(self, moteur, Kp, Ki, Kd):
        self.moteur = moteur
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.target_speed = 0.0
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.voltages = []
        self.speeds = []

    def __str__(self):
        return f"ControlPID_vitesse(Kp={self.Kp}, Ki={self.Ki}, Kd={self.Kd})"

    def __repr__(self):
        return self.__str__()

    def setTarget(self, vitesse):
        self.target_speed = vitesse

    def getVoltage(self):
        return self.voltages[-1] if self.voltages else 0.0

    def simule(self, step):
        # Calcul de l'erreur
        error = self.target_speed - self.moteur.getSpeed()
        
        # Terme intégral
        self.integral_error += error * step
        
        # Terme dérivé
        derivative_error = (error - self.prev_error) / step

        # Commande PID
        V = (self.Kp * error +
             self.Ki * self.integral_error +
             self.Kd * derivative_error)

        self.prev_error = error

        # Envoi de la tension et simulation du moteur
        self.moteur.setVoltage(V)
        self.moteur.simule(step)

        # Enregistrement pour le tracé
        self.voltages.append(V)
        self.speeds.append(self.moteur.getSpeed())

    def plot(self, temps):
        plt.figure(figsize=(10, 6))
        plt.plot(temps, self.speeds, label="Vitesse moteur (PID)")
        plt.plot(temps, self.voltages, label="Tension envoyée (V)", linestyle='--')
        plt.xlabel("Temps (s)")
        plt.ylabel("Valeurs")
        plt.title("Réponse du moteur en boucle fermée avec contrôleur PID")
        plt.grid(True)
        plt.legend()
        plt.show()


# Paramètres moteurs
R = 1.0      # résistance de l’induit [Ohm]
L = 0.001    # inductance de l’induit [H] ≈ 0
k_c = 0.01   # constante de couple [Nm/A]
k_e = 0.01   # constante de fcem [V.s]
J = 0.01     # inertie du rotor [kg.m²]
f = 0.1      # frottement visqueux interne [Nms]
Um = 1.0     # tension aux bornes du moteur [V]

# Paramètres extérieurs
load_inertia = 0.005           # inertie de charge [kg.m²]
external_torque = 0.002        # couple extérieur [Nm]
viscosity = 0.05               # viscosité [N.m.s]

# Constantes analytiques
K = k_c / (k_c * k_e + R * f)

# Simulation
step = 0.01
t_max = 10
temps = np.arange(0, t_max + step, step)

# === Boucle ouverte ===
m_bo = MoteurCC(R, L, k_c, k_e, J, f)
m_bo.setLoadInertia(load_inertia)
m_bo.setExternalTorque(external_torque)
m_bo.setViscosity(viscosity)

# === Contrôle P ===
m_P = MoteurCC(R, L, k_c, k_e, J, f)
m_P.setLoadInertia(load_inertia)
m_P.setExternalTorque(external_torque)
m_P.setViscosity(viscosity)
ctrl_P = ControlPID_vitesse(m_P, Kp=5.0, Ki=0.0, Kd=0.0)

# === Contrôle PI ===
m_PI = MoteurCC(R, L, k_c, k_e, J, f)
m_PI.setLoadInertia(load_inertia)
m_PI.setExternalTorque(external_torque)
m_PI.setViscosity(viscosity)
ctrl_PI = ControlPID_vitesse(m_PI, Kp=5.0, Ki=10.0, Kd=0.0)

# Stockage des vitesses
vit_bo = []
vit_P = []
vit_PI = []

# Boucle de simulation
for t in temps:
    m_bo.setVoltage(1/K)
    m_bo.simule(step)
    vit_bo.append(m_bo.getSpeed())

    ctrl_P.setTarget(1)
    ctrl_P.simule(step)
    vit_P.append(m_P.getSpeed())

    ctrl_PI.setTarget(1)
    ctrl_PI.simule(step)
    vit_PI.append(m_PI.getSpeed())

# === Tracé des résultats ===
plt.figure(figsize=(10, 6))
plt.axhline(y=1.0, color='gray', linestyle='--', label='Consigne (1 rad/s)')
plt.plot(temps, vit_bo, label="Boucle ouverte (1/K)", linestyle=":", linewidth=2)
plt.plot(temps, vit_P, label="Contrôle P (Kp = 5.0)", linewidth=2)
plt.plot(temps, vit_PI, label="Contrôle PI (Kp = 5.0, Ki = 10.0)", linewidth=2)
plt.xlabel("Temps (s)")
plt.ylabel("Vitesse Ω(t) [rad/s]")
plt.title("Comparaison : effets de $K_P$ et $K_I$ avec actions extérieures")
plt.grid(True)
plt.legend()
plt.show()
