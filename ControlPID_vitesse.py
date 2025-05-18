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

# Paramètres moteur
R, L, k_c, k_e, J, f = 1.0, 0.001, 0.01, 0.01, 0.01, 0.1
load_inertia, external_torque, viscosity = 0.005, 0.002, 0.05
K = k_c / (k_c * k_e + R * f)

# Simulation
step = 0.01
t_max = 10
temps = np.arange(0, t_max + step, step)

# Boucle ouverte
m_bo = MoteurCC(R, L, k_c, k_e, J, f)
m_bo.setLoadInertia(load_inertia)
m_bo.setExternalTorque(external_torque)
m_bo.setViscosity(viscosity)
vit_bo = [m_bo.getSpeed()]
for t in temps[1:]:
    m_bo.setVoltage(1/K)
    m_bo.simulate(step)
    vit_bo.append(m_bo.getSpeed())
omega_bo = np.array(vit_bo)
print("\n--- Performances (Boucle ouverte) ---")
print(f"Erreur statique         : {abs(1 - omega_bo[-1]):.4f} rad/s")
print(f"Vitesse max atteinte    : {omega_bo.max():.4f} rad/s")

# Contrôle P
m_P = MoteurCC(R, L, k_c, k_e, J, f)
m_P.setLoadInertia(load_inertia)
m_P.setExternalTorque(external_torque)
m_P.setViscosity(viscosity)
ctrl_P = ControlPID_vitesse(m_P, Kp=100.0, Ki=0.0, Kd=0.0)
ctrl_P.setTarget(1)
for t in temps:
    ctrl_P.simule(step)

# Contrôle PI
m_PI = MoteurCC(R, L, k_c, k_e, J, f)
m_PI.setLoadInertia(load_inertia)
m_PI.setExternalTorque(external_torque)
m_PI.setViscosity(viscosity)
ctrl_PI = ControlPID_vitesse(m_PI, Kp=5.0, Ki=10.0, Kd=0.0)
ctrl_PI.setTarget(1)
for t in temps:
    ctrl_PI.simule(step)

# Tracé
plt.figure(figsize=(10, 6))
plt.axhline(y=1.0, color='gray', linestyle='--', label='Consigne (1 rad/s)')
plt.plot(temps, omega_bo, label="Boucle ouverte (1/K)", linewidth=2)
plt.plot(temps, ctrl_P.speeds, label="Contrôle P (Kp=100)", linewidth=2)
plt.plot(temps, ctrl_PI.speeds, label="Contrôle PI (Kp=5, Ki=10)", linewidth=2)
plt.xlabel("Temps (s)")
plt.ylabel("Vitesse Ω(t) [rad/s]")
plt.title("Comparaison : boucle ouverte vs PID")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("comparaison_pid.png")
plt.show()

# Affichage des performances
ctrl_P.evaluate_performance(temps, name="Contrôle P")
ctrl_PI.evaluate_performance(temps, name="Contrôle PI")
