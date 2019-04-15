"""
Various utility classes
"""
import pygame
import math


def distance(x1, y1, x2, y2):
    """Simple distance formula"""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def normalize_rotation(rotation):
    """Convert rotation degrees so that it is from -PI to PI"""
    if rotation > 180:
        return rotation - 360
    if rotation <= -180:
        return rotation + 360
    return rotation


def vec_to_ints(vec):
    """Convert a pygame Vector2 to a tuple of ints
    Also coverts float tuples to int tuples
    """
    try:
        return int(vec.x), int(vec.y)
    except AttributeError:
        return int(vec[0]), int(vec[1])


class FrameTimer:
    """
    Keeps track of and controls frame rate
    """
    DEFAULT_FRAMERATE = 60
    MAX_FRAME_TIME = 1.0 / 10

    def __init__(self):
        self.framerate = FrameTimer.DEFAULT_FRAMERATE
        self.clock = pygame.time.Clock()

    def next_frame(self):
        """Call once per frame to limit fps and compute delta"""
        # Tick will limit framerate and return delta in millis
        delta = self.clock.tick(self.framerate)

        # Convert delta to seconds
        delta /= 1000.0

        # Limit worst-case delta to make debugging easier
        delta = min(delta, FrameTimer.MAX_FRAME_TIME)

        return delta

    def print_fps(self):
        print(self.clock.get_fps())
