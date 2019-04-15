"""
Class that represents an objects position and orientation in the world
"""

from pygame import Vector2
import src.util as util


class Movable:
    """Abstract class used by things that move and are steerable"""
    def __init__(self):
        self.pos = Vector2()
        self.velocity = Vector2()
        self.velocity_steering = Vector2()
        self.max_velocity = 0
        self.max_vel_accel = 60
        self.facing = 0
        self.rotation = 0
        self.rotation_steering = 0
        self.max_rotation = 0
        self.max_rot_accel = 80
        self.stationary_timer = 0

    def set_position(self, x_pos, y_pos, facing=None):
        self.pos.x = x_pos
        self.pos.y = y_pos
        if facing is not None:
            self.facing = facing

    def reset_steering(self):
        self.velocity_steering.x = 0
        self.velocity_steering.y = 0
        self.rotation_steering = 0

    def handle_steering(self, delta):
        """Apply the current steering values to move this moveable"""
        # Velocity
        # Don't move if we are temporarily stationary
        if self.stationary_timer <= 0:
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

    def add_velocity_steering(self, steering):
        if steering.length() > self.max_vel_accel:
            steering.scale_to_length(self.max_vel_accel)
        self.velocity_steering += steering

    def add_rotation_steering(self, steering):
        if steering > self.max_rot_accel:
            steering = self.max_rot_accel
        self.rotation += steering

    def get_rotation_to_dest(self, destination):
        """Calculate the angle in degrees from this movable to the destination"""
        direction = destination - self.pos
        facing = Vector2(0, -1)
        facing.rotate_ip(self.facing)
        rotation = facing.angle_to(direction)
        return util.normalize_rotation(rotation)

