"""
Various utility classes
"""
import pygame


class FrameTimer(object):
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
