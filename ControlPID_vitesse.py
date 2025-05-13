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

        # Saturation éventuelle de la tension (ex : Vmax = 12V)
        V = max(min(V, 12), -12)

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

# Paramètres moteur (valeurs de base)
R = 1.0
L = 0.0
k_c = 0.01
k_e = 0.01
J = 0.01
f = 0.1

# Constantes analytiques
K = k_c / (k_c * k_e + R * f)

# Simulation
step = 0.01
t_max = 2
temps = np.arange(0, t_max + step, step)

# Moteur en boucle ouverte (pour référence du gain)
m_bo = MoteurCC(R, L, k_c, k_e, J, f)

# Moteur avec correcteur P
m_P = MoteurCC(R, L, k_c, k_e, J, f)
ctrl_P = ControlPID_vitesse(m_P, Kp=2.0, Ki=0.0, Kd=0.0)

# Moteur avec correcteur PI
m_PI = MoteurCC(R, L, k_c, k_e, J, f)
ctrl_PI = ControlPID_vitesse(m_PI, Kp=2.0, Ki=10.0, Kd=0.0)

# Traces des courbes
vit_bo = []
vit_P = []
vit_PI = []

for t in temps:
    # Boucle ouverte : tension constante pour atteindre 1 rad/s
    m_bo.setVoltage(1 / K)
    m_bo.simule(step)
    vit_bo.append(m_bo.getSpeed())

    # Boucle fermée : consigne de vitesse à 1 rad/s
    ctrl_P.setTarget(1)
    ctrl_P.simule(step)
    vit_P.append(m_P.getSpeed())

    ctrl_PI.setTarget(1)
    ctrl_PI.simule(step)
    vit_PI.append(m_PI.getSpeed())

# Tracé des vitesses
plt.figure(figsize=(10, 6))
plt.plot(temps, vit_bo, label="Boucle ouverte (1/K)", linestyle=":", linewidth=2)
plt.plot(temps, vit_P, label="Contrôle P = 2.0", linewidth=2)
plt.plot(temps, vit_PI, label="Contrôle P = 2.0, I = 10.0", linewidth=2)
plt.xlabel("Temps (s)")
plt.ylabel("Vitesse Ω(t) [rad/s]")
plt.title("Comparaison : effet de $K_P$ et $K_I$ sur le contrôle de vitesse")
plt.grid(True)
plt.legend()
plt.show()
