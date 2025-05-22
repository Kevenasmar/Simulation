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

# === Sliders (k, c, perturbation)
sliders = {
    "k": {"x": 850, "y": 20, "w": 150, "h": 10, "val": 30},
    "c": {"x": 850, "y": 50, "w": 150, "h": 10, "val": 1},
    "perturb": {"x": 850, "y": 80, "w": 150, "h": 10, "val": 1000},
}
active_slider = None

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
link1 = SpringDamperBarre(b1, -1/5, b2, -2/3, k=30, c=1)
link2 = SpringDamperBarre(b1,  1/5, b2,  2/3, k=30, c=1)
link3 = SpringDamperBarre(b2, -2/3, b3, -2/3, k=30, c=1)
link4 = SpringDamperBarre(b2,  2/3, b3,  2/3, k=30, c=1)
links = [link1, link2, link3, link4]
U.addGenerators(*links)

# Gravité (ajoutée plus tard)
# grav = Gravity()

# Modes propres (forces)
mode11 = ForceSelectBarre(V3D(0, -1000, 0), b2, 0, active=False)
mode12 = ForceSelectBarre(V3D(0, -1000, 0), b3, 0, active=False)
mode21 = ForceSelectBarre(V3D(0, 1000, 0), b2, 0, active=False)
mode22 = ForceSelectBarre(V3D(0, -1000, 0), b3, 0, active=False)
mode31 = ForceSelectBarre(V3D(0, -500, 0), b2, -1, active=False)
mode32 = ForceSelectBarre(V3D(0, -500, 0), b3, -1, active=False)
mode41 = ForceSelectBarre(V3D(0, -500, 0), b2, 1, active=False)
mode42 = ForceSelectBarre(V3D(0, -500, 0), b3, -1, active=False)

# Associer les forces aux boutons
buttons[0]["forces"] = [mode11, mode12]
buttons[1]["forces"] = [mode21, mode22]
buttons[2]["forces"] = [mode31, mode32]
buttons[3]["forces"] = [mode41, mode42]

U.addGenerators(mode11, mode12, mode21, mode22, mode31, mode32, mode41, mode42)

# Interaction
def interaction(events, keys):
    global mode_selected, active_slider
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, button in enumerate(buttons):
                if button["rect"].collidepoint(mx, my):
                    mode_selected = i
                    print(f"Mode propre {i+1} sélectionné")
            for label, s in sliders.items():
                if s["y"] - 5 <= my <= s["y"] + 15 and s["x"] <= mx <= s["x"] + s["w"]:
                    active_slider = label
        elif event.type == pygame.MOUSEBUTTONUP:
            active_slider = None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and mode_selected is not None:
            for f in buttons[mode_selected]["forces"]:
                force_val = sliders["perturb"]["val"]
                f.force = V3D(0, -force_val, 0) if f.force.y < 0 else V3D(0, force_val, 0)
                f.active = True

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

    if active_slider:
        mx, _ = pygame.mouse.get_pos()
        s = sliders[active_slider]
        mx = max(s["x"], min(mx, s["x"] + s["w"]))
        s["val"] = ((mx - s["x"]) / s["w"]) * 100  # Échelle de 0 à 100
        for link in links:
            link.k = sliders["k"]["val"]
            link.c = sliders["c"]["val"]

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

    # Sliders UI
    for label, s in sliders.items():
        pygame.draw.rect(screen, GRAY, (s["x"], s["y"], s["w"], s["h"]))
        knob_x = s["x"] + int((s["val"] / 100) * s["w"])
        pygame.draw.rect(screen, RED, (knob_x - 5, s["y"] - 5, 10, s["h"] + 10))
        slider_text = font.render(f"{label} = {s['val']:.1f}", True, (0, 0, 0))
        screen.blit(slider_text, (s["x"] + s["w"] + 10, s["y"] - 5))

    # Instructions
    font_obj = pygame.font.Font(None, 24)
    instruction_text = "Sélectionner le mode et appuyer sur ESPACE pour l'activer"
    text_surface = font_obj.render(instruction_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midbottom = (WIDTH // 2, 100)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(U.gameFPS)

pygame.quit()
