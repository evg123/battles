"""
Class representing an army made up of formations of soldiers
"""

from pygame import Vector2


class Army:

    next_id = 1

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self):
        self.my_id = Army.get_id()
        self.soldiers = []
        self.waypoint = Vector2()

    def set_waypoint(self, xpos, ypos):
        self.waypoint.x = xpos
        self.waypoint.y = ypos

    def add_soldier(self, soldier):
        soldier.army_id = self.my_id
        self.soldiers.append(soldier)
