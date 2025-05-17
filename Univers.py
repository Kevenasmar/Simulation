from random import random,randint
from vector3D import Vector3D as V3D
from Particule import Particule
import pygame
from pygame.locals import *
from types import MethodType
from MoteurCC import MoteurCC
import math


class Univers(object):
    def __init__(self, name='ici', t0=0, step=0.1, dimensions=(100, 100), game=False, gameDimensions=(1024, 780), fps=60):
        self.name = name
        self.time = [t0]
        self.population = []
        self.bars = []
        self.motors = []
        self.generators = []
        self.step = step

        self.dimensions = dimensions

        self.game = game
        self.gameDimensions = gameDimensions
        self.gameFPS = fps

        self.scale = gameDimensions[0] / dimensions[0]

    def __str__(self):
        return 'Univers (%s,%g,%g)' % (self.name, self.time[0], self.step)

    def __repr__(self):
        return str(self)

    def addEntity(self, *members):
        for m in members:
            if isinstance(m, Particule):
                self.population.append(m)
            if isinstance(m,MoteurCC):
                self.motors.append(m)

    def addGenerators(self, *members):
        for g in members:
            self.generators.append(g)

    def simulateAll(self):
        for p in self.population:
            # Seules les entités ayant une méthode applyForce (i.e. les particules) reçoivent les forces
            if hasattr(p, 'applyForce'):
                for source in self.generators:
                    source.setForce(p)
            p.simulate(self.step)
        self.time.append(self.time[-1] + self.step)

    def simulateFor(self, duration):
        while duration > 0:
            self.simulateAll()
            duration -= self.step

    def plot(self):
        from pylab import figure, legend, show

        figure(self.name)
        for agent in self.population:
            if hasattr(agent, 'plot'):
                agent.plot()
        legend()
        show()

    def gameInteraction(self, events, keys):
        # A surcharger par le client
        pass

    def simulateRealTime(self):
        import pygame
        pygame.init()
        W, H = self.gameDimensions
        screen = pygame.display.set_mode((W, H))
        clock = pygame.time.Clock()
        running = self.game

        while running:
            screen.fill((240, 240, 240))
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            events = pygame.event.get()

            if keys[pygame.K_ESCAPE]:
                running = False

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            self.gameInteraction(events, keys)
            self.simulateFor(1 / self.gameFPS)

            for t in self.population:
                if hasattr(t, 'gameDraw'):
                    t.gameDraw(self.scale, screen)

            for t in self.motors:
                if hasattr(t, 'gameDraw'):
                    t.gameDraw(self.scale, screen)


            flip_surface = pygame.transform.flip(screen, False, True)
            screen.blit(flip_surface, (0, 0))

            font_obj = pygame.font.Font('freesansbold.ttf', 12)
            text_surface_obj = font_obj.render(('time: %.2f' % self.time[-1]), True, 'green', (240, 240, 240))
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.topleft = (0, 0)
            screen.blit(text_surface_obj, text_rect_obj)

            pygame.display.flip()
            clock.tick(self.gameFPS)

        pygame.quit()


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
                entity.applyForce(self.g*entity.mass)


    
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



class ForceMoteur(Force):
    def __init__(self, moteur, particule, distance, active=True, name="force_moteur"):
        super().__init__(V3D(), name, active)
        self.moteur = moteur
        self.particule = particule
        self.distance = distance

    def setForce(self, particule):
        if self.active and particule == self.particule:
            # Calculate the direction vector from the motor to the particle
            dx = particule.getPosition().x - self.moteur.x
            dy = particule.getPosition().y - self.moteur.y

            # Calculate the angle for rotation
            angle = math.atan2(dy, dx)
            angle += 1  # Rotate by 1 radian per second

            # Calculate the new position based on the rotation
            new_x = self.moteur.x + self.distance * math.cos(angle)
            new_y = self.moteur.y + self.distance * math.sin(angle)

            # Calculate the force needed to move the particle to the new position
            force_x = (new_x - particule.getPosition().x) * particule.mass
            force_y = (new_y - particule.getPosition().y) * particule.mass

            # Apply the force to the particle
            particule.applyForce(V3D(force_x, force_y, 0))


if __name__ == '__main__':
    from pylab import figure, show, legend

    R = 1.0
    L = 0.001
    k_c = 0.01
    k_e = 0.01
    J = 0.01
    f = 0.1
    Um = 1.0

    monUnivers = Univers(game=True)

    particule = Particule(p0=V3D(40,50,0))
    moteur = MoteurCC(R, L, k_c, k_e, J, f, V3D(50,50,0))

    # Add the particle and motor to the universe
    monUnivers.addEntity(particule)
    monUnivers.addEntity(moteur)

    # Add some forces
    gravity = Gravity()
    bounce_y = Bounce_y()
    monUnivers.addGenerators(gravity, bounce_y)

    # Add ForceMoteur for the particle
    distance = 50  # Set the distance between the motor and the particle
    # force_moteur = ForceMoteur(moteur, particule, distance)
    # monUnivers.addGenerators(force_moteur)

    monUnivers.simulateRealTime()

    monUnivers.plot()
