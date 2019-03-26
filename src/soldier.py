"""
Class representing a soldier
"""
import pygame
import src.util as util
from src.weapon import Sword, Bow
from src.behavior import BehaviorTree
from src.location import Location


class Soldier:

    DEFAULT_RADIUS = 10
    DEFAULT_CLEANUP_TIME = 10
    DEFAULT_COLOR = pygame.color.THECOLORS["white"]
    HEALING_FACTOR = 1.0

    next_id = 1

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self):
        self.my_id = Soldier.get_id()
        self.army = None
        self.formation = None
        self.loc = Location()
        self.radius = Soldier.DEFAULT_RADIUS
        self.max_health = 0
        self.health = self.max_health
        self.cleanup_timer = Soldier.DEFAULT_CLEANUP_TIME
        self.behavior_tree = None
        self.weapon = None
        self.weapon.wielder_update(self.pos, self.facing)
        self.sight_range = 150
        self.slot_costs = (0, 0, 0)

    def update(self, delta):
        # Countdown to removal if needed
        if not self.is_alive():
            self.cleanup_timer -= delta
            if self.weapon:
                self.weapon.deactivate()
            return

        # Slow healing over time
        self.heal(Soldier.HEALING_FACTOR * delta)

        self.loc.reset_steering()
        self.behavior_tree.run(self, delta)
        self.loc.handle_steering(delta)

        if self.weapon:
            self.weapon.wielder_update(self.loc)
            self.weapon.update(delta)

    def interact(self, other):
        if self.weapon:
            if self.weapon.hits_circle(other.pos, other.radius):
                other.take_damage(self.weapon.damage)
                self.weapon.deactivate()

    def draw(self, window):
        health_factor = self.health / self.max_health
        color = self.army.color if self.army else self.DEFAULT_COLOR
        current_color = [max(part * health_factor, 0) for part in color]
        pygame.draw.circle(window, current_color,
                           [int(self.loc.pos.x), int(self.loc.pos.y)], self.radius)#TODO just pass in loc.pos?
        pygame.draw.circle(window, pygame.color.THECOLORS["black"],
                           [int(self.loc.pos.x), int(self.loc.pos.y)], self.radius, 1)

        self.weapon.draw(window)

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        self.health -= damage

    def overlaps(self, xpos, ypos):
        dist = util.distance(self.loc.pos.x, self.loc.pos.y, xpos, ypos)
        return dist <= self.radius

    def is_alive(self):
        return self.health > 0

    def needs_removal(self):
        return not self.is_alive() and self.cleanup_timer < 0

    def attack(self):
        if self.weapon:
            self.weapon.activate()


class Swordsperson(Soldier):
    def __init__(self):
        super(Swordsperson, self).__init__()
        self.loc.max_velocity = 120
        self.loc.max_vel_accel = 40
        self.loc.max_rotation = 300
        self.loc.max_rot_accel = 80
        self.max_health = 100
        self.health = self.max_health
        self.behavior_tree = BehaviorTree("swordsman")
        self.weapon = Sword()
        self.slot_costs = (10, 0, 100)


class Archer(Soldier):
    def __init__(self):
        super(Archer, self).__init__()
        self.loc.max_velocity = 150
        self.loc.max_vel_accel = 60
        self.loc.max_rotation = 300
        self.loc.max_rot_accel = 80
        self.max_health = 60
        self.health = self.max_health
        self.behavior_tree = BehaviorTree("archer")
        self.weapon = Bow()
        self.slot_costs = (10, 100, 0)




