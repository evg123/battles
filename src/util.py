"""
Various utility classes
"""
import pygame
import math


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def normalize_rotation(rotation):
    if rotation > 180:
        return rotation - 360
    if rotation <= -180:
        return rotation + 360
    return rotation


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
        # Tick will limit framerate and return delta in millis
        delta = self.clock.tick(self.framerate)

        # Convert delta to seconds
        delta /= 1000.0

        # Limit worst-case delta to make debugging easier
        delta = min(delta, FrameTimer.MAX_FRAME_TIME)

        return delta
