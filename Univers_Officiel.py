from random import random,randint
from vector3D import Vector3D as V3D
from Particule import Particule
import pygame
from pygame.locals import *
from types import MethodType
from MoteurCC import MoteurCC
from Forces import *
from Barre2D import Barre
import math


class Univers(object):
    def __init__(self, name='ici', t0=0, step=0.001, dimensions=(100, 100), game=False, gameDimensions=(1024, 780), fps=60):
        self.name = name                              # Nom de l'univers
        self.time = [t0]                              # Temps initial
        self.population = []                          # Liste des particules
        self.bars = []                                # (Optionnel) Liste alternative de barres
        self.motors = []                              # Liste des moteurs
        self.barres = []                              # Liste des barres rigides
        self.generators = []                          # Liste des forces (générateurs)
        self.step = step                              # Pas de temps de simulation

        self.dimensions = dimensions                  # Dimensions logiques de l'univers

        self.game = game                              # Mode interactif activé ou non
        self.gameDimensions = gameDimensions          # Taille de la fenêtre Pygame
        self.gameFPS = fps                            # Nombre d'images par seconde

        self.scale = gameDimensions[0] / dimensions[0]  # Échelle pixels/unités pour l'affichage

    
    def __str__(self):
        return 'Univers (%s,%g,%g)' % (self.name, self.time[0], self.step)

    def __repr__(self):
        return str(self)
    
    def addEntity(self, *entity):
        for e in entity:                                   
            if isinstance(e, Particule):                   # Si c'est une particule
                self.population.append(e)                  # Ajoute à la liste des particules

            if isinstance(e, MoteurCC):                    # Si c'est un moteur
                self.motors.append(e)                      # Ajoute à la liste des moteurs

            if isinstance(e, Barre):                       # Si c'est une barre rigide
                self.barres.append(e)                      # Ajoute à la liste des barres


    def addGenerators(self, *members):
        for g in members:                   # Parcourt chaque générateur de force passé en argument
            self.generators.append(g)      # L'ajoute à la liste des générateurs de l'univers


    def simulateAll(self):
        for p in self.population:                       # Pour chaque particule de l’univers
            for source in self.generators:              # Applique toutes les forces disponibles
                source.setForce(p)
            p.simulate(self.step)                       # Met à jour son état (position, vitesse...)

        for m in self.motors:                           # Pour chaque moteur
            m.simulate(self.step)                       # Met à jour son état interne

        for b in self.barres:                           # Pour chaque barre
            for source in self.generators:              # Applique toutes les forces disponibles
                source.setForce(b)
            b.simulate(self.step)                       # Met à jour son état (position, angle...)

        self.time.append(self.time[-1] + self.step)     # Avance le temps de la simulation


    def simulateFor(self,duration):
        # On calcule autant de pas que nécessaire pendant duration
        while duration > 0:
            self.simulateAll()
            duration -= self.step
        
    def plot(self):
        from pylab import figure, legend, show          # Import des fonctions pour les tracés matplotlib

        figure(self.name)                               # Crée une figure avec le nom de l'univers comme titre

        for p in self.population:                       # Parcourt toutes les particules
            p.plot()                                    # Trace la trajectoire de la particule

        for b in self.barres:                           # Parcourt toutes les barres
            b.plot()                                    # Trace la trajectoire de la barre

        legend()                                        # Affiche la légende du graphique
        show()                                          # Affiche le graphique

    
    def gameInteraction(self,events,keys):
        # Fonction qui sera surchargée par le client pour définir ses intéractions
        pass

    def simulateRealTime(self):
        import pygame
        pygame.init()
        W, H = self.gameDimensions
        screen = pygame.display.set_mode((W, H))
        clock = pygame.time.Clock()
        running = self.game

        while running:
            screen.fill((255, 255, 255))
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
            for p in self.population:
                if hasattr(p, 'gameDraw'):
                    p.gameDraw(self.scale, screen)

            for m in self.motors:
                if hasattr(m, 'gameDraw'):
                    m.gameDraw(self.scale, screen)
            
            for b in self.barres : 
                if hasattr(b,'gameDraw'):
                    b.gameDraw(self.scale,screen)

            # Draw time
            font_obj = pygame.font.Font('freesansbold.ttf', 12)
            text_surface_obj = font_obj.render(('time: %.2f' % self.time[-1]), True, 'black', (255, 255, 255))
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.topleft = (0, 0)
            screen.blit(text_surface_obj, text_rect_obj)

            pygame.display.flip()
            clock.tick(self.gameFPS)

        pygame.quit()



    



    