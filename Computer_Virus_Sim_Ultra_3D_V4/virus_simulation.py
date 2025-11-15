# virus_simulation.py
import random
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from network import create_network
from graphics_init import initialize_pygame_opengl
import time

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

class Camera:
    def __init__(self, distance=30):
        self.angle_x = 30
        self.angle_y = 0
        self.distance = distance
        self.mouse_sensitivity = 0.3
        self.zoom_speed = 1.0
        self.last_mouse_pos = None

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [1, 2, 3]:  # Left, middle, right click
                self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 4:  # Scroll up
                self.distance -= self.zoom_speed
                if self.distance < 5:
                    self.distance = 5
            elif event.button == 5:  # Scroll down
                self.distance += self.zoom_speed

        elif event.type == MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left button held -> rotate
                x, y = pygame.mouse.get_pos()
                dx = x - self.last_mouse_pos[0]
                dy = y - self.last_mouse_pos[1]
                self.angle_y += dx * self.mouse_sensitivity
                self.angle_x += dy * self.mouse_sensitivity
                self.angle_x = max(-90, min(90, self.angle_x))
                self.last_mouse_pos = (x, y)

    def apply(self):
        glLoadIdentity()
        ax = math.radians(self.angle_x)
        ay = math.radians(self.angle_y)
        x = self.distance * math.cos(ax) * math.sin(ay)
        y = self.distance * math.sin(ax)
        z = self.distance * math.cos(ax) * math.cos(ay)
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

class VirusSimulation3D:
    def __init__(self, network, defense_nodes=None, defense_strength=0.95, initial_infected=None):
        self.network = network
        self.defense_nodes = defense_nodes or set()
        self.defense_strength = defense_strength
        self.infected = set(initial_infected or [0])
        self.newly_infected = set(initial_infected or [0])
        self.time_step = 0
        self.node_positions = self.generate_node_positions()
        self.last_update_time = time.time()

        self.strains = {}
        for node in self.infected:
            self.strains[node] = 0

        self.text_texture_cache = {}

    def generate_node_positions(self):
        positions = {}
        for node in self.network:
            positions[node] = (
                random.uniform(-10, 10),
                random.uniform(-10, 10),
                random.uniform(-10, 10),
            )
        return positions

    def update(self):
        mutation_chance = 0.1  # 10% chance to mutate to a new strain
        max_strain_id = 4  # Assuming 5 strain colors: 0-4

        current_new_infections = set()
        for node in self.newly_infected:
            parent_strain = self.strains.get(node, 0)
            for neighbor in self.network[node]:
                if neighbor not in self.infected:
                    if neighbor in self.defense_nodes:
                        if random.random() > self.defense_strength:
                            # Decide mutation or not
                            if random.random() < mutation_chance:
                                new_strain = (parent_strain + 1) % (max_strain_id + 1)
                                self.strains[neighbor] = new_strain
                            else:
                                self.strains[neighbor] = parent_strain
                            current_new_infections.add(neighbor)
                    else:
                        # Decide mutation or not
                        if random.random() < mutation_chance:
                            new_strain = (parent_strain + 1) % (max_strain_id + 1)
                            self.strains[neighbor] = new_strain
                        else:
                            self.strains[neighbor] = parent_strain
                        current_new_infections.add(neighbor)

        self.newly_infected = current_new_infections
        self.infected.update(self.newly_infected)
        self.time_step += 1



    def draw_cube(self, size=0.3):
        half = size / 2
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-half, -half,  half)
        glVertex3f( half, -half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f(-half,  half,  half)
        # Back face
        glVertex3f(-half, -half, -half)
        glVertex3f(-half,  half, -half)
        glVertex3f( half,  half, -half)
        glVertex3f( half, -half, -half)
        # Left face
        glVertex3f(-half, -half, -half)
        glVertex3f(-half, -half,  half)
        glVertex3f(-half,  half,  half)
        glVertex3f(-half,  half, -half)
        # Right face
        glVertex3f(half, -half, -half)
        glVertex3f(half,  half, -half)
        glVertex3f(half,  half,  half)
        glVertex3f(half, -half,  half)
        # Top face
        glVertex3f(-half,  half, -half)
        glVertex3f(-half,  half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f( half,  half, -half)
        # Bottom face
        glVertex3f(-half, -half, -half)
        glVertex3f( half, -half, -half)
        glVertex3f( half, -half,  half)
        glVertex3f(-half, -half,  half)
        glEnd()

    def draw_node(self, node):
        x, y, z = self.node_positions[node]
        glPushMatrix()
        glTranslatef(x, y, z)
        if node in self.infected:
            strain_colors = {
                0: (1.0, 0.0, 0.0),   # Red
                1: (1.0, 0.5, 0.0),   # Orange
                2: (0.5, 0.0, 0.5),   # Purple
                3: (1.0, 1.0, 0.0),   # Yellow
                4: (0.0, 1.0, 1.0),   # Cyan
            }
            strain_id = self.strains.get(node, 0)
            color = strain_colors.get(strain_id, (1.0, 0.0, 0.0))
            glColor3f(*color)
        elif node in self.defense_nodes:
            glColor3f(0.0, 0.0, 1.0)  # Blue
        else:
            glColor3f(0.0, 1.0, 0.0)  # Green
        self.draw_cube()
        glPopMatrix()

    def draw_edges(self):
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        for node, neighbors in self.network.items():
            x1, y1, z1 = self.node_positions[node]
            for neighbor in neighbors:
                x2, y2, z2 = self.node_positions[neighbor]
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)
        glEnd()

    def render_text_texture(self, text, font):
        if text in self.text_texture_cache:
            return self.text_texture_cache[text]

        text_surface = font.render(text, True, (255, 255, 255, 255))
        text_surface = pygame.transform.flip(text_surface, False, True)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        self.text_texture_cache[text] = (texture_id, width, height)
        return texture_id, width, height

    def draw_text(self, text, x, y, font):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)

        texture_id, width, height = self.render_text_texture(text, font)

        glBindTexture(GL_TEXTURE_2D, texture_id)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0); glVertex2f(x, y + height)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)

    def run(self):
        initialize_pygame_opengl(WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 20)
        clock = pygame.time.Clock()
        running = True

        camera = Camera(distance=30)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    camera.handle_event(event)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Apply manual camera control
            camera.apply()

            self.draw_edges()
            for node in self.network:
                self.draw_node(node)

            infected_strains = set()
            for node in self.infected:
                if node in self.strains:
                    infected_strains.add(self.strains[node])
            num_strains = len(infected_strains)

            infected_count = len(self.infected)
            healthy_count = len(self.network) - infected_count - len(self.defense_nodes.intersection(self.infected))
            defended_count = len(self.defense_nodes) - len(self.defense_nodes.intersection(self.infected))

            stats_lines = [
                f"Time Step: {self.time_step}",
                f"Infected (Red): {infected_count}",
                f"Defended (Blue) (healthy): {defended_count}",
                f"Healthy (Green) (undefended): {healthy_count}",
                f"Total Nodes: {len(self.network)}",
                f"Total Strains: {num_strains}",
            ]

            y_pos = 10
            for line in stats_lines:
                self.draw_text(line, 10, y_pos, font)
                y_pos += 25

            pygame.display.flip()
            clock.tick(60)

            now = time.time()
            if now - self.last_update_time > 2:
                if self.newly_infected:
                    self.update()
                self.last_update_time = now

        pygame.quit()

if __name__ == "__main__":
    network = create_network(num_nodes=1000, connection_prob=0.01)
    defense_nodes = {
        2, 4, 6, 9, 11, 13, 15, 18, 20, 22, 25, 27, 29,
        32, 34, 36, 39, 41, 43, 46, 48, 50, 53, 55, 57,
        60, 62, 64, 67, 69, 71, 74, 76, 78, 81, 83, 85,
        88, 90, 92, 95, 97, 99, 100
    }
    defense_strength = 1.00

    sim = VirusSimulation3D(
        network=network,
        defense_nodes=defense_nodes,
        defense_strength=defense_strength,
        initial_infected=[0],
    )
    sim.run()
