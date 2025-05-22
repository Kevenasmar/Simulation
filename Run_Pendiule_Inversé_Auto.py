from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
from Particule import Particule
import pygame
import numpy as np

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pendule inverse automatisé avec sliders")
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

    # === Forces ===
    perturbation = ForceSelectBarre(barre=b2, force=V3D(), point=1)
    select_force = ForceSelectBarre(barre=b1, force=V3D(0, 0, 0), point=0)
    U.addGenerators(Gravity(), glissiere, pivot, select_force, perturbation)

    # === Sliders ===
    sliders = {
        "Kp": {"x": 10, "y": 10, "w": 200, "h": 10, "val": 50},
        "Kd": {"x": 10, "y": 40, "w": 200, "h": 10, "val": 100},
        "Perturb": {"x": 10, "y": 70, "w": 200, "h": 10, "val": 20},
    }
    active_slider = None

    # === Boucle principale ===
    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for label, s in sliders.items():
                    if s["y"] - 5 <= my <= s["y"] + 15 and s["x"] <= mx <= s["x"] + s["w"]:
                        active_slider = label
            elif event.type == pygame.MOUSEBUTTONUP:
                active_slider = None

        if active_slider:
            mx, _ = pygame.mouse.get_pos()
            s = sliders[active_slider]
            mx = max(s["x"], min(mx, s["x"] + s["w"]))
            value = ((mx - s["x"]) / s["w"]) * 200  # Scale max = 200
            s["val"] = value

        # === Clavier ===
        keys = pygame.key.get_pressed()
        perturbation_force = sliders["Perturb"]["val"]
        if keys[pygame.K_LEFT]:
            perturbation.force = V3D(-perturbation_force, 0, 0)
            perturbation.active = True
        elif keys[pygame.K_RIGHT]:
            perturbation.force = V3D(perturbation_force, 0, 0)
            perturbation.active = True

        # === PID ===
        Kp = sliders["Kp"]["val"]
        Kd = sliders["Kd"]["val"]
        theta = b2.getAngle() - np.radians(-90)
        omega = b2.getAngularSpeed()
        Fx = Kp * theta + Kd * omega
        select_force.force = V3D(Fx, 0, 0)
        select_force.active = True

        # === Simulation ===
        U.simulateFor(1 / U.gameFPS)
        select_force.active = False
        perturbation.active = False

        # === Affichage ===
        for b in U.barres:
            if hasattr(b, 'gameDraw'):
                b.gameDraw(U.scale, screen)

        text_surface = font.render("Stabilisation automatique du pendule inversé", True, (0, 0, 0))
        screen.blit(text_surface, (250, 450))
        text_surface2 = font.render("Jouez avec les flèches pour appliquer la force sur le penudule", True, (0, 0, 0))
        screen.blit(text_surface2, (190, 500))

        # === Affichage sliders ===
        for label, s in sliders.items():
            pygame.draw.rect(screen, (180, 180, 180), (s["x"], s["y"], s["w"], s["h"]))
            knob_x = s["x"] + int((s["val"] / 200) * s["w"])
            pygame.draw.rect(screen, (0, 128, 0), (knob_x - 5, s["y"] - 5, 10, s["h"] + 10))
            text = font.render(f"{label} = {s['val']:.1f}", True, (0, 0, 0))
            screen.blit(text, (s["x"] + s["w"] + 10, s["y"] - 5))

        pygame.display.flip()
        clock.tick(U.gameFPS)

    pygame.quit()
