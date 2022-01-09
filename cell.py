import math
import random

import numpy as np
import pygame

from constants import *


class Cell(pygame.sprite.Sprite):
    def __init__(self, game, pos, speed):
        super().__init__()
        self.game = game  # may delete
        self.color = RED

        self.pos = vec(pos)
        self.vel = vec(speed)
        self.radius = radius

        self.mass = 1

    def update(self):
        self.pos += self.vel
        self.check_collide_with_wall()
        # self.check_collide_with_cells(self.other_cells)

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.pos.x, self.pos.y), self.radius)

    def check_collide_with_wall(self):
        width_limit_right = experiment_WIDTH
        width_limit_left = 0
        height_limit_bot = experiment_HEIGHT
        height_limit_top = 0

        if width_limit_right < self.pos.x + self.radius:
            self.pos.x = width_limit_right - self.radius
            self.vel.x = -1 * self.vel.x
        elif self.pos.x - self.radius < width_limit_left:
            self.pos.x = width_limit_left + self.radius
            self.vel.x = -1 * self.vel.x

        if height_limit_bot < self.pos.y + self.radius:
            self.pos.y = height_limit_bot - self.radius
            self.vel.y = -1 * self.vel.y
        elif self.pos.y - self.radius < height_limit_top:
            self.pos.y = height_limit_top + self.radius
            self.vel.y = -1 * self.vel.y

    def get_left(self):
        return vec(self.pos.x - self.radius, self.pos.y)

    def get_right(self):
        return vec(self.pos.x + self.radius, self.pos.y)


def distance(a, b):
    return math.sqrt((a.pos.x - b.pos.x) ** 2 + (a.pos.y - b.pos.y) ** 2)


def find_possible_collisions(particles):
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
