import numpy as np
import matplotlib.pyplot as plt

class ControlPID_vitesse:
    def __init__(self, moteur, K_P, K_I, K_D):
        self.moteur = moteur  # Instance de la classe MoteurCC à contrôler
        self.K_P = K_P  # Gain proportionnel
        self.K_I = K_I  # Gain intégral
        self.K_D = K_D  # Gain dérivé

        self.vitesse_desiree = 0  # Vitesse désirée
        self.integral = 0  # Terme intégral
        self.derivative = 0  # Terme dérivé
        self.prev_error = 0  # Erreur précédente

    def __str__(self):
        return (f"ControlPID_vitesse(K_P={self.K_P}, K_I={self.K_I}, K_D={self.K_D})")

    def __repr__(self):
        return self.__str__()

    def setTarget(self, vitesse_desiree):
        self.vitesse_desiree = vitesse_desiree

    def getVoltage(self):
        # Calcul de l'erreur
        error = self.vitesse_desiree - self.moteur.getSpeed()

        # Calcul des termes PID
        self.integral += error
        self.derivative = error - self.prev_error
        self.prev_error = error

        # Calcul de la tension de sortie
        voltage = self.K_P * error + self.K_I * self.integral + self.K_D * self.derivative
        return voltage

    def simule(self, step):
        # Obtenir la tension du contrôleur PID
        voltage = self.getVoltage()

        # Appliquer la tension au moteur et simuler
        self.moteur.setVoltage(voltage)
        self.moteur.simule(step)

    def plot(self, temps, vitesses_desirees, vitesses_reelles):
        plt.plot(temps, vitesses_desirees, label='Vitesse Désirée')
        plt.plot(temps, vitesses_reelles, label='Vitesse Réelle')
        plt.xlabel('Temps (s)')
        plt.ylabel('Vitesse (rad/s)')
        plt.title('Réponse du moteur avec contrôleur PID')
        plt.legend()
        plt.grid(True)
        plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    from MoteurCC import MoteurCC

    # Paramètres du moteur
    R = 1.0  # Ohms
    L = 0.001  # Henry
    k_c = 0.01  # N.m/A
    k_e = 0.01  # V.s
    J = 0.01  # kg.m^2
    f = 0.1  # N.m.s

    # Création du moteur
    moteur = MoteurCC(R, L, k_c, k_e, J, f)

    # Création du contrôleur PID
    control = ControlPID_vitesse(moteur, K_P=1.0, K_I=0.1, K_D=0.01)

    # Simulation
    t = 0
    step = 0.01
    temps = [t]
    vitesses_desirees = [control.vitesse_desiree]
    vitesses_reelles = [moteur.getSpeed()]

    while t < 2:
        t += step
        temps.append(t)
        control.setTarget(1)  # Vitesse désirée de 1 rad/s
        control.simule(step)
        vitesses_desirees.append(control.vitesse_desiree)
        vitesses_reelles.append(moteur.getSpeed())

    # Tracé des résultats
    control.plot(temps, vitesses_desirees, vitesses_reelles)
