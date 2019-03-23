"""
Classes representing weapons like a sword or bow
"""

import pygame
from pygame import Vector2


class Weapon:
    """Abstract base class"""

    def __init__(self):
        # Position of the weapon wielder
        self.pos = Vector2()

        # Angle relative to wielder
        self.angle = 0

        self.damage = 0

    def update(self, delta):
        pass

    def draw(self, window):
        raise NotImplementedError()

    def update_wielder_pos(self, pos):
        self.pos.x = pos.x
        self.pos.y = pos.y

    def activate(self):
        pass

    def deactivate(self):
        pass

    def hits_circle(self, other_pos, other_radius):
        raise NotImplementedError()


class Sword(Weapon):

    INACTIVE = -1.0
    START = 0.0
    FINISHED = 0.75

    START_DIST_OFFSET = 0
    FINAL_DIST_OFFSET = 10
    START_ANGLE_OFFSET = 0
    COLOR = (128, 128, 128)

    def __init__(self):
        super(Sword, self).__init__()
        self.pos_speed = 600
        self.angle_speed = 500
        self.damage = 30
        self.swing_time = Sword.INACTIVE
        self.length = 20
        self.width = 5

        # Offset from wielder
        self.dist_offset = 0
        self.angle_offset = 0

    def update(self, delta):
        self.animate(delta)

    def animate(self, delta):
        if self.swing_time > Sword.FINISHED:
            self.swing_time = Sword.INACTIVE

        if self.swing_time < Sword.START:
            # Return to sheathed position
            if self.dist_offset > Sword.START_DIST_OFFSET:
                change = self.pos_speed * delta
                self.dist_offset = max(self.dist_offset - change, Sword.START_DIST_OFFSET)
            if self.angle_offset > Sword.START_ANGLE_OFFSET:
                change = self.angle_speed * delta
                self.angle_offset = max(self.angle_offset - change, Sword.START_ANGLE_OFFSET)
        else:
            # Progress through swing
            change = self.pos_speed * delta
            self.dist_offset = min(self.dist_offset + change, Sword.FINAL_DIST_OFFSET)
            self.angle_offset += self.angle_speed * delta

        self.swing_time += delta

    def draw(self, window):
        norm = Vector2(0, 1)
        norm.rotate_ip(self.angle + self.angle_offset)
        start_pos = self.pos + norm * self.dist_offset
        end_pos = self.pos + norm * (self.dist_offset + self.length)
        pygame.draw.line(window, Sword.COLOR, start_pos, end_pos, self.width)

    def activate(self):
        if self.swing_time == Sword.INACTIVE:
            self.swing_time = Sword.START

    def deactivate(self):
        self.swing_time = Sword.INACTIVE

    def hits_circle(self, other_pos, other_radius):
        norm = Vector2(0, 1)
        norm.rotate_ip(self.angle + self.angle_offset)
        end_pos = self.pos + norm * (self.dist_offset + self.length)
        dist = other_pos.distance_to(end_pos)
        return dist <= other_radius




