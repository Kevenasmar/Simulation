from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
from Particule import Particule
import pygame
import numpy as np

if __name__ == "__main__":
    # Initialisation Pygame
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pendule inverse automatisé")
    clock = pygame.time.Clock()

    # Univers
    U = Univers(game=True, gameDimensions=(WIDTH, HEIGHT))

    # === Entités ===
    p1 = Particule(p0=V3D(50, 60), fix=True)
    b1 = Barre(mass=1, p0=V3D(45, 40))  # Base mobile
    b2 = Barre(mass=1, p0=V3D(50, 40), t0=np.radians(-90))  # Pendule inversé

    U.addEntity(p1, b1, b2)

    # === Liaisons ===
    glissiere = GlissiereBarreParticule(b1, p1, axis=V3D(1, 0, 0))
    pivot = PivotBarre(b1, 0, b2, -1)

    # === Force perturbatrice ===
    perturbation = ForceSelectBarre(barre=b2, force=V3D(), point=1)


    # === Force correctrice 
    select_force = ForceSelectBarre(barre=b1, force=V3D(0, 0, 0), point=0)
    U.addGenerators(Gravity(), glissiere, pivot, select_force, perturbation)

    # === Boucle principale ===
    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                perturbation.force = V3D(-20, 0, 0)
                perturbation.active = True

            elif keys[pygame.K_RIGHT]:
                perturbation.force = V3D(20, 0, 0)
                perturbation.active = True


        # === PID correcteur sur l'angle du pendule
        theta = b2.getAngle() - np.radians(-90)
        omega = b2.getAngularSpeed()

        Kp = 100
        Kd = 100

        Fx = Kp * theta + Kd * omega

        # Activer la force juste pour ce pas
        select_force.force = V3D(Fx, 0, 0)
        select_force.active = True

        # === Simulation (un seul pas)
        U.simulateFor(1 / U.gameFPS)

        # Désactiver la force juste après le pas
        select_force.active = False

        # === Affichage des barres
        for b in U.barres:
            if hasattr(b, 'gameDraw'):
                b.gameDraw(U.scale, screen)

        # === Affichage du texte
        text_surface = font.render("Stabilisation automatique du pendule inversé", True, (0, 0, 0))
        screen.blit(text_surface, (20, 20))

        pygame.display.flip()
        clock.tick(U.gameFPS)

    pygame.quit()
