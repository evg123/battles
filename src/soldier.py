"""
Class representing a soldier
"""
import pygame
from pygame import Vector2
import src.util as util
from src.weapon import Sword
from src.behavior import BehaviorTree


class Soldier:

    DEFAULT_RADIUS = 10
    DEFAULT_COLOR = (255, 255, 255)
    DEFAULT_CLEANUP_TIME = 10

    MAX_HEALTH = 100
    HEALING_FACTOR = 1.0

    next_id = 1

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self):
        self.my_id = Soldier.get_id()
        self.army_id = 0
        self.pos = Vector2()
        self.velocity = Vector2()
        self.velocity_steering = Vector2()
        self.max_velocity = 100 #TODO remove default after subclassing
        self.max_vel_accel = 10 #TODO remove default after subclassing
        self.facing = 0
        self.rotation = 0
        self.rotation_steering = 0
        self.max_rotation = 360 #TODO remove default after subclassing
        self.max_rot_accel = 20 #TODO remove default after subclassing
        self.radius = Soldier.DEFAULT_RADIUS
        self.color = Soldier.DEFAULT_COLOR
        self.health = Soldier.MAX_HEALTH
        self.cleanup_timer = Soldier.DEFAULT_CLEANUP_TIME
        self.behavior_tree = BehaviorTree("swordsman")
        self.weapon = Sword()
        self.weapon.update_wielder_pos(self.pos)

    def update(self, delta):
        # Countdown to removal if needed
        if not self.is_alive():
            self.cleanup_timer -= delta

        # Slow healing over time
        self.heal(Soldier.HEALING_FACTOR * delta)

        self.reset_steering()
        self.behavior_tree.run(self.my_id, delta)
        self.handle_steering()

        if self.weapon:
            self.weapon.update(delta)

    def reset_steering(self):
        self.velocity_steering.x = 0
        self.velocity_steering.y = 0
        self.rotation_steering = 0

    def handle_steering(self):
        # Velocity
        if self.velocity_steering.length() > self.max_vel_accel:
            self.velocity_steering.scale_to_length(self.max_vel_accel)
        self.velocity += self.velocity_steering
        if self.velocity.length() > self.max_velocity:
            self.velocity.scale_to_length(self.max_velocity)
        self.pos += self.velocity

        # Rotation
        if self.rotation_steering > self.max_rot_accel:
            self.rotation_steering = self.max_rot_accel
        self.rotation += self.rotation_steering
        if self.rotation > self.max_rotation:
            self.rotation = self.max_rotation
        self.facing += self.rotation

    def interact(self, other):
        if self.weapon:
            if self.weapon.hits_circle(other.pos, other.radius):
                other.take_damage(self.weapon.damage)
                self.weapon.deactivate()

    def draw(self, window):
        pygame.draw.circle(window, self.color, [int(self.pos.x), int(self.pos.y)], self.radius)

        self.weapon.draw(window)

    def move_to_coords(self, new_x, new_y):
        self.pos.x = new_x
        self.pos.y = new_y
        # Update weapon positions
        if self.weapon:
            self.weapon.update_wielder_pos(self.pos)

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

    def heal(self, amount):
        self.health += amount
        if self.health > Soldier.MAX_HEALTH:
            self.health = Soldier.MAX_HEALTH

    def take_damage(self, damage):
        self.health -= damage

    def overlaps(self, xpos, ypos):
        dist = util.distance(self.pos.x, self.pos.y, xpos, ypos)
        return dist <= self.radius

    def is_alive(self):
        return self.health > 0

    def needs_removal(self):
        return not self.is_alive() and self.cleanup_timer < 0

