"""
Classes representing weapons like a sword or bow
"""
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
    COLOR = (128, 128, 128)

    def __init__(self):
        super(Sword, self).__init__()
        self.pos_speed = 600
        self.angle_speed = 500
        self.damage = 30
        self.swing_time = self.INACTIVE
        self.length = 22
        self.width = 5
        self.attack_range = self.length + self.FINAL_DIST_OFFSET

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

    START_ANGLE_OFFSET = 0

    def __init__(self):
        super(Bow, self).__init__()
        self.arrows = []
        self.arrow_speed = 600
        self.damage = 20
        self.attack_range = 400

        # Offset from wielder
        self.dist_offset = 10
        self.angle_offset = self.START_ANGLE_OFFSET

    def update(self, delta):
        pass

    def draw(self, renderer):
        pass

    def activate(self):
        # Fire an arrow
        pass

    def deactivate(self):
        # Can't stop a fired arrow
        pass

    def hits_circle(self, other_pos, other_radius):
        # Check if any arrow hits the circle
        return False
