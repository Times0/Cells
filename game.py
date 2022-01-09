import random
import time

import numpy as np
import pygame.sprite
from constants import *
from button import Button
import cell


class Game:
    def __init__(self, win):  # Here I put parameters related to when you generate the game, for example the map
        self.game_is_on = True
        self.win = win

        self.buttons = []
        self.load_buttons()

        self.experiment_rect = pygame.rect.Rect(WIDTH * 1 / 10, HEIGHT * 1 / 10, experiment_WIDTH, experiment_HEIGHT)
        self.experiment_surface = pygame.surface.Surface(self.experiment_rect.size)

        self.dt = 0

        self.all_sprites = pygame.sprite.Group()
        self.cells = []

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS) / 1000
            # print(clock.get_fps())
            self.check_events()
            self.update_all(dt)
            self.draw_all()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if you push the red cross, it close the game
                self.game_is_on = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.buttons:
                    if btn.isMouseOn(event.pos):
                        btn.onclick()

    def create_cells(self, n):
        return [cell.Cell(self, (random.randint(self.experiment_rect.left, self.experiment_rect.right),
                                 random.randint(self.experiment_rect.top, self.experiment_rect.bottom)),
                          speed=random_speed(speed)) for _ in range(n)]

    def update_all(self, dt):
        for elem in self.all_sprites:
            elem.update()
        self.check_cells_collisions2()

    def draw_all(self):
        self.win.fill(BLACK)
        for btn in self.buttons:
            btn.draw(self.win)
        # exp surface
        self.experiment_surface.fill(BLACK)
        for elem in self.all_sprites:
            elem.draw(self.experiment_surface)
        self.win.blit(self.experiment_surface, self.experiment_rect.topleft)
        pygame.draw.rect(self.win, WHITE, self.experiment_rect, 1)

        pygame.display.flip()

    def load_buttons(self):
        start_experiment_button = Button(GREEN, GRAY, 10, 10, 210, 50, self.start_experiment, f"Add {n_cells} cells",
                                         WHITE)
        clear_experiment_button = Button(RED, GRAY, 10, 90, 100, 50, self.clear_experiment, "Clear", WHITE)
        self.buttons.extend([start_experiment_button, clear_experiment_button])

    def start_experiment(self, n=n_cells):
        self.cells.extend(self.create_cells(n))
        self.all_sprites.add(*self.cells)

    def clear_experiment(self):
        for c in self.all_sprites:
            if isinstance(c, cell.Cell):
                c.kill()
        self.cells = []

    def check_cells_collisions1(self):
        for a in self.cells:
            for b in self.cells:
                if 0 < cell.distance(a, b) < a.radius + b.radius:
                    a.color = GREEN

    def check_cells_collisions2(self):
        """sweep and prune algorithm (way faster)"""
        L = cell.find_possible_collisions(self.cells)
        for a, b in L:
            if 0 < cell.distance(a, b) < a.radius + b.radius:
                v1, v2 = cell.get_response_velocities(a, b)
                a.vel = v1
                b.vel = v2

    def check_cells_collisions3(self):
        pass


def random_speed(norm):
    """calculates the x and y coordinates of a x,y vel in a random direction"""
    theta = random.randint(1, 360)
    return np.cos(theta) * norm, np.sin(theta) * norm
