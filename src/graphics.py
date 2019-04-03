"""
Classes and functions dealing with how the game should be rendered
"""
import pygame
import src.util as util


class PygameColors(type):
    def __getattr__(self, item):
        return pygame.color.THECOLORS.get(item)


class Colors(metaclass=PygameColors):
    pass


class Renderer:

    BACKGROUND_COLOR = Colors.lightgray

    def __init__(self, window_title, screen_size):
        self.draw = pygame.draw
        pygame.display.set_caption(window_title)
        self.window = pygame.display.set_mode(screen_size)
        self.tactics_enabled = True
        self.influence_enabled = False

    def start_frame(self):
        self.window.fill(self.BACKGROUND_COLOR)

    def end_frame(self):
        pygame.display.update()

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.window, color, util.vec_to_ints(start_pos), util.vec_to_ints(end_pos), width)

    def draw_circle(self, color, position, radius, width=0):
        pygame.draw.circle(self.window, color, util.vec_to_ints(position), radius, width)

    def draw_rect(self, color, rect, width=0):
        pygame.draw.rect(self.window, color, rect, width)

    def draw_text(self, color, position, size, text):
        #TODO
        pygame.draw.circle(self.window, color, util.vec_to_ints(position), 1)

