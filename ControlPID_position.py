import pygame
import numpy as np
from MoteurCC import MoteurCC
from vector3D import Vector3D as V3D
from Forces import *

class ControlPID_position:
    """
    Contrôleur PID appliqué à un moteur à courant continu (MoteurCC)
    pour asservir la position angulaire (en radian).
    """

    def __init__(self, moteur, Kp=0.0, Ki=0.0, Kd=0.0):
        self.m = moteur          # Moteur contrôlé
        self.Kp = Kp             # Gain proportionnel
        self.Ki = Ki             # Gain intégral
        self.Kd = Kd             # Gain dérivé

        self.target = 0.0        # Position cible (en rad)
        self.erreur_cumulee = 0.0
        self.derniere_erreur = 0.0
        self.voltage = 0.0       # Tension calculée (V)
        self.position = 0.0      # Position simulée (rad)
        self.positions = []      # Historique (pour affichage)

    def setTarget(self, position_cible):
        """
        Définit une nouvelle consigne de position (en radian).
        """
        self.target = position_cible

    def getVoltage(self):
        """
        Retourne la dernière tension calculée (V).
        """
        return self.voltage

    def simule(self, step):
        """
        Simule un pas de temps (step en secondes) :
        - met à jour l'état du moteur
        - applique la commande PID sur la position
        """

        # Mise à jour de la position actuelle (intégration de la vitesse)
        self.position += self.m.getSpeed() * step

        # Calcul des termes du PID
        erreur = self.target - self.position
        self.erreur_cumulee += erreur * step
        derivee = (erreur - self.derniere_erreur) / step if step > 0 else 0.0
        self.derniere_erreur = erreur

        # Commande PID → tension à appliquer au moteur
        self.voltage = (
            self.Kp * erreur +
            self.Ki * self.erreur_cumulee +
            self.Kd * derivee
        )

        # Application de la tension et mise à jour du moteur
        self.m.setVoltage(self.voltage)
        self.m.simulate(step)

        # Stockage de la position simulée
        self.positions.append(self.position)
