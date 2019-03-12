"""
Class representing a soldier
"""
import pygame
from src.behavior import BehaviorTree


class Soldier(object):

    DEFAULT_RADIUS = 10
    DEFAULT_COLOR = [255, 255, 255]

    MAX_HEALTH = 100
    HEALING_FACTOR = 1.0

    next_id = 1
    behavior_tree = None

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    @classmethod
    def get_behavior(cls):
        if cls.behavior_tree is None:
            cls.behavior_tree = BehaviorTree()
            #TODO
        return cls.behavior_tree

    def __init__(self):
        self.sid = Soldier.get_id()
        self._pos_x = 0
        self._pos_y = 0
        self._radius = Soldier.DEFAULT_RADIUS
        self._color = Soldier.DEFAULT_COLOR

        self.health = Soldier.MAX_HEALTH
        self.behavior_tree = Soldier.get_behavior()

    def update(self, delta):
        # Slow healing over time
        self.heal(Soldier.HEALING_FACTOR * delta)

        self.behavior_tree.run(delta)

    def draw(self, window):
        pygame.draw.circle(window, self._color, [self._pos_x, self._pos_y], self._radius)

    def moveTo(self, new_x, new_y):
        self._pos_x = new_x
        self._pos_y = new_y

    def moveOffset(self, off_x, off_y):
        self._pos_x += off_x
        self._pos_y += off_y

    def heal(self, amount):
        self.health += amount
        if self.health > Soldier.MAX_HEALTH:
            self.health = Soldier.MAX_HEALTH




