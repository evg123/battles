"""
Class representing a soldier
"""
import src.util as util
from src.graphics import Colors
from src.weapon import Sword, Bow
from src.behavior import BehaviorTree
from src.movable import Movable


class Soldier(Movable):

    DEFAULT_RADIUS = 10
    DEFAULT_CLEANUP_TIME = 10
    DEFAULT_COLOR = Colors.white
    HEALING_FACTOR = 1.0

    next_id = 1

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self):
        super(Soldier, self).__init__()
        self.my_id = Soldier.get_id()
        self.army = None
        self.formation = None
        self.radius = Soldier.DEFAULT_RADIUS
        self.max_health = 0
        self.health = self.max_health
        self.cleanup_timer = Soldier.DEFAULT_CLEANUP_TIME
        self.behavior_tree = None
        self.weapon = None
        self.sight_range = 150
        self.slot_costs = (0, 0, 0)

    def set_position(self, x_pos, y_pos, facing=None):
        self.pos.x = x_pos
        self.pos.y = y_pos
        if facing is not None:
            self.facing = facing
        self.weapon.wielder_update(self.pos, self.facing)

    def set_position_vec(self, pos_vector):
        self.set_position(pos_vector.x, pos_vector.y)

    def update(self, delta):
        # Countdown to removal if needed
        if not self.is_alive():
            self.cleanup_timer -= delta
            if self.weapon:
                self.weapon.deactivate()
            return

        # Slow healing over time
        self.heal(Soldier.HEALING_FACTOR * delta)

        self.reset_steering()
        self.behavior_tree.run(self, delta)
        self.handle_steering(delta)

        if self.weapon:
            self.weapon.wielder_update(self.pos, self.facing)
            self.weapon.update(delta)

    def interact(self, other):
        if self.weapon:
            if self.weapon.hits_circle(other.pos, other.radius):
                other.take_damage(self.weapon.damage)
                self.weapon.deactivate()

    def draw(self, renderer):
        health_factor = self.health / self.max_health
        color = self.army.color if self.army else self.DEFAULT_COLOR
        current_color = [max(int(part * health_factor), 0) for part in color]
        renderer.draw_circle(current_color, self.pos, self.radius)
        renderer.draw_circle(Colors.black, self.pos, self.radius, 1)

        self.weapon.draw(renderer)

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        self.health -= damage

    def overlaps(self, xpos, ypos):
        dist = util.distance(self.pos.x, self.pos.y, xpos, ypos)
        return dist <= self.radius

    def is_alive(self):
        return self.health > 0

    def needs_removal(self):
        return not self.is_alive() and self.cleanup_timer < 0

    def attack(self):
        if self.weapon:
            self.weapon.activate()

    def get_attack_range(self):
        if not self.weapon:
            return 0
        return self.weapon.attack_range


class Swordsperson(Soldier):
    def __init__(self):
        super(Swordsperson, self).__init__()
        self.max_velocity = 120
        self.max_rotation = 300
        self.max_health = 100
        self.health = self.max_health
        self.behavior_tree = BehaviorTree("swordsman")
        self.weapon = Sword()
        self.slot_costs = (10, 0, 100)


class Archer(Soldier):
    def __init__(self):
        super(Archer, self).__init__()
        self.max_velocity = 150
        self.max_rotation = 300
        self.max_health = 60
        self.health = self.max_health
        self.behavior_tree = BehaviorTree("archer")
        self.weapon = Bow()
        self.slot_costs = (10, 100, 0)




