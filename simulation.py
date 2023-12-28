import random

import numpy as np
import pygame.sprite
from PygameUIKit.button import TextAlignment
from PygameUIKit.combobox import ComboBox
from pygame import Color

from constants import *
import cell
from config import config

from PygameUIKit import Group, button, slider

CELL_START_SPEED = 5

default_font = pygame.font.SysFont(None, 30)

UI = True


class Simulation:
    def __init__(self, win):
        self.game_is_on = True
        self.win = win
        self.experiment_rect = self.win.get_rect().inflate(-300, -100).move(100, 0)
        self.dt = 0
        self.cells = pygame.sprite.Group()
        self.set_cells_to_nb(config.NB_CELLS)

        # Ui
        self.ui_group = Group()
        self.algo = ComboBox(["Naive O(n²)", "Sort and sweep", "KD-Tree"], ui_group=self.ui_group)
        self.algo.add_action(0, lambda: setattr(self, "check_collisions", self.naive))
        self.algo.add_action(1, lambda: setattr(self, "check_collisions", self.sweepandprune))
        self.algo.add_action(2, lambda: setattr(self, "check_collisions", self.kdtree))

        self.nb_cell_slider = slider.Slider(0, 1000, 1, show_value=True, ui_group=self.ui_group,
                                            font_color=Color("white"))
        self.nb_cell_slider.current_value = config.NB_CELLS
        self.nb_cell_slider.connect(lambda: self.set_cells_to_nb(self.nb_cell_slider.current_value))
        self.attraction_slider = slider.Slider(0, 100, 1, show_value=True, ui_group=self.ui_group,
                                               font_color=Color("white"))
        self.attraction_slider.current_value = config.ATTRACTION_FORCE
        self.attraction_slider.connect(
            lambda: setattr(config, "ATTRACTION_FORCE", self.attraction_slider.current_value))
        self.friction_slider = slider.Slider(0, 1, 0.01, show_value=True, ui_group=self.ui_group,
                                             font_color=Color("white"))
        self.friction_slider.current_value = config.FRICTION
        self.friction_slider.connect(lambda: setattr(config, "FRICTION", self.friction_slider.current_value))

        self.min_radius_slider = slider.Slider(0, 100, 1, show_value=True, ui_group=self.ui_group,
                                               font_color=Color("white"))
        self.min_radius_slider.current_value = config.MIN_RADIUS
        self.min_radius_slider.connect(lambda: setattr(config, "MIN_RADIUS", self.min_radius_slider.current_value))

        self.max_radius_slider = slider.Slider(0, 100, 1, show_value=True, ui_group=self.ui_group,
                                               font_color=Color("white"))
        self.max_radius_slider.current_value = config.MAX_RADIUS
        self.max_radius_slider.connect(lambda: setattr(config, "MAX_RADIUS", self.max_radius_slider.current_value))

        self.btn_clear = button.ButtonText("Clear", self.clear_experiment, Color(91, 44, 44), border_radius=5,
                                           ui_group=self.ui_group, fixed_width=200, text_align=TextAlignment.CENTER)

        self.check_collisions = self.naive

        self.fps = 0

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(config.TARGET_FPS) / 1000
            self.fps = clock.get_fps()
            self.check_events()
            self.update_all(dt)
            self.draw_all()

    def check_events(self):
        events = pygame.event.get()
        for event in events:
            self.ui_group.handle_event(event)
            if event.type == pygame.QUIT:
                self.game_is_on = False

    def create_cells(self, n):
        return [cell.Cell(pos=(random.randint(self.experiment_rect.left, self.experiment_rect.right),
                               random.randint(self.experiment_rect.top, self.experiment_rect.bottom)),
                          speed=random_speed(CELL_START_SPEED),
                          experiment_rect=self.experiment_rect)
                for _ in range(n)]

    def update_all(self, dt):
        for c in self.cells:
            c.update(dt)
            if config.ATTRACTION_FORCE > 0:
                c.attraction(self.cells)

        self.check_collisions()

    def draw_all(self):
        self.win.fill(Color((28, 28, 38)))
        pygame.draw.rect(self.win, Color("White"), self.experiment_rect, 1, border_radius=15)
        for cell in self.cells:
            cell.draw(self.win)

        # ui
        if UI:
            self.draw_ui(self.win)

        # fps
        text = default_font.render(f"FPS: {self.fps:.2f}", True, Color("red"))
        self.win.blit(text, text.get_rect(bottomright=self.win.get_rect().bottomright).move(-10, -10))
        pygame.display.flip()

    def draw_ui(self, win):
        nb_cell_label = default_font.render("Number of Cells", True, (255, 255, 255))
        win.blit(nb_cell_label, (10, 370))
        self.nb_cell_slider.draw(win, 10, 400, 200, 5)

        force_label = default_font.render("Attraction Strength", True, (255, 255, 255))
        win.blit(force_label, (10, 470))
        self.attraction_slider.draw(win, 10, 500, 200, 5)

        friction_label = default_font.render("Friction", True, (255, 255, 255))
        win.blit(friction_label, (10, 570))
        self.friction_slider.draw(win, 10, 600, 200, 5)

        min_radius_label = default_font.render("Min Radius", True, (255, 255, 255))
        win.blit(min_radius_label, (10, 670))
        self.min_radius_slider.draw(win, 10, 700, 200, 5)

        max_radius_label = default_font.render("Max Radius", True, (255, 255, 255))
        win.blit(max_radius_label, (10, 770))
        self.max_radius_slider.draw(win, 10, 800, 200, 5)

        self.btn_clear.draw(win, 10, HEIGHT // 2 - self.btn_clear.rect.height // 2 + 500)
        self.algo.draw(win, 10, 300)

    def set_cells_to_nb(self, n):
        config.NB_CELLS = n
        if n < len(self.cells):
            self.cells.remove(self.cells.sprites()[:len(self.cells) - n])
        elif n > len(self.cells):
            self.cells.add(self.create_cells(n - len(self.cells)))

    def clear_experiment(self):
        self.cells.empty()
        self.nb_cell_slider.current_value = 0

    # __________Check for collisions between cells with different algorithms __________#

    def naive(self):
        for a in self.cells:
            for b in self.cells:
                if 0 < cell.distance(a, b) < a.radius + b.radius:
                    v1, v2 = cell.get_response_velocities(a, b)
                    a.vel = v1
                    b.vel = v2

                    direction = (a.pos - b.pos).normalize()
                    a.pos = b.pos + direction * (a.radius + b.radius)
                    b.pos = a.pos - direction * (a.radius + b.radius)

    def sweepandprune(self):
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

    def kdtree(self):
        tree = KDTree(self.cells)
        for a in self.cells:
            b = tree.get_nearest(a)
            if 0 < cell.distance(a, b) < a.radius + b.radius:
                v1, v2 = cell.get_response_velocities(a, b)
                a.vel = v1
                b.vel = v2
                direction = (a.pos - b.pos).normalize()
                a.pos = b.pos + direction * (a.radius + b.radius)
                b.pos = a.pos - direction * (a.radius + b.radius)


class KDTree:
    """https://fr.wikipedia.org/wiki/Arbre_kd"""

    def __init__(self, points, depth=0):
        self.axis = depth % 2
        self.points = list(points)
        self.left = None
        self.right = None
        self.split = None

        self.build()

    def build(self):
        if len(self.points) == 0:
            return
        self.points.sort(key=lambda x: x.pos[self.axis])
        median = len(self.points) // 2
        self.split = self.points[median]
        self.left = KDTree(self.points[:median], self.axis + 1)
        self.right = KDTree(self.points[median + 1:], self.axis + 1)

    def query(self, point):
        """returns the list of points that are in the same cell as the given point"""
        if self.split is None:
            return []
        if point.pos[self.axis] < self.split.pos[self.axis]:
            return self.left.query(point)
        else:
            return self.right.query(point)

    def get_nearest(self, point):
        """returns the nearest point to the given point. The answer is not the point itself."""
        if self.split is None:
            return None
        if point.pos[self.axis] < self.split.pos[self.axis]:
            nearest = self.left.get_nearest(point)
        else:
            nearest = self.right.get_nearest(point)

        if nearest is None:
            return self.split

        d = cell.distance(point, nearest)
        if d == 0:
            return self.split

        if d < cell.distance(point, self.split):
            return nearest
        else:
            return self.split


def random_speed(norm):
    """calculates the x and y coordinates of a x,y vel in a random direction"""
    theta = random.randint(1, 360)
    return np.cos(theta) * norm, np.sin(theta) * norm
