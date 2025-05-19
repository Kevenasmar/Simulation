from Particule import Particule
from Barre2D import Barre
from vector3D import Vector3D as V3D
import numpy as np

class Force(object):
    
    def __init__(self,force=V3D(),name='force',active=True):
        self.force = force
        self.name = name
        self.active = active
        
    def __str__(self):
        return "Force ("+str(self.force)+', '+self.name+")"
        
    def __repr__(self):
        return str(self)

    def setForce(self,entity):
        if self.active:
            entity.applyForce(self.force)

class Gravity(Force):
    def __init__(self,g=V3D(0,-9.8),name='gravity',active=True):
        self.g = g
        self.name = name
        self.active = active

    def setForce(self,entity):
        if isinstance(entity,Particule):
            if self.active:
                entity.applyForce(-self.g*entity.mass)
    
        if isinstance(entity, Barre):
            if self.active : 
                entity.applyForce(-self.g*entity.mass,0.0)

class Bounce_y(Force):
    def __init__(self,k=1,step=0.1,name="boing",active=True):
        self.name=name
        self.k = k
        self.step = step

    def setForce(self,entity):
        if isinstance(entity, Particule):
            if entity.getPosition().y < 0 and entity.getSpeed().y <0 :
                entity.applyForce(-2*(self.k/self.step)*V3D(0,entity.getSpeed().y * entity.mass ))
        
class Bounce_x(Force):
    def __init__(self,k=1,step=0.1,name="boing",active=True):
        self.name=name
        self.k = k
        self.step = step
        
    def setForce(self,entity):
        if isinstance(entity,Particule):
            if entity.getPosition().x < 0 and entity.getSpeed().x <0 :
                entity.applyForce(-2*(self.k/self.step)*V3D(entity.getSpeed().x * entity.mass))
        
class SpringDamper(Force):
    def __init__(self,P0,P1,k=0,c=0,l0=0,active=True,name="spring_and_damper"):
        Force.__init__(self,V3D(),name,active)
        self.k = k
        self.c = c
        self.P0 = P0
        self.P1 = P1
        self.l0 = l0
    
    def setForce(self, entity):
        if isinstance(entity, Particule):
            vec_dir = self.P1.getPosition() - self.P0.getPosition()
            v_n = vec_dir.norm()
            flex = vec_dir.mod()-self.l0
            
            vit = self.P1.getSpeed() - self.P0.getSpeed()
            vit_n = vit ** v_n * self.c 
            
            force = (self.k * flex + vit_n)* v_n
            if entity == self.P0:
                entity.applyForce(force)
            elif entity == self.P1:
                entity.applyForce(-force)
            else:
                pass
            
class Link(SpringDamper):
    def __init__(self,P0,P1,name="link"):
        l0 = (P0.getPosition()-P1.getPosition()).mod()
        SpringDamper.__init__(self,P0, P1,1000,100,l0,True,"link")


class SpringDamperMoteur(Force):
    def __init__(self, moteur, particule, k = 10, c = 1, name = "spring damper moteur"):
        self.moteur = moteur 
        self.particule  = particule
        self.k = k 
        self.c = c
        self.name = name

        self.l0 = (self.particule.getPosition() - self.moteur.p).mod()

    def setForce(self,p):
        if p != self.particule : 
            return 
        
        pos_m = self.moteur.p
        pos_p = p.getPosition()
        vec_dir = pos_p - pos_m
        unit = vec_dir.norm()
        distance = vec_dir.mod()

        v_r = self.particule.getSpeed()
        v_n = v_r ** unit 

        force = (-self.k * (distance - self.l0) - self.c * v_n) * unit
        self.particule.applyForce(force)


class ForceMoteur(Force):
    def __init__(self, moteur, particule, active=True, name="force_moteur"):
        super().__init__(V3D(), name, active)
        self.moteur = moteur
        self.particule = particule

    def setForce(self, particule):
        if not self.active:
            return
        if particule == self.particule:
            vecteur = particule.getPosition() - V3D(self.moteur.x, self.moteur.y, 0)
            rayon = vecteur.mod()
            if rayon == 0:
                return  
            tangente = V3D(-vecteur.y, vecteur.x, 0).norm()
            torque = self.moteur.getTorque()
            force_moteur = (torque / rayon) * tangente
            particule.applyForce(force_moteur)



class Pivot(Force):
    def __init__(self, barre, point_fix, point=0.0, k=1000, c=50, name="pivot", active=True):
        super().__init__(V3D(), name=name, active=active)
        self.barre = barre
        self.point_fix = point_fix  # Doit être une Particule
        self.point = point          # Position normalisée sur la barre [-1, 1]
        self.k = k
        self.c = c

        # Initialisation de la distance à l'équilibre (l0)
        theta0 = self.barre.getAngle()
        dir_barre = V3D(np.cos(theta0), np.sin(theta0), 0)
        P0 = self.barre.getPosition() + (self.point * self.barre.L / 2) * dir_barre
        self.l0 = (self.point_fix.getPosition() - P0).mod()  # distance initiale

    def setForce(self, obj):
        if not self.active or obj != self.barre:
            return

        # Position actuelle du point d'attache
        pos = self.barre.getPosition()
        theta = self.barre.getAngle()
        dir_barre = V3D(np.cos(theta), np.sin(theta), 0)
        P = pos + (self.point * self.barre.L / 2) * dir_barre

        # Vecteur distance vers la particule fixe
        delta = self.point_fix.getPosition() - P
        d = delta.mod()
        if d == 0:
            return  # Évite division par 0

        n = delta.norm()  # direction normalisée

        # Vitesse du point
        r = (self.point * self.barre.L / 2) * dir_barre
        omega = self.barre.getAngularSpeed()
        v_translation = self.barre.getSpeed()
        v_rotation = V3D(-omega * r.y, omega * r.x, 0)
        v_point = v_translation + v_rotation

        # Vitesse projetée sur l'axe du ressort
        v_proj = v_point ** n

        # Force de rappel + amortissement
        force = self.k * (d - self.l0) * n - self.c * v_proj * n

        self.barre.applyForce(force, self.point)
