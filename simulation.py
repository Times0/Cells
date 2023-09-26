import random

import numpy as np
import pygame.sprite
from pygame import Color

from constants import *
import cell

from PygameUIKit import Group, button

CELL_RADIUS = 10
CELL_SPEED = 10

default_font = pygame.font.SysFont("None", 30)


class Simulation:
    def __init__(self, win):  # Here I put parameters related to when you generate the game, for example the map
        self.game_is_on = True
        self.win = win

        self.experiment_rect = self.win.get_rect().inflate(-300, -50)

        self.dt = 0

        self.cells = pygame.sprite.Group()

        # Ui
        self.buttons = Group()
        self.btn_add_cells = button.ButtonText("Add cells", lambda: self.add_cells(10), Color("green"),
                                               border_radius=5, font=default_font, ui_group=self.buttons)
        self.btn_clear = button.ButtonText("Clear", self.clear_experiment, Color("red"), border_radius=5,
                                           font=default_font,
                                           ui_group=self.buttons)

        self.fps = 0

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS) / 1000
            self.fps = clock.get_fps()
            self.check_events()
            self.update_all(dt)
            self.draw_all()

    def check_events(self):
        events = pygame.event.get()
        for event in events:
            self.buttons.handle_event(event)
            if event.type == pygame.QUIT:
                self.game_is_on = False

    def create_cells(self, n):
        return [cell.Cell((random.randint(self.experiment_rect.left, self.experiment_rect.right),
                           random.randint(self.experiment_rect.top, self.experiment_rect.bottom)),
                          speed=random_speed(CELL_SPEED),
                          radius=CELL_RADIUS,
                          experiment_rect=self.experiment_rect)
                for _ in range(n)]

    def update_all(self, dt):
        for c in self.cells:
            c.update()
        self.check_cells_collisions2()

    def draw_all(self):
        self.win.fill(Color("black"))
        pygame.draw.rect(self.win, Color("White"), self.experiment_rect, 1)
        for cell in self.cells:
            cell.draw(self.win)

        # ui
        self.btn_add_cells.draw(self.win, 10, HEIGHT // 2 - self.btn_add_cells.rect.height // 2 - 50)
        self.btn_clear.draw(self.win, 10, HEIGHT // 2 - self.btn_clear.rect.height // 2 + 50)

        # fps
        text = default_font.render(f"FPS: {self.fps:.2f}", True, Color("red"))
        self.win.blit(text, text.get_rect(bottomright=self.win.get_rect().bottomright).move(-10, -10))
        pygame.display.flip()

    def add_cells(self, n):
        self.cells.add(self.create_cells(n))

    def clear_experiment(self):
        self.cells.empty()

    def check_cells_collisions1(self):
        for a in self.cells:
            for b in self.cells:
                if 0 < cell.distance(a, b) < a.radius + b.radius:
                    a.color = Color("green")

    def check_cells_collisions2(self):
        """sweep and prune algorithm (way faster)"""
        L = cell.find_possible_collisions(self.cells)
        for a, b in L:
            if 0 < cell.distance(a, b) < a.radius + b.radius:
                v1, v2 = cell.get_response_velocities(a, b)
                a.vel = v1
                b.vel = v2

                direction = (a.pos - b.pos).normalize()
                a.pos = b.pos + direction * (a.radius + b.radius)
                b.pos = a.pos - direction * (a.radius + b.radius)

    def check_cells_collisions3(self):
        pass


def random_speed(norm):
    """calculates the x and y coordinates of a x,y vel in a random direction"""
    theta = random.randint(1, 360)
    return np.cos(theta) * norm, np.sin(theta) * norm
