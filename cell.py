import math
import random

import numpy as np
import pygame
from pygame import Color

from constants import *
from config import config


def create_random_color(radius):
    """ Creates a color based on the radius of the cell. """
    r = int(255 * radius / 100)
    g = int(255 * (1 - radius / 100))
    b = 0

    return Color(r, g, b)


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, speed, experiment_rect):
        super().__init__()

        self.pos = vec(pos)
        self.vel = vec(speed)
        self.experiment_rect = experiment_rect
        self.radius = random.randint(config.MIN_RADIUS, config.MAX_RADIUS)
        self.mass = self.radius ** 2
        self.color = create_random_color(self.radius)

        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2,
                                self.radius * 2).inflate(10, 10)

    def update(self, dt):
        self.pos += self.vel
        self.rect.center = self.pos
        self.apply_movement()

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.pos.x, self.pos.y), self.radius)

    def apply_movement(self):
        if self.pos.x - self.radius < self.experiment_rect.left:
            self.pos.x = self.experiment_rect.left + self.radius
            self.vel.x = abs(self.vel.x)
        elif self.pos.x + self.radius > self.experiment_rect.right:
            self.pos.x = self.experiment_rect.right - self.radius
            self.vel.x = -abs(self.vel.x)

        if self.pos.y - self.radius < self.experiment_rect.top:
            self.pos.y = self.experiment_rect.top + self.radius
            self.vel.y = abs(self.vel.y)
        elif self.pos.y + self.radius > self.experiment_rect.bottom:
            self.pos.y = self.experiment_rect.bottom - self.radius
            self.vel.y = -abs(self.vel.y)

        # friction
        if self.vel.length() == 0:
            return
        friction_force = self.vel.normalize() * config.FRICTION
        if friction_force.length() > self.vel.length():
            self.vel = vec(0, 0)
        else:
            self.vel -= friction_force

    def get_left(self):
        return vec(self.pos.x - self.radius, self.pos.y)

    def get_right(self):
        return vec(self.pos.x + self.radius, self.pos.y)

    def apply_attraction(self, cells):
        for c in cells:
            if c == self:
                continue
            d = distance(self, c)
            if d < 1000:
                m1 = self.mass * config.ATTRACTION_FORCE / 1000
                m2 = c.mass * config.ATTRACTION_FORCE / 1000
                self.vel += (c.pos - self.pos).normalize() * m2 * m1 / d ** 2

    def apply_gravity(self, gravity):
        self.vel += vec(0, gravity)

    def __repr__(self):
        return f"Cell(pos={self.pos}, vel={self.vel}, radius={self.radius})"


def distance(a, b):
    return math.sqrt((a.pos.x - b.pos.x) ** 2 + (a.pos.y - b.pos.y) ** 2)


def find_possible_collisions(particles) -> set[tuple[Cell, Cell]]:
    axis_list = sorted(particles, key=lambda x: x.get_left()[0])
    active_list = []
    possible_collisions = set()
    for particle in axis_list:
        to_remove = [p for p in active_list if particle.get_left()[0] > p.get_right()[0]]
        for r in to_remove:
            active_list.remove(r)
        for other_particle in active_list:
            possible_collisions.add((particle, other_particle))

        active_list.append(particle)

    return possible_collisions


def get_response_velocities(particle, other_particle):
    # https://en.wikipedia.org/wiki/Elastic_collision
    v1 = particle.vel
    v2 = other_particle.vel
    m1 = particle.mass
    m2 = other_particle.mass
    x1 = particle.pos
    x2 = other_particle.pos

    particle_response_v = compute_velocity(v1, v2, m1, m2, x1, x2)
    other_particle_response_v = compute_velocity(v2, v1, m2, m1, x2, x1)
    return particle_response_v, other_particle_response_v


def compute_velocity(v1, v2, m1, m2, x1, x2):
    return v1 - (2 * m2 / (m1 + m2)) * np.dot(v1 - v2, x1 - x2) / np.linalg.norm(x1 - x2) ** 2 * (x1 - x2)
