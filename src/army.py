"""
Class representing an army made up of formations of soldiers
"""

from pygame import Vector2
from src.location import Location


class Army:

    next_id = 1

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self, color):
        self.my_id = Army.get_id()
        self.color = color
        self.anchor = Location()
        self.waypoint = Vector2()
        self.formations = []

    def set_waypoint(self, xpos, ypos):
        self.waypoint.x = xpos
        self.waypoint.y = ypos



