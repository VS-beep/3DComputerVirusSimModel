# graphics_init.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def initialize_pygame_opengl(width, height):
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Computer Virus Simulation Ultra 3D V4")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (width / height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_text(screen, text, pos, font, color=(255, 255, 255)):
    """
    Draw 2D text overlay using Pygame.
    - screen: Pygame display surface
    - text: string
    - pos: (x, y) tuple for top-left position
    - font: pygame.font.Font object
    - color: text color tuple
    """
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)
