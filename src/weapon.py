"""
Classes representing weapons like a sword or bow
"""

import pygame
import src.util


class Weapon(object):
    """Abstract base class"""

    def __init__(self):
        # Position of the weapon wielder
        self.xpos = 0
        self.ypos = 0

        # Angle relative to wielder
        self.angle = 0

        self.damage = 0

    def update(self, delta):
        pass

    def draw(self):
        raise NotImplementedError()

    def update_wielder_pos(self, xpos, ypos):
        raise NotImplementedError()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def hits_circle(self, other_xpos, other_ypos, other_radius):
        raise NotImplementedError()


class Sword(Weapon):

    INACTIVE = -1.0
    START = 0.0
    FINISHED = 0.75

    START_DIST_OFFSET = 0
    FINAL_DIST_OFFSET = 20
    START_ANGLE_OFFSET = 0

    def __init__(self):
        super(Weapon, self).__init__()
        self.pos_speed = 1000
        self.angle_speed = 360
        self.damage = 30
        self.swing_time = Sword.INACTIVE

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
        pygame.draw.line(window, Sword.COLOR, , , width = 2)

    def activate(self):
        self.swing_time = Sword.START

    def deactivate(self):
        self.swing_time = Sword.INACTIVE




