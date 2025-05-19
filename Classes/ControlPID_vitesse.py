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

    def setTarget(self, vitesse):
        self.target_speed = vitesse

    def getVoltage(self):
        return self.voltages[-1] if self.voltages else 0.0

    def simule(self, step):
        error = self.target_speed - self.moteur.getSpeed()
        self.integral_error += error * step
        derivative_error = (error - self.prev_error) / step if step > 0 else 0.0

        Vmax = 24
        V = (self.Kp * error + self.Ki * self.integral_error + self.Kd * derivative_error)
        V = max(min(V, Vmax), -Vmax)
        self.prev_error = error

        self.moteur.setVoltage(V)
        self.moteur.simulate(step)

        self.voltages.append(V)
        self.speeds.append(self.moteur.getSpeed())

    def evaluate_performance(self, temps, name="Système"):
        speeds = np.array(self.speeds)
        voltages = np.array(self.voltages)
        target = self.target_speed

        error_stat = abs(target - speeds[-1])
        vmax = speeds.max()
        v_overshoot = max(0.0, vmax - target)
        t95 = next((t for t, omega in zip(temps, speeds) if omega >= 0.95 * target), None)

        v_applied_max = abs(voltages).max()

        print(f"\n--- Performances ({name}) ---")
        print(f"Temps de réponse à 95% : {t95:.2f} s" if t95 else "Temps de réponse non atteint.")
        print(f"Erreur statique         : {error_stat:.4f} rad/s")
        print(f"Vitesse max atteinte    : {vmax:.4f} rad/s")
        print(f"Survitesse              : {v_overshoot:.4f} rad/s")
        print(f"Tension max appliquée   : {v_applied_max:.2f} V")

