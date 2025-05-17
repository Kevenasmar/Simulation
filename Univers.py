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
            if hasattr(p, 'applyForce'):
                for source in self.generators:
                    if isinstance(source, ForceMoteur):
                        for m in self.motors:
                            source.setForce(m, p)
                    else:
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

             # === DRAW GRID ===
            grid_color = (200, 200, 200)  # light gray
            grid_spacing = 10  # 10 units in simulation space
            pixel_spacing = int(grid_spacing * self.scale)

            # Vertical lines
            for x in range(0, W, pixel_spacing):
                pygame.draw.line(screen, grid_color, (x, 0), (x, H), 1)

            # Horizontal lines
            for y in range(0, H, pixel_spacing):
                pygame.draw.line(screen, grid_color, (0, y), (W, y), 1)

            # === DRAW OBJECTS ===
            for t in self.population:
                if hasattr(t, 'gameDraw'):
                    t.gameDraw(self.scale, screen)

            for t in self.motors:
                if hasattr(t, 'gameDraw'):
                    t.gameDraw(self.scale, screen)

            # Flip vertically if needed
            flip_surface = pygame.transform.flip(screen, False, True)
            screen.blit(flip_surface, (0, 0))

            # Draw time
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
    def __init__(self, moteur, particule, active=True, name="force_moteur"):
        super().__init__(V3D(), name, active)
        self.moteur = moteur
        self.particule = particule

    def setForce(self, particule):
        if not self.active or particule != self.particule:
            return

        # Calcul du vecteur depuis le moteur vers la particule
        moteur_pos = V3D(self.moteur.x, self.moteur.y, 0)
        d = self.particule.getPosition() - moteur_pos

        if d.mod() == 0:
            return  # éviter une division par zéro

        # Tangente (rotation +90° dans le plan)
        tangent = V3D(-d.y, d.x, 0).norm()

        # Force proportionnelle au couple moteur
        force_strength = self.moteur.getTorque()
        force = force_strength * tangent

        self.particule.applyForce(force)




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
    bounce_x = Bounce_x()
    bounce_y = Bounce_y()
    force_moteur = ForceMoteur(moteur = moteur, particule=particule)
    
    monUnivers.addGenerators(bounce_x, bounce_y, force_moteur)

    monUnivers.simulateRealTime()

    monUnivers.plot()
