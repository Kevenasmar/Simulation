import matplotlib.pyplot as plt
import numpy as np
from MoteurCC import MoteurCC
from ControlPID_vitesse import ControlPID_vitesse

if __name__ == "__main__":
    # === Paramètres du moteur ===
    R, L, k_c, k_e, J, f = 1.0, 0.001, 0.01, 0.01, 0.01, 0.1  # constantes physiques
    load_inertia = 0.005       # Inertie de charge supplémentaire
    external_torque = 0.002    # Couple de perturbation
    viscosity = 0.05           # Frottement additionnel

    # Gain statique du système
    K = k_c / (k_c * k_e + R * f)

    # === Paramètres de simulation ===
    step = 0.01
    t_max = 10
    temps = np.arange(0, t_max + step, step)

    # === Boucle ouverte (commande constante = 1/K) ===
    m_bo = MoteurCC(R, L, k_c, k_e, J, f)
    m_bo.setLoadInertia(load_inertia)
    m_bo.setExternalTorque(external_torque)
    m_bo.setViscosity(viscosity)

    vit_bo = [m_bo.getSpeed()]  # initialisation
    for t in temps[1:]:
        m_bo.setVoltage(1 / K)  # tension qui devrait donner Ω=1 à l'équilibre
        m_bo.simulate(step)
        vit_bo.append(m_bo.getSpeed())
    omega_bo = np.array(vit_bo)

    print("\n--- Performances (Boucle ouverte) ---")
    print(f"Erreur statique         : {abs(1 - omega_bo[-1]):.4f} rad/s")
    print(f"Vitesse max atteinte    : {omega_bo.max():.4f} rad/s")

    # === Contrôle P seul ===
    m_P = MoteurCC(R, L, k_c, k_e, J, f)
    m_P.setLoadInertia(load_inertia)
    m_P.setExternalTorque(external_torque)
    m_P.setViscosity(viscosity)
    ctrl_P = ControlPID_vitesse(m_P, Kp=100.0, Ki=0.0, Kd=0.0)
    ctrl_P.setTarget(1)  # consigne Ω = 1 rad/s

    for t in temps:
        ctrl_P.simule(step)

    # === Contrôle PI ===
    m_PI = MoteurCC(R, L, k_c, k_e, J, f)
    m_PI.setLoadInertia(load_inertia)
    m_PI.setExternalTorque(external_torque)
    m_PI.setViscosity(viscosity)
    ctrl_PI = ControlPID_vitesse(m_PI, Kp=5.0, Ki=10.0, Kd=0.0)
    ctrl_PI.setTarget(1)

    for t in temps:
        ctrl_PI.simule(step)

    # === Tracé des résultats ===
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
    plt.show()

    # === Analyse des performances ===
    ctrl_P.evaluate_performance(temps, name="Contrôle P")
    ctrl_PI.evaluate_performance(temps, name="Contrôle PI")
