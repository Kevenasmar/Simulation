from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
import pygame
from Particule import Particule

if __name__ == "__main__":
    # Initialisation Pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Contrôle barre avec flèches")
    clock = pygame.time.Clock()

    # Univers
    U = Univers(game=True, gameDimensions=(WIDTH, HEIGHT))

    # Entités
    p1 = Particule(p0=V3D(50, 60), fix=True)
    b1 = Barre(mass=1, p0=V3D(45, 40))
    b2 = Barre()
    U.addEntity(p1, b1)

    # Liaison glissière
    glissiere = GlissiereBarreParticule(b1, p1, axis=V3D(1, 0, 0))
    U.addGenerators(Gravity(),glissiere)

    # Boucle principale
    running = True
    while running:
        screen.fill((255, 255, 255))

        # Gestion événements clavier
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if keys[pygame.K_LEFT]:
            b1.applyForce(V3D(-500, 0, 0),0)
        elif keys[pygame.K_RIGHT]:
            b1.applyForce(V3D(500, 0, 0),0)
        else:
            b1.speed[-1] = V3D(0, 0, 0)

        # Simulation et affichage
        U.simulateFor(1 / U.gameFPS)
        for g in U.generators:
            if hasattr(g, "postStep"):
                g.postStep()

        # Affichage objets
        for p in U.population:
            if hasattr(p, 'gameDraw'):
                p.gameDraw(U.scale, screen)
        for b in U.barres:
            if hasattr(b, 'gameDraw'):
                b.gameDraw(U.scale, screen)

        pygame.display.flip()
        clock.tick(U.gameFPS)

    pygame.quit()
