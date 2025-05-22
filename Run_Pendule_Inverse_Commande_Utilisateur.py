# === Imports nécessaires ===
from Univers_Officiel import Univers          # Classe principale de simulation
from Barre2D import Barre                     # Barre rigide 2D
from vector3D import Vector3D as V3D          # Vecteurs 3D utilisés pour positions, vitesses, forces...
from Forces import *                          # Ensemble des forces disponibles (glissière, gravité, etc.)
import pygame                                 # Librairie graphique
from Particule import Particule               # Particule ponctuelle (fixe ou mobile)
import numpy as np                            # Calcul numérique
import matplotlib.pyplot as plt               # Affichage graphique matplotlib

# === Code principal ===
if __name__ == "__main__":
    # === Initialisation de Pygame ===
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)

    # === Dimensions de la fenêtre Pygame ===
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Contrôle barre avec flèches")
    clock = pygame.time.Clock()

    # === Création de l’univers de simulation ===
    U = Univers(game=True, gameDimensions=(WIDTH, HEIGHT))

    # === Entités physiques ===
    p1 = Particule(p0=V3D(50, 60), fix=True)           # Point fixe
    b1 = Barre(mass=1, p0=V3D(45, 40), color='blue')   # Base mobile
    b2 = Barre(mass=1, p0=V3D(50, 40), t0=np.radians(-90))  # Barre pendante (angle initial de -90°)
    U.addEntity(p1, b1, b2)

    # === Liaisons mécaniques ===
    glissiere = GlissiereBarreParticule(b1, p1, axis=V3D(1, 0, 0))  # b1 ne bouge que horizontalement
    pivot = PivotBarre(b1, 0, b2, -1)                               # Pivot entre b1 et b2
    U.addGenerators(Gravity(), glissiere, pivot)                   # Ajout des forces dans l’univers

    # === Liste pour stocker la trajectoire de l’extrémité droite de b2 ===
    positions = []

    # === Boucle principale Pygame ===
    running = True
    while running:
        screen.fill((255, 255, 255))  # Fond blanc

        # === Lecture des événements clavier ===
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # === Application des forces selon les touches fléchées ===
        if keys[pygame.K_LEFT]:
            b1.applyForce(V3D(-100, 0, 0), 0)  # Force vers la gauche
        elif keys[pygame.K_RIGHT]:
            b1.applyForce(V3D(100, 0, 0), 0)   # Force vers la droite
        else:
            b1.speed[-1] = V3D(0, 0, 0)        # Arrêt si aucune touche n’est pressée

        # === Sauvegarde de la position de l’extrémité droite de b2 (point = 1) ===
        pos_ext = b2.getPoint(1)
        positions.append((pos_ext.x, pos_ext.y))

        # === Simulation physique ===
        U.simulateFor(1 / U.gameFPS)
        for g in U.generators:
            if hasattr(g, "postStep"):
                g.postStep()

        # === Affichage graphique des entités ===
        for p in U.population:
            if hasattr(p, 'gameDraw'):
                p.gameDraw(U.scale, screen)
        for b in U.barres:
            if hasattr(b, 'gameDraw'):
                b.gameDraw(U.scale, screen)

        # === Message d’aide à l’écran ===
        text_surface = font.render("Jouez avec les flèches pour faire bouger la base", True, (0, 0, 0))
        screen.blit(text_surface, (20, 20))

        # === Mise à jour de l’écran ===
        pygame.display.flip()
        clock.tick(U.gameFPS)

    pygame.quit()

    # === Affichage matplotlib de la trajectoire enregistrée ===
    X = [p[0] for p in positions]
    Y = [p[1] for p in positions]

    plt.figure()
    plt.plot(X, Y, label="Extrémité droite de b2")
    plt.xlabel("Position X")
    plt.ylabel("Position Y")
    plt.title("Trajectoire de l'extrémité droite de la barre 2")
    plt.grid()
    plt.axis('equal')
    plt.legend()
    plt.show()
