from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
import pygame
from Particule import Particule
import numpy as np
import matplotlib.pyplot as plt

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
    b2 = Barre(mass=1, p0=V3D(50, 40), t0=np.radians(-90))
    U.addEntity(p1, b1, b2)

    # Liaison glissière et pivot
    glissiere = GlissiereBarreParticule(b1, p1, axis=V3D(1, 0, 0))
    pivot = PivotBarre(b1, 0, b2, -1)
    U.addGenerators(Gravity(), glissiere, pivot)

    # Stockage de la position de l'extrémité droite de b2
    positions = []

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
            b1.applyForce(V3D(-100, 0, 0), 0)
        elif keys[pygame.K_RIGHT]:
            b1.applyForce(V3D(100, 0, 0), 0)
        else:
            b1.speed[-1] = V3D(0, 0, 0)

        # Sauvegarde position extrémité droite de b2 (point = 1)
        pos_ext = b2.getPoint(1)
        positions.append((pos_ext.x, pos_ext.y))

        # Simulation
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

    # === Plot de la trajectoire de l'extrémité droite de b2 ===
    X = [p[0] for p in positions]
    Y = [p[1] for p in positions]

    plt.figure()
    plt.plot(X, Y, label="Extrémité droite de b2")
    plt.xlabel("Position X")
    plt.ylabel("Position Y")
    plt.title("Trajectoire de l’extrémité droite de la barre 2")
    plt.grid()
    plt.axis('equal')
    plt.legend()
    plt.show()
