import platform
from colors import *
import pygame.math
from screeninfo import get_monitors

WIDTH, HEIGHT = 1920, 1080
ratio = 4/7  # corresponds to the place I want my window to take. For example, 1 will be fullscreen.

WIDTH, HEIGHT = int(WIDTH * ratio), int(HEIGHT * ratio)
experiment_WIDTH = WIDTH * 4 / 5
experiment_HEIGHT = HEIGHT * 4 / 5

vec = pygame.math.Vector2

# game

FPS = 60
n_cells = 10
radius = 5
speed = 4
