"""
Class that represents an objects position and orientation in the world
"""

from pygame import Vector2


class Location:
    def __init__(self):
        self.pos = Vector2()
        self.velocity = Vector2()
        self.velocity_steering = Vector2()
        self.max_velocity = 0
        self.max_vel_accel = 0
        self.facing = 0
        self.rotation = 0
        self.rotation_steering = 0
        self.max_rotation = 0
        self.max_rot_accel = 0

    def reset_steering(self):
        self.velocity_steering.x = 0
        self.velocity_steering.y = 0
        self.rotation_steering = 0

    def handle_steering(self, delta):
        # Velocity
        if self.velocity_steering.length() > self.max_vel_accel:
            self.velocity_steering.scale_to_length(self.max_vel_accel)
        self.velocity += self.velocity_steering
        if self.velocity.length() > self.max_velocity:
            self.velocity.scale_to_length(self.max_velocity)
        self.pos += self.velocity * delta

        # Rotation
        if self.rotation_steering > self.max_rot_accel:
            self.rotation_steering = self.max_rot_accel
        self.rotation += self.rotation_steering
        if abs(self.rotation) > self.max_rotation:
            self.rotation = self.max_rotation * (self.rotation / abs(self.rotation))
        self.facing += self.rotation * delta
        self.facing = util.normalize_rotation(self.facing)

    def move_to_coords(self, new_x, new_y):
        self.pos.x = new_x
        self.pos.y = new_y
        # Update weapon positions
        if self.weapon:
            self.weapon.wielder_update(self.pos, self.facing)

    def move_to_vec2(self, new_pos):
        self.move_to_coords(new_pos.x, new_pos.y)

    def move_offset(self, xoff, yoff):
        self.move_to_coords(self.pos.x + xoff, self.pos.y + yoff)

    def add_velocity_steering(self, steering):
        if steering.length() > self.max_vel_accel:
            steering.scale_to_length(self.max_vel_accel)
        self.velocity_steering += steering

    def add_rotation_steering(self, steering):
        if steering > self.max_rot_accel:
            steering = self.max_rot_accel
        self.rotation += steering

