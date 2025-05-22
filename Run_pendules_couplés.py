# === Import des modules nécessaires ===
from Univers_Officiel import Univers       # Environnement de simulation
from Barre2D import Barre                  # Classe de barre rigide
from vector3D import Vector3D as V3D       # Classe de vecteur 3D
from Forces import *                       # Import de toutes les forces (gravité, ressort, etc.)
from Particule import Particule            # Classe de particule ponctuelle
from math import radians                   # Conversion degré ↔ radian
import pygame                              # Interface graphique Pygame

# === Initialisation Pygame ===
pygame.init()
WIDTH, HEIGHT = 1024, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# === Définition des couleurs utilisées ===
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)
RED = (255, 50, 50)

# === Création des boutons de l’interface utilisateur ===
button1 = pygame.Rect(50, 50, 200, 50)     # Bouton pour Mode propre 1
button2 = pygame.Rect(300, 50, 200, 50)    # Bouton pour Mode propre 2
mode_selected = 0                          # Aucun mode sélectionné par défaut

# === Création de l’univers et des entités ===
U = Univers(game=True)

# Particules fixes A et B
A = Particule(fix=True, p0=V3D(30, 30, 0), color="blue")
B = Particule(fix=True, p0=V3D(70, 30, 0), color="red")

# Deux barres attachées à A et B
b1 = Barre(mass=1, p0=V3D(30, 30, 0), t0=radians(90), long=20, color='blue')
b2 = Barre(mass=1, p0=V3D(70, 30, 0), t0=radians(90), long=20, color='red')

# Ajout à l’univers
U.addEntity(A, B, b1, b2)

# === Liaisons et forces constantes ===
gravity = Gravity()                               # Force de gravité
pivotA = Pivot(b1, A, point=-1, k=1000, c=100)     # Pivot entre A et b1 (à l’extrémité gauche)
pivotB = Pivot(b2, B, point=-1, k=1000, c=100)     # Pivot entre B et b2 (à l’extrémité gauche)
link = SpringDamperBarre(b1, 1, b2, 1, k=5, c=0.1)  # Ressort reliant les extrémités droites des deux barres

# Forces des modes propres, désactivées par défaut
mode1 = ForceSelectBarre(V3D(200, 0, 0), b1, 1, active=False)   # Force vers la droite sur b1
mode12 = ForceSelectBarre(V3D(-200, 0, 0), b2, 1, active=False) # Force vers la gauche sur b2
mode2 = ForceSelectBarre(V3D(200, 0, 0), b1, 1, active=False)   # Force vers la droite sur b1
mode22 = ForceSelectBarre(V3D(200, 0, 0), b2, 1, active=False)   # Force vers la drotie sur b2

# Ajout des forces fixes à l’univers
U.addGenerators(gravity, pivotA, pivotB, link)

# === Fonction d'interaction clavier ===
def interaction(events, keys):
    global mode_selected
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if mode_selected == 1:
                mode1.active = True
                mode12.active = True
                print("Mode propre 1 activé")
            elif mode_selected == 2:
                mode2.active = True
                mode22.active = True
                print("Mode propre 2 activé")

U.gameInteraction = interaction

# === Boucle principale Pygame ===
running = True
while running:
    screen.fill(WHITE)
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    # Gestion des événements utilisateur
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button1.collidepoint(event.pos):
                # Activation du Mode propre 1
                if mode1 not in U.generators:
                    U.addGenerators(mode1, mode12)
                if mode2 in U.generators:
                    U.generators.remove(mode2)
                    U.generators.remove(mode22)
                mode_selected = 1
                print("Mode propre 1 sélectionné")

            elif button2.collidepoint(event.pos):
                # Activation du Mode propre 2
                if mode2 not in U.generators:
                    U.addGenerators(mode2,mode22)
                if mode1 in U.generators:
                    U.generators.remove(mode1)
                    U.generators.remove(mode12)
                mode_selected = 2
                print("Mode propre 2 sélectionné")

    # Interaction personnalisée (gestion clavier)
    U.gameInteraction(events, keys)

    # Simulation physique
    U.simulateFor(1 / U.gameFPS)
    for g in U.generators:
        if hasattr(g, "postStep"):
            g.postStep()

    # === Dessin de la grille et des objets ===
    screen.fill(WHITE)
    grid_spacing = int(10 * U.scale)
    for x in range(0, WIDTH, grid_spacing):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_spacing):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    # Affichage des particules et des barres
    for p in U.population:
        if hasattr(p, 'gameDraw'):
            p.gameDraw(U.scale, screen)
    for b in U.barres:
        if hasattr(b, 'gameDraw'):
            b.gameDraw(U.scale, screen)

    # === Dessin des boutons ===
    pygame.draw.rect(screen, BLUE if mode_selected == 1 else GRAY, button1)
    pygame.draw.rect(screen, RED if mode_selected == 2 else GRAY, button2)
    screen.blit(font.render("Mode Propre 1", True, (0, 0, 0)), (button1.x + 20, button1.y + 10))
    screen.blit(font.render("Mode Propre 2", True, (0, 0, 0)), (button2.x + 20, button2.y + 10))

    # === Instructions pour l’utilisateur ===
    font_obj = pygame.font.Font(None, 24)
    instruction_text = "Sélectionner le mode et appuyer sur ESPACE pour l'activer"
    text_surface = font_obj.render(instruction_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midbottom = (WIDTH // 2, HEIGHT - 15)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(U.gameFPS)

# === Fin de la simulation ===
pygame.quit()
