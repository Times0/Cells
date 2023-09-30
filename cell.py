import math
import random

import numpy as np
import pygame
from pygame import Color

from constants import *


def create_random_color(mass):
    """ Creates a random color based on the mass of the cell """
    gradient = 255 / 10
    r = int(gradient * mass)
    g = int(gradient * (10 - mass))
    b = 0
    return Color(r, g, b)


class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, speed, radius, experiment_rect):
        super().__init__()

        self.pos = vec(pos)
        self.vel = vec(speed)
        self.experiment_rect = experiment_rect
        self.mass = random.randint(1, 5)
        self.color = create_random_color(self.mass)
        self.radius = int(radius * self.mass / 2)

        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2,
                                self.radius * 2).inflate(10, 10)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        self.check_collide_with_wall()

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.pos.x, self.pos.y), self.radius)
        # pygame.draw.rect(win, Color("white"), self.rect, 1)

    def check_collide_with_wall(self):
        if self.pos.x - self.radius < self.experiment_rect.left:
            self.pos.x = self.experiment_rect.left + self.radius
            self.vel.x *= -1
        elif self.pos.x + self.radius > self.experiment_rect.right:
            self.pos.x = self.experiment_rect.right - self.radius
            self.vel.x *= -1

        if self.pos.y - self.radius < self.experiment_rect.top:
            self.pos.y = self.experiment_rect.top + self.radius
            self.vel.y *= -1
        elif self.pos.y + self.radius > self.experiment_rect.bottom:
            self.pos.y = self.experiment_rect.bottom - self.radius
            self.vel.y *= -1

    def get_left(self):
        return vec(self.pos.x - self.radius, self.pos.y)

    def get_right(self):
        return vec(self.pos.x + self.radius, self.pos.y)

    def attraction(self, cells):
        for c in cells:
            if c != self:
                d = distance(self, c)
                if d < 500:
                    m1 = self.mass * 100
                    m2 = c.mass * 100
                    self.vel += (c.pos - self.pos).normalize() * m2 / d ** 2
                    c.vel += (self.pos - c.pos).normalize() * m1 / d ** 2


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
    f = 0.9

    particle_response_v = compute_velocity(v1, v2, m1, m2, x1, x2)
    other_particle_response_v = compute_velocity(v2, v1, m2, m1, x2, x1)
    return particle_response_v * f, other_particle_response_v * f


def compute_velocity(v1, v2, m1, m2, x1, x2):
    return v1 - (2 * m2 / (m1 + m2)) * np.dot(v1 - v2, x1 - x2) / np.linalg.norm(x1 - x2) ** 2 * (x1 - x2)
