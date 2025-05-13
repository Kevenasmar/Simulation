import numpy as np
import matplotlib.pyplot as plt
from MoteurCC import MoteurCC

class ControlPID_vitesse:
    def __init__(self, moteur, K_P, K_I, K_D):
        self.moteur = moteur
        self.K_P = K_P
        self.K_I = K_I
        self.K_D = K_D
        self.vitesse_desiree = 0
        self.integral = 0
        self.derivative = 0
        self.prev_error = 0

    def setTarget(self, vitesse_desiree):
        self.vitesse_desiree = vitesse_desiree

    def getVoltage(self):
        error = self.vitesse_desiree - self.moteur.getSpeed()
        self.integral += error
        self.derivative = error - self.prev_error
        self.prev_error = error
        voltage = self.K_P * error + self.K_I * self.integral + self.K_D * self.derivative
        return voltage

    def simule(self, step):
        voltage = self.getVoltage()
        self.moteur.setVoltage(voltage)
        self.moteur.simule(step)

def simulate_and_plot(K_P_values, K_I_values, K_D_values, title, param_type):
    R = 1.0
    L = 0.0
    k_c = 0.01
    k_e = 0.01
    J = 0.01
    f = 0.1

    t = 0
    step = 0.01
    temps = np.arange(0, 2, step)

    plt.figure(figsize=(12, 8))

    if param_type == 'K_P':
        for K_P in K_P_values:
            moteur = MoteurCC(R, L, k_c, k_e, J, f)
            control = ControlPID_vitesse(moteur, K_P, K_I_values[0], K_D_values[0])
            vitesses = []
            for t in temps:
                control.setTarget(1)
                control.simule(step)
                vitesses.append(moteur.getSpeed())
            plt.plot(temps, vitesses, label=f'K_P={K_P}, K_I={K_I_values[0]}, K_D={K_D_values[0]}')

    elif param_type == 'K_I':
        for K_I in K_I_values:
            moteur = MoteurCC(R, L, k_c, k_e, J, f)
            control = ControlPID_vitesse(moteur, K_P_values[0], K_I, K_D_values[0])
            vitesses = []
            for t in temps:
                control.setTarget(1)
                control.simule(step)
                vitesses.append(moteur.getSpeed())
            plt.plot(temps, vitesses, label=f'K_P={K_P_values[0]}, K_I={K_I}, K_D={K_D_values[0]}')

    elif param_type == 'K_D':
        for K_D in K_D_values:
            moteur = MoteurCC(R, L, k_c, k_e, J, f)
            control = ControlPID_vitesse(moteur, K_P_values[0], K_I_values[0], K_D)
            vitesses = []
            for t in temps:
                control.setTarget(1)
                control.simule(step)
                vitesses.append(moteur.getSpeed())
            plt.plot(temps, vitesses, label=f'K_P={K_P_values[0]}, K_I={K_I_values[0]}, K_D={K_D}')

    plt.xlabel('Temps (s)')
    plt.ylabel('Vitesse (rad/s)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

# Valeurs des gains à tester
K_P_values = [0.1, 1.0, 10]
K_I_values = [0.1, 1.0, 10]
K_D_values = [0.01, 1.0, 10]

# Exécuter la simulation et le tracé pour différents K_P
simulate_and_plot(K_P_values, K_I_values, K_D_values, 'Comparaison des Réponses du Moteur avec Différents K_P', 'K_P')

# Exécuter la simulation et le tracé pour différents K_I
simulate_and_plot(K_P_values, K_I_values, K_D_values, 'Comparaison des Réponses du Moteur avec Différents K_I', 'K_I')

# Exécuter la simulation et le tracé pour différents K_D
simulate_and_plot(K_P_values, K_I_values, K_D_values, 'Comparaison des Réponses du Moteur avec Différents K_D', 'K_D')
