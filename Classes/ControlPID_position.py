import pygame
import numpy as np
from MoteurCC import MoteurCC
from vector3D import Vector3D as V3D
from Forces import *

class ControlPID_position:
    def __init__(self, moteur, Kp=0.0, Ki=0.0, Kd=0.0):
        self.m = moteur
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.target = 0.0
        self.erreur_cumulee = 0.0
        self.derniere_erreur = 0.0
        self.voltage = 0.0
        self.position = 0.0
        self.positions = []

    def setTarget(self, position_cible):
        self.target = position_cible

    def getVoltage(self):
        return self.voltage

    def simule(self, step):
        self.position += self.m.getSpeed() * step

        erreur = self.target - self.position
        self.erreur_cumulee += erreur * step
        derivee = (erreur - self.derniere_erreur) / step if step > 0 else 0.0
        self.derniere_erreur = erreur

        self.voltage = (
            self.Kp * erreur +
            self.Ki * self.erreur_cumulee +
            self.Kd * derivee
        )

        self.m.setVoltage(self.voltage)
        self.m.simulate(step)
        self.positions.append(self.position)

