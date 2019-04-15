"""
Classes representing weapons like a sword or bow
"""
import math
from pygame import Vector2, Rect
from src.graphics import Colors

class Weapon:
    """Abstract base class"""

    def __init__(self):
        # Position of the weapon wielder
        self.pos = Vector2()
        # Angle relative to wielder
        self.angle = 0
        self.damage = 0
        self.stationary_time = 0

    def update(self, delta):
        pass

    def draw(self, renderer):
        raise NotImplementedError()

    def wielder_update(self, pos, facing):
        self.pos.x = pos.x
        self.pos.y = pos.y
        self.angle = facing

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

    START_DIST_OFFSET = 4
    FINAL_DIST_OFFSET = 8
    START_ANGLE_OFFSET = 0
    COLOR = Colors.darkgrey

    def __init__(self):
        super(Sword, self).__init__()
        self.pos_speed = 600
        self.angle_speed = 500
        self.damage = 30
        self.swing_time = self.INACTIVE
        self.length = 22
        self.width = 5
        self.attack_range = self.length + self.FINAL_DIST_OFFSET
        self.stationary_time = 0.1

        # Offset from wielder
        self.dist_offset = self.START_DIST_OFFSET
        self.angle_offset = self.START_ANGLE_OFFSET

    def update(self, delta):
        self.animate(delta)

    def animate(self, delta):
        if self.swing_time > self.FINISHED:
            self.swing_time = self.INACTIVE

        if self.swing_time < self.START:
            # Return to sheathed position
            if self.dist_offset > self.START_DIST_OFFSET:
                change = self.pos_speed * delta
                self.dist_offset = max(self.dist_offset - change, self.START_DIST_OFFSET)
            if self.angle_offset > self.START_ANGLE_OFFSET:
                change = self.angle_speed * delta
                self.angle_offset = max(self.angle_offset - change, self.START_ANGLE_OFFSET)
        else:
            # Progress through swing
            self.swing_time += delta
            change = self.pos_speed * delta
            self.dist_offset = min(self.dist_offset + change, self.FINAL_DIST_OFFSET)
            self.angle_offset += self.angle_speed * delta

    def draw(self, renderer):
        norm = Vector2(0, -1)
        norm.rotate_ip(self.angle + self.angle_offset)
        start_pos = self.pos + norm * self.dist_offset
        end_pos = self.pos + norm * (self.dist_offset + self.length)
        renderer.draw_line(self.COLOR, start_pos, end_pos, self.width)

    def activate(self):
        if self.swing_time == self.INACTIVE:
            self.swing_time = self.START

    def deactivate(self):
        self.swing_time = self.INACTIVE

    def hits_circle(self, other_pos, other_radius):
        if self.swing_time == self.INACTIVE:
            return False
        norm = Vector2(0, -1)
        norm.rotate_ip(self.angle + self.angle_offset)
        end_pos = self.pos + norm * (self.dist_offset + self.length)
        dist = other_pos.distance_to(end_pos)
        return dist <= other_radius


class Bow(Weapon):
    COLOR = [max(part - 90, 0) for part in Colors.brown]
    FIRING_SPEED = 2.0
    SIZE = 25
    CURVE = math.pi * .4
    ANGLE_FIX = math.pi * 0.5

    def __init__(self):
        super(Bow, self).__init__()
        self.arrows = []
        self.damage = 20
        self.attack_range = 400
        self.fire_timer = 0
        self.stationary_time = 0.2

        # Offset from wielder
        self.dist_offset = 6
        self.angle_offset = 0

    def update(self, delta):
        self.fire_timer -= delta

        for arrow in self.arrows:
            arrow.update(delta)

        # Remove spent arrows
        self.arrows = [arrow for arrow in self.arrows if not arrow.needs_removal()]

    def draw(self, renderer):
        norm = Vector2(0, -1)
        norm.rotate_ip(self.angle)
        pos = self.pos + norm * self.dist_offset
        rect = Rect(0, 0, self.SIZE, self.SIZE)
        rect.center = pos
        rads = math.radians(self.angle)
        renderer.draw_arc(self.COLOR, rect, self.ANGLE_FIX - rads - self.CURVE,
                          self.ANGLE_FIX - rads + self.CURVE, width=3)

        for arrow in self.arrows:
            arrow.draw(renderer)

    def activate(self):
        if self.fire_timer <= 0:
            # Fire an arrow
            arrow = Arrow(self.pos, self.angle)
            self.arrows.append(arrow)
            self.fire_timer = self.FIRING_SPEED

    def deactivate(self):
        # Can't stop a fired arrow
        pass

    def hits_circle(self, other_pos, other_radius):
        # Check if any arrow hits the circle
        for arrow in self.arrows:
            if arrow.hits_circle(other_pos, other_radius):
                return True
        return False


class Arrow(Weapon):

    COLOR = Colors.brown

    def __init__(self, pos, angle):
        super(Arrow, self).__init__()
        self.pos.x = pos.x
        self.pos.y = pos.y
        self.angle = angle
        self.length = 9
        self.width = 1
        self.flight_speed = 250
        self.max_distance = 400
        self.distance = 0
        self.hit = False  # has the arrow connected?

    def needs_removal(self):
        return self.distance > self.max_distance or self.hit

    def update(self, delta):
        norm = Vector2(0, -1)
        norm.rotate_ip(self.angle)
        dist = self.flight_speed * delta
        new_pos = self.pos + norm * dist
        self.pos.x = new_pos.x
        self.pos.y = new_pos.y
        # Keep track of how far the arrow has gone
        self.distance += dist

    def draw(self, renderer):
        norm = Vector2(0, -1)
        norm.rotate_ip(self.angle)
        end_pos = self.pos + norm * self.length
        renderer.draw_line(self.COLOR, self.pos, end_pos, self.width)

    def hits_circle(self, other_pos, other_radius):
        dist = other_pos.distance_to(self.pos)
        self.hit = dist <= other_radius
        return self.hit
