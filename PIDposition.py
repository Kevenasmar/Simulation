import pygame
import numpy as np
from MoteurCC import MoteurCC
from vector3D import Vector3D as V3D
from Forces import *

class ControlPID_position:
    def __init__(self, moteur, Kp=0.0, Ki=0.0, Kd=0.0):
        self.m = moteur
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.target = 0.0
        self.erreur_cumulee = 0.0
        self.derniere_erreur = 0.0
        self.voltage = 0.0
        self.position = 0.0
        self.positions = []

    def setTarget(self, position_cible):
        self.target = position_cible

    def getVoltage(self):
        return self.voltage

    def simule(self, step):
        self.position += self.m.getSpeed() * step

        erreur = self.target - self.position
        self.erreur_cumulee += erreur * step
        derivee = (erreur - self.derniere_erreur) / step if step > 0 else 0.0
        self.derniere_erreur = erreur

        self.voltage = (
            self.Kp * erreur +
            self.Ki * self.erreur_cumulee +
            self.Kd * derivee
        )

        self.m.setVoltage(self.voltage)
        self.m.simulate(step)
        self.positions.append(self.position)

if __name__ == "__main__":
    pygame.init()
    W, H = 800, 600
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Commande PID avec slider")
    clock = pygame.time.Clock()

    R, L, k_c, k_e, J, f = 1.0, 0.001, 0.01, 0.01, 0.01, 0.1
    P = V3D(50, 50, 0)
    scale = 7.0
    dt = 0.01

    moteur = MoteurCC(R, L, k_c, k_e, J, f, P)
    pid = ControlPID_position(moteur, Kp=120.0, Ki=0.0, Kd=1.0)
    pid.setTarget(0)

    # Slider
    slider_x = 100
    slider_y = 540
    slider_w = 600
    slider_h = 10
    knob_w = 10
    dragging = False

    font = pygame.font.SysFont(None, 24)

    def draw_slider(val_rad):
        pygame.draw.rect(screen, (180, 180, 180), (slider_x, slider_y, slider_w, slider_h))
        knob_x = slider_x + int((val_rad / (2 * np.pi)) * slider_w) - knob_w // 2
        pygame.draw.rect(screen, (0, 0, 255), (knob_x, slider_y - 5, knob_w, slider_h + 10))

        # Graduations
        graduations = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]
        labels = ["0", "π/2", "π", "3π/2", "2π"]
        for angle, label in zip(graduations, labels):
            gx = slider_x + int((angle / (2 * np.pi)) * slider_w)
            pygame.draw.line(screen, (0, 0, 0), (gx, slider_y + 15), (gx, slider_y + 25), 2)
            text = font.render(label, True, (0, 0, 0))
            screen.blit(text, (gx - 10, slider_y + 30))

    running = True
    elapsed_time = 0.0  # Timer initialisé

    while running:
        screen.fill((250, 250, 250))
        elapsed_time += dt  # Incrément du temps


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if slider_y - 10 <= my <= slider_y + 30 and slider_x <= mx <= slider_x + slider_w:
                    dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

        if dragging:
            mx, _ = pygame.mouse.get_pos()
            mx = max(slider_x, min(mx, slider_x + slider_w))
            angle = (mx - slider_x) / slider_w * 2 * np.pi
            pid.setTarget(angle)

        # Simulation
        pid.simule(dt)

        # Moteur
        moteur.gameDraw(scale, screen)

        # Flèche d’angle
        theta = pid.position
        cx, cy = moteur.p.x * scale, moteur.p.y * scale
        length = 50
        end_x = cx + length * np.cos(theta)
        end_y = cy - length * np.sin(theta)
        pygame.draw.line(screen, (0, 0, 128), (cx, cy), (end_x, end_y), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(cx), int(cy)), 5)

        # Affichage du temps + angle
        time_text = font.render(f"t = {elapsed_time:.2f} s", True, (0, 0, 0))
        angle_text = font.render(f"θ = {theta:.2f} rad", True, (0, 100, 0))
        screen.blit(time_text, (10, 10))
        screen.blit(angle_text, (700, 10))


        # Slider
        draw_slider(pid.target)

        pygame.display.flip()
        clock.tick(1 / dt)

    pygame.quit()
