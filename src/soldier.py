"""
Class representing a soldier
"""
import pygame


class Soldier(object):

    DEFAULT_RADIUS = 10
    DEFAULT_COLOR = [255, 255, 255]

    def __init__(self):
        self._pos_x = 0
        self._pos_y = 0
        self._radius = Soldier.DEFAULT_RADIUS
        self._color = Soldier.DEFAULT_COLOR

    def update(self, delta):
        pass

    def draw(self, window):
        pygame.draw.circle(window, self._color, [self._pos_x, self._pos_y], self._radius)

    def moveTo(self, new_x, new_y):
        self._pos_x = new_x
        self._pos_y = new_y

    def moveOffset(self, off_x, off_y):
        self._pos_x += off_x
        self._pos_y += off_y
