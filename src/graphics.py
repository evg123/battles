"""
Classes and functions dealing with how the game should be rendered
"""
import pygame
import src.util as util


class PygameColors(type):
    """Metaclass to enable the Colors class"""
    def __getattr__(cls, item):
        return pygame.color.THECOLORS.get(item)


class Colors(metaclass=PygameColors):
    """Helper for accessing the built-in pygame colors"""
    pass


class Renderer:
    """A class to handle drawing to the screen
    Mostly just wraps pygame functions
    """
    BACKGROUND_COLOR = Colors.lightgray

    def __init__(self, window_title, screen_size):
        self.draw = pygame.draw
        pygame.display.set_caption(window_title)
        self.window = pygame.display.set_mode(screen_size)
        self.tactics_enabled = True
        self.influence_enabled = True

    def start_frame(self):
        self.window.fill(self.BACKGROUND_COLOR)

    def end_frame(self):
        pygame.display.update()

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.window, color, util.vec_to_ints(start_pos), util.vec_to_ints(end_pos), width)

    def draw_circle(self, color, position, radius, width=0):
        pygame.draw.circle(self.window, color, util.vec_to_ints(position), radius, width)

    def draw_arc(self, color, rect, start_angle, stop_angle, width=0):
        pygame.draw.arc(self.window, color, rect, start_angle, stop_angle, width)

    def draw_rect(self, color, rect, width=0):
        pygame.draw.rect(self.window, color, rect, width)

    def draw_transparent_rect(self, color, rect, alpha):
        surf = ResourceManager.get_rect_surf((rect.width, rect.height), color, alpha)
        self.window.blit(surf, rect.topleft)

    def draw_text(self, color, position, size, text):
        surf = ResourceManager.get_text_surface(text, color, size)
        top_left = position[0] - surf.get_width() / 2, position[1] - surf.get_height() / 2
        self.window.blit(surf, top_left)

    def draw_x(self, color, position, radius, width=1):
        pos = util.vec_to_ints(position)
        top_left = pos[0] - radius, pos[1] - radius
        bottom_left = pos[0] - radius, pos[1] + radius
        top_right = pos[0] + radius, pos[1] - radius
        bottom_right = pos[0] + radius, pos[1] + radius
        pygame.draw.line(self.window, color, top_left, bottom_right, width)
        pygame.draw.line(self.window, color, top_right, bottom_left, width)


class ResourceManager:
    """Holds and caches already loaded resources"""
    fonts = {}
    text_surfs = {}
    rect_surfs = {}

    @classmethod
    def get_font(cls, size):
        """Get or create a font object of the given size"""
        key = size
        val = cls.fonts.get(key, None)
        if val is not None:
            return val
        font = pygame.font.Font(pygame.font.get_default_font(), size)
        cls.fonts[key] = font
        return font

    @classmethod
    def get_text_surface(cls, text, color, size):
        """Get or create a surface of the rendered text"""
        key = (text, color, size)
        val = cls.text_surfs.get(key, None)
        if val is not None:
            return val
        font = ResourceManager.get_font(size)
        surf = font.render(text, True, color)
        cls.text_surfs[key] = surf
        return surf

    @classmethod
    def get_rect_surf(cls, size, color, alpha):
        """Get or create a surface of the given size and color.
        Translucency is determined by alpha.
        """
        key = (size, color, alpha)
        val = cls.fonts.get(key, None)
        if val is not None:
            return val
        surf = pygame.Surface(size)
        surf.set_alpha(alpha)
        surf.fill(color)
        cls.rect_surfs[key] = surf
        return surf
