from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
from Particule import Particule
from math import radians
import pygame

# === Initialisation Pygame
pygame.init()
WIDTH, HEIGHT = 1024, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# === Couleurs
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)
RED = (255, 50, 50)

# === Boutons UI
buttons = [
    {"rect": pygame.Rect(50, 550, 200, 40), "label": "Mode propre 1", "forces": []},
    {"rect": pygame.Rect(300, 550, 200, 40), "label": "Mode propre 2", "forces": []},
    {"rect": pygame.Rect(550, 550, 200, 40), "label": "Mode propre 3", "forces": []},
    {"rect": pygame.Rect(800, 550, 200, 40), "label": "Mode propre 4", "forces": []}
]

mode_selected = None

# === Simulation setup
U = Univers(game=True, gameDimensions=(WIDTH, HEIGHT))

# Barres
b1 = Barre(mass=1, p0=V3D(0, 30, 0), fix=True, long=100)
b2 = Barre(mass=1, p0=V3D(35, 35, 0), long=30, color='blue')
b3 = Barre(mass=1, p0=V3D(35, 40, 0), long=30, color='green')
U.addEntity(b1, b2, b3)

# Liens uniquement (au début)
link1 = SpringDamperBarre(b1, -1/5, b2, -2/3, k=25, c=1)
link2 = SpringDamperBarre(b1,  1/5, b2,  2/3, k=25, c=1)
link3 = SpringDamperBarre(b2, -2/3, b3, -2/3, k=25, c=1)
link4 = SpringDamperBarre(b2,  2/3, b3,  2/3, k=25, c=1)
U.addGenerators(link1, link2, link3, link4)

# Gravité (ajoutée plus tard)
grav = Gravity()

# Modes propres (forces)
mode11 = ForceSelectBarre(V3D(0, -100, 0), b2, 0, active=False)
mode12 = ForceSelectBarre(V3D(0, -100, 0), b3, 0, active=False)
mode21 = ForceSelectBarre(V3D(0, 100, 0), b2, 0, active=False)
mode22 = ForceSelectBarre(V3D(0, -1000, 0), b3, 0, active=False)
mode31 = ForceSelectBarre(V3D(0, -100, 0), b2, -1, active=False)
mode32 = ForceSelectBarre(V3D(0, -100, 0), b3, -1, active=False)
mode41 = ForceSelectBarre(V3D(0, -100, 0), b2, 1, active=False)
mode42 = ForceSelectBarre(V3D(0, -100, 0), b3, -1, active=False)

# Associer les forces aux boutons
buttons[0]["forces"] = [mode11, mode12]
buttons[1]["forces"] = [mode21, mode22]
buttons[2]["forces"] = [mode31, mode32]
buttons[3]["forces"] = [mode41, mode42]

U.addGenerators(mode11, mode12, mode21, mode22, mode31, mode32, mode41, mode42)

# Interaction
activated_gravity = False

def interaction(events, keys):
    global mode_selected, activated_gravity
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, button in enumerate(buttons):
                if button["rect"].collidepoint(event.pos):
                    mode_selected = i
                    print(f"Mode propre {i+1} sélectionné")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and mode_selected is not None:
            # Ajouter gravité une seule fois
            if not activated_gravity:
                U.addGenerators(grav)
                activated_gravity = True
            for f in buttons[mode_selected]["forces"]:
                f.active = True
            print(f"Mode propre {mode_selected+1} activé")

U.gameInteraction = interaction

# Boucle principale
running = True
while running:
    screen.fill(WHITE)
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    U.gameInteraction(events, keys)
    U.simulateFor(1 / U.gameFPS)
    for g in U.generators:
        if hasattr(g, "postStep"):
            g.postStep()

    # Dessin
    screen.fill(WHITE)
    grid_spacing = int(10 * U.scale)
    for x in range(0, WIDTH, grid_spacing):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_spacing):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    for p in U.population:
        if hasattr(p, 'gameDraw'):
            p.gameDraw(U.scale, screen)
    for b in U.barres:
        if hasattr(b, 'gameDraw'):
            b.gameDraw(U.scale, screen)

    for i, button in enumerate(buttons):
        color = BLUE if mode_selected == i else GRAY
        pygame.draw.rect(screen, color, button["rect"])
        pygame.draw.rect(screen, (0, 0, 0), button["rect"], 2)
        text = font.render(button["label"], True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=button["rect"].center))

    # Instructions
    font_obj = pygame.font.Font(None, 24)
    instruction_text = "Sélectionner le mode et appuyer sur ESPACE pour l'activer"
    text_surface = font_obj.render(instruction_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midbottom = (WIDTH // 2, HEIGHT - 5)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(U.gameFPS)

pygame.quit()