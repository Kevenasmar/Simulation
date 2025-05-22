import pygame
import numpy as np
from MoteurCC import MoteurCC
from vector3D import Vector3D as V3D
from Forces import *
from ControlPID_position import ControlPID_position

if __name__ == "__main__":
    pygame.init()
    W, H = 800, 600
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Commande PID sur la position")
    clock = pygame.time.Clock()

    # === Paramètres du moteur et PID ===
    R, L, k_c, k_e, J, f = 1.0, 0.001, 0.01, 0.01, 0.01, 0.1   # constantes physiques
    P = V3D(55, 45, 0)        # Position visuelle du moteur
    scale = 7.0               # Échelle d’affichage
    dt = 0.01                 # Pas de temps

    # === Initialisation du moteur et du contrôleur PID ===
    moteur = MoteurCC(R, L, k_c, k_e, J, f, P)
    pid = ControlPID_position(moteur, Kp=50.0, Ki=0.0, Kd=1.0)
    pid.setTarget(0)  # angle cible en radians

    # === Slider de consigne angulaire (valeurs entre 0 et 2π) ===
    slider_x = 100
    slider_y = 540
    slider_w = 600
    slider_h = 10
    knob_w = 10
    dragging = False

    # === Sliders pour les gains PID ===
    pid_sliders = {
        "Kp": {"x": 10, "y": 40, "w": 200, "h": 10, "val": pid.Kp},
        "Ki": {"x": 10, "y": 80, "w": 200, "h": 10, "val": pid.Ki},
        "Kd": {"x": 10, "y": 120, "w": 200, "h": 10, "val": pid.Kd},
    }
    active_pid_slider = None

    font = pygame.font.SysFont(None, 24)
    elapsed_time = 0.0

    # === Dessin du slider pour régler la consigne angulaire ===
    def draw_slider(val_rad):
        pygame.draw.rect(screen, (180, 180, 180), (slider_x, slider_y, slider_w, slider_h))
        knob_x = slider_x + int((val_rad / (2 * np.pi)) * slider_w) - knob_w // 2
        pygame.draw.rect(screen, (0, 0, 255), (knob_x, slider_y - 5, knob_w, slider_h + 10))

        # Graduations (repères sur le slider)
        graduations = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]
        labels = ["0", "π/2", "π", "3π/2", "2π"]
        for angle, label in zip(graduations, labels):
            gx = slider_x + int((angle / (2 * np.pi)) * slider_w)
            pygame.draw.line(screen, (0, 0, 0), (gx, slider_y + 15), (gx, slider_y + 25), 2)
            text = font.render(label, True, (0, 0, 0))
            screen.blit(text, (gx - 10, slider_y + 30))

    # === Dessin des sliders PID ===
    def draw_pid_sliders():
        for label, s in pid_sliders.items():
            pygame.draw.rect(screen, (180, 180, 180), (s["x"], s["y"], s["w"], s["h"]))
            knob_x = s["x"] + int((s["val"] / 100) * s["w"])
            pygame.draw.rect(screen, (0, 128, 0), (knob_x - 5, s["y"] - 5, 10, s["h"] + 10))
            text = font.render(f"{label} = {s['val']:.1f}", True, (0, 0, 0))
            screen.blit(text, (s["x"] + s["w"] + 10, s["y"] - 5))

    # === Boucle principale ===
    running = True
    while running:
        screen.fill((250, 250, 250))
        elapsed_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if slider_y - 10 <= my <= slider_y + 30 and slider_x <= mx <= slider_x + slider_w:
                    dragging = True

                # Activation d’un slider PID
                for label, s in pid_sliders.items():
                    if s["y"] - 10 <= my <= s["y"] + 20 and s["x"] <= mx <= s["x"] + s["w"]:
                        active_pid_slider = label

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                active_pid_slider = None

        # === Réglage de la consigne (angle cible) via slider
        if dragging:
            mx, _ = pygame.mouse.get_pos()
            mx = max(slider_x, min(mx, slider_x + slider_w))
            angle = (mx - slider_x) / slider_w * 2 * np.pi
            pid.setTarget(angle)

        # === Réglage des gains PID via sliders
        if active_pid_slider:
            mx, _ = pygame.mouse.get_pos()
            s = pid_sliders[active_pid_slider]
            mx = max(s["x"], min(mx, s["x"] + s["w"]))
            value = ((mx - s["x"]) / s["w"]) * 100
            s["val"] = value
            pid.Kp = pid_sliders["Kp"]["val"]
            pid.Ki = pid_sliders["Ki"]["val"]
            pid.Kd = pid_sliders["Kd"]["val"]

        # === Simulation physique
        pid.simule(dt)

        # === Affichage du moteur
        moteur.gameDraw(scale, screen)

        # === Affichage de l’aiguille de position (angle courant)
        theta = pid.position
        cx, cy = moteur.p.x * scale, moteur.p.y * scale
        length = 50
        end_x = cx + length * np.cos(theta)
        end_y = cy - length * np.sin(theta)
        pygame.draw.line(screen, (0, 0, 128), (cx, cy), (end_x, end_y), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(cx), int(cy)), 5)

        # Affichage du temps et de l’angle courant
        time_text = font.render(f"t = {elapsed_time:.2f} s", True, (0, 0, 0))
        angle_text = font.render(f"θ = {theta:.2f} rad", True, (0, 100, 0))
        screen.blit(time_text, (10, 10))
        screen.blit(angle_text, (700, 10))

        # === Sliders UI
        draw_slider(pid.target)
        draw_pid_sliders()

        pygame.display.flip()
        clock.tick(1 / dt)

    pygame.quit()
