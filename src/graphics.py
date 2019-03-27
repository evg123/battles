"""
Classes and functions dealing with how the game should be rendered
"""
import pygame


class Renderer:

    BACKGROUND_COLOR = (220, 220, 220)

    def __init__(self, window_title, screen_size):
        self.draw = pygame.draw
        pygame.display.set_caption(window_title)
        self.window = pygame.display.set_mode(screen_size)
        self.tactics_enabled = False
        self.influence_enabled = False

    def start_frame(self):
        self.window.fill(self.BACKGROUND_COLOR)

    def end_frame(self):
        pygame.display.update()

    def draw_line(self, color, start_pos, end_pos, width):
        pygame.draw.line(self.window, color, start_pos, end_pos, width)

    def draw_circle(self, color, position, radius, width):
        pygame.draw.circle(self.window, color, position, radius, width)

    def draw_text(self, color, position, size, text):
        #TODO
        pygame.draw.circle(self.window, color, position, 1)


class PygameColors(type):
    def __getattr__(self, item):
        return pygame.color.THECOLORS.get(item)


class Colors(metaclass=PygameColors):
    pass

