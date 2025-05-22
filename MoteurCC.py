import numpy as np
import matplotlib.pyplot as plt
import pygame
from vector3D import Vector3D as v

# === Classe représentant un moteur à courant continu (CC) ===
class MoteurCC:
    def __init__(self, R, L, k_c, k_e, J, f, p=v()):
        # === Caractéristiques physiques ===
        self.R = R       # Résistance (Ohm)
        self.L = L       # Inductance (H) — ignorée ici (L ≈ 0)
        self.k_c = k_c   # Constante de couple (Nm/A)
        self.k_e = k_e   # Constante de force contre-électromotrice (V.s/rad)
        self.J = J       # Inertie du moteur (kg.m²)
        self.f = f       # Frottement visqueux interne (N.m.s)

        # === Entrées du système ===
        self.Um = 0                # Tension d'alimentation (V)
        self.load_inertia = 0      # Inertie de charge (kg.m²)
        self.external_torque = 0   # Couple extérieur appliqué (N.m)
        self.viscosity = 0         # Frottement extérieur (N.m.s)

        # === États internes ===
        self.i = 0         # Courant (A)
        self.Omega = 0     # Vitesse angulaire (rad/s)
        self.Gamma = 0     # Couple développé (N.m)
        self.position = 0  # Position angulaire (rad)

        # === Position dans l'espace pour affichage pygame ===
        self.p = p
        self.x = p.x
        self.y = p.y

    # === Représentation textuelle utile pour debug ===
    def __str__(self):
        return (f"MoteurCC(R={self.R}, L={self.L}, k_c={self.k_c}, k_e={self.k_e}, "
                f"J={self.J}, f={self.f}, x={self.x}, y={self.y})")

    def __repr__(self):
        return self.__str__()

    # === Méthodes de configuration ===
    def setVoltage(self, Um):
        self.Um = Um  # Tension appliquée au moteur (V)

    def setLoadInertia(self, load_inertia):
        self.load_inertia = load_inertia  # Inertie extérieure (kg.m²)

    def setExternalTorque(self, external_torque):
        self.external_torque = external_torque  # Couple externe (N.m)

    def setViscosity(self, viscosity):
        self.viscosity = viscosity  # Frottement externe (N.m.s)

    # === Accès aux sorties ===
    def getPosition(self):
        return self.position  # Angle en rad

    def getSpeed(self):
        return self.Omega  # Vitesse en rad/s

    def getTorque(self):
        return self.Gamma  # Couple en N.m

    def getIntensity(self):
        return self.i  # Courant en A

    # (Non utilisée ici — prévue pour ajout de forces si besoin)
    def applyForce(self, *args):
        for f in args:
            self.forces += f

    # === Simulation d’un pas de temps ===
    def simulate(self, step):
        """
        Évolution de l'état du moteur au pas de temps `step` (en secondes),
        en supposant L ≈ 0 (approximation quasistatique du courant).
        """
        # Loi de Kirchhoff : Um = R*i + k_e*Omega
        self.i = (self.Um - self.k_e * self.Omega) / self.R

        # Couple généré par le moteur
        self.Gamma = self.k_c * self.i

        # Inertie et frottement totaux
        total_inertia = self.J + self.load_inertia
        total_friction = self.f + self.viscosity

        # Équation différentielle : J*dΩ/dt = Γ - Γ_ext - frottements
        dOmega_dt = (self.Gamma - self.external_torque - total_friction * self.Omega) / total_inertia

        # Mise à jour de la vitesse et de la position
        self.Omega += dOmega_dt * step
        self.position += self.Omega * step

    # === Affichage graphique avec pygame ===
    def gameDraw(self, scale, screen):
        X = self.x * scale
        Y = self.y * scale
        pygame.draw.circle(screen, (0, 0, 0), (int(X), int(Y)), 20)        # Centre noir
        pygame.draw.circle(screen, (0, 0, 128), (int(X), int(Y)), 40, 2)   # Anneau bleu

    # === Solution analytique de la vitesse angulaire ===
    def solution_analytique(self, time, Um, R, k_c, k_e, J, f):
        """
        Renvoie la solution analytique de la vitesse angulaire Ω(t) pour un moteur CC
        sans charge et à tension constante.
        """
        K = k_c / (k_e * k_c + R * f)
        tau = (R * J) / (k_e * k_c + R * f)
        return K * (1 - np.exp(-time / tau)) * Um
