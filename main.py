from constants import *
from simulation import Simulation
import ctypes

# make the window dpi aware
ctypes.windll.user32.SetProcessDPIAware()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Cell simulation")
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN| pygame.HWSURFACE| pygame.DOUBLEBUF)
    game = Simulation(win)
    game.run()
