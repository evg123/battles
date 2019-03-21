"""
Class representing a soldier
"""
import pygame
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
        self.xpos = 0
        self.ypos = 0
        self.radius = Soldier.DEFAULT_RADIUS
        self.color = Soldier.DEFAULT_COLOR
        self.health = Soldier.MAX_HEALTH
        self.cleanup_timer = Soldier.DEFAULT_CLEANUP_TIME
        self.behavior_tree = BehaviorTree()
        self.weapon = Sword()
        self.weapon.update_wielder_pos(self.xpos, self.ypos)

    def update(self, delta):
        # Countdown to removal if needed
        if not self.is_alive():
            self.cleanup_timer -= delta

        # Slow healing over time
        self.heal(Soldier.HEALING_FACTOR * delta)

        if self.weapon:
            self.weapon.update(delta)

        self.behavior_tree.run(self.my_id, delta)

    def interact(self, other):
        if self.weapon:
            if self.weapon.hits_circle(other.xpos, other.ypos, other.radius):
                other.take_damage(self.weapon.damage)
                self.weapon.deactivate()

    def draw(self, window):
        pygame.draw.circle(window, self.color, [self.xpos, self.ypos], self.radius)

        self.weapon.draw(window)

    def move_to(self, new_x, new_y):
        self.xpos = new_x
        self.ypos = new_y
        # Update weapon positions
        if self.weapon:
            self.weapon.update_wielder_pos(self.xpos, self.ypos)

    def move_offset(self, xoff, yoff):
        self.move_to(self.xpos + xoff, self.ypos + yoff)

    def heal(self, amount):
        self.health += amount
        if self.health > Soldier.MAX_HEALTH:
            self.health = Soldier.MAX_HEALTH

    def take_damage(self, damage):
        self.health -= damage

    def overlaps(self, xpos, ypos):
        dist = util.distance(self.xpos, self.ypos, xpos, ypos)
        return dist <= self.radius

    def is_alive(self):
        return self.health > 0

    def needs_removal(self):
        return not self.is_alive() and self.cleanup_timer < 0

