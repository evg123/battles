"""
Class representing an army made up of formations of soldiers
"""
from pygame import Vector2
import src.util as util
from src.movable import Movable
from src.behavior import BehaviorTree
from src.formation import FormationLoader
from src.graphics import Colors


class Army(Movable):

    COLORS = [Colors.orangered, Colors.darkgreen, Colors.darkblue]
    ANCHOR_RADIUS = 15
    WAYPOINT_RADIUS = 15
    MARCH_SPEED = 90
    ROTATION_SPEED = 40

    next_id = 0

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    @classmethod
    def next_color(cls):
        #TODO handle out of colors
        return cls.COLORS[cls.next_id]

    def __init__(self):
        super(Army, self).__init__()
        self.color = self.next_color()
        self.my_id = Army.get_id()
        self.waypoint = Vector2()
        self.formations = []
        self.max_velocity = self.MARCH_SPEED
        self.max_rotation = self.ROTATION_SPEED

    def set_waypoint(self, x_pos, y_pos):
        self.waypoint.x = x_pos
        self.waypoint.y = y_pos

    def update(self, delta):
        self.reset_steering()
        BehaviorTree.aim(self, self.waypoint)
        BehaviorTree.arrive(self, self.waypoint)
        self.handle_steering(delta)

        for form in self.formations:
            form.update(delta, self.pos)

    def draw(self, renderer):
        if renderer.tactics_enabled:
            renderer.draw_circle(self.color, self.pos, self.ANCHOR_RADIUS)
        for form in self.formations:
            form.draw(renderer)

    def add_formation(self, formation, x_pos, y_pos):
        formation.set_army(self)
        formation.set_position(x_pos, y_pos, self.facing)
        formation.refresh_army_offset()
        self.formations.append(formation)

    def anchor_overlaps(self, x_pos, y_pos):
        dist = util.distance(self.pos.x, self.pos.y, x_pos, y_pos)
        return dist <= self.ANCHOR_RADIUS


