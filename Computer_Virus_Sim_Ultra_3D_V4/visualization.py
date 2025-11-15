import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import colorsys

def initialize_opengl():
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)


# Extend strain colors here for multiple strains:
def strain_id_to_color(strain_id):
    # Map strain_id to hue [0,1) by modulo to cycle colors
    hue = (strain_id * 0.618033988749895) % 1.0  # Golden ratio to distribute hues well
    saturation = 0.8
    value = 0.9
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (r, g, b)

class Camera:
    def __init__(self, distance=40):
        self.angle_x = 30
        self.angle_y = 0
        self.distance = distance
        self.mouse_sensitivity = 2.0
        self.zoom_speed = 2.0
        self.last_mouse_pos = None

    def handle_mouse(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.last_mouse_pos = pygame.mouse.get_pos()

        elif event.type == MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            self.angle_y += dx * self.mouse_sensitivity
            self.angle_x += dy * self.mouse_sensitivity
            self.angle_x = max(-90, min(90, self.angle_x))
            self.last_mouse_pos = (x, y)

        elif event.type == MOUSEWHEEL:
            # event.y is positive when scrolling up, negative when scrolling down
            self.distance -= event.y * self.zoom_speed
            if self.distance < 5:
                self.distance = 5

    def apply(self):
        glLoadIdentity()
        # Convert angles to radians
        ax = math.radians(self.angle_x)
        ay = math.radians(self.angle_y)
        # Calculate camera position
        x = self.distance * math.cos(ax) * math.sin(ay)
        y = self.distance * math.sin(ax)
        z = self.distance * math.cos(ax) * math.cos(ay)
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)


def draw_network(network, positions, states, strains, strain_colors, defense_nodes):
    """
    Draw nodes and edges with colors reflecting infection state & strain.
    """
    # Draw edges
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    color = strain_id_to_color(strain_id)
    glColor3f(*color)
    for node, neighbors in network.items():
        x1, y1, z1 = positions[node]
        for neighbor in neighbors:
            x2, y2, z2 = positions[neighbor]
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
    glEnd()

    # Draw nodes
    for node in network:
        x, y, z = positions[node]
        glPushMatrix()
        glTranslatef(x, y, z)

        state = states[node]
        if state == 0:  # Healthy
            if node in defense_nodes:
                glColor3f(0.0, 0.0, 1.0)  # Blue for defense
            else:
                glColor3f(0.0, 1.0, 0.0)  # Green healthy
        elif state == 1:  # Infected
            strain_id = strains[node]
            color = strain_colors.get(strain_id, (1.0, 0.0, 0.0))
            glColor3f(*color)
        elif state == 2:  # Recovered
            glColor3f(1.0, 1.0, 0.0)  # Yellow recovered
        else:
            glColor3f(0.5, 0.5, 0.5)  # Grey other states

        glPopMatrix()
