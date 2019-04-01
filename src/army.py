"""
Class representing an army made up of formations of soldiers
"""
from pygame import Vector2
from src.movable import Movable
from src.behavior import BehaviorTree
from src.formation import FormationLoader
from src.graphics import Colors


class Army(Movable):

    COLORS = [Colors.orangered, Colors.darkgreen, Colors.darkblue]
    ANCHOR_RADIUS = 15
    MARCH_SPEED = 90
    ROTATION_SPEED = 40

    next_id = 0

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    def __init__(self):
        super(Army, self).__init__()
        self.my_id = Army.get_id()
        self.color = self.COLORS[self.my_id] #TODO handle out of colors
        self.waypoint = Vector2()
        self.formations = []
        self.max_velocity = self.MARCH_SPEED
        self.max_rotation = self.ROTATION_SPEED

    def set_waypoint(self, xpos, ypos):
        self.waypoint.x = xpos
        self.waypoint.y = ypos

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

    def add_formation(self, formation_name, x_pos, y_pos):
        form = FormationLoader.load(formation_name)
        form.set_army(self)
        form.pos.x = x_pos
        form.pos.y = y_pos
        form.army_offset.x = x_pos - self.pos.x
        form.army_offset.y = y_pos - self.pos.y
        self.formations.append(form)


