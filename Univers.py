from random import random,randint
from vector3D import Vector3D as V3D
from Particule import Particule
import pygame
from pygame.locals import *
from types import MethodType
from MoteurCC import MoteurCC

class Univers(object):
    def __init__(self, name='ici', t0=0, step=0.1, dimensions=(100, 100), game=False, gameDimensions=(1024, 780), fps=60):
        self.name = name
        self.time = [t0]
        self.population = []
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
            self.population.append(m)

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



if __name__ == '__main__':
    from pylab import figure, show, legend

    R = 1.0
    L = 0.001
    k_c = 0.01
    k_e = 0.01
    J = 0.01
    f = 0.1
    Um = 1.0

    # Create an instance of Univers with game mode enabled
    monUnivers = Univers(game=True, gameDimensions=(1024, 780))

    # Create instances of Particule and MoteurCC
    P0 = Particule(p0=V3D(10,10,0))    
    moteur = MoteurCC(R, L, k_c, k_e, J, f)

    # Set the positions of the particle and motor to the center of the screen
    moteur.x, moteur.y = 50,40

    # Add the particle and motor to the universe
    monUnivers.addEntity(P0)
    monUnivers.addEntity(moteur)

    # Simulate the universe in real-time
    monUnivers.simulateRealTime()

    # Plot the results
    monUnivers.plot()
