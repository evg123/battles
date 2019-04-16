"""
Class representing an army made up of formations of soldiers
"""
from pygame import Vector2
import src.util as util
from src.movable import Movable
from src.behavior import BehaviorTree
from src.graphics import Colors


class Army(Movable):
    """Made up of Formations"""
    COLORS = [Colors.orangered, Colors.darkgreen, Colors.darkblue, Colors.purple, Colors.yellow]
    ANCHOR_RADIUS = 11
    WAYPOINT_RADIUS = 15
    MARCH_SPEED = 70
    ROTATION_SPEED = 40

    next_id = 0

    @classmethod
    def get_id(cls):
        sid = cls.next_id
        cls.next_id += 1
        return sid

    @classmethod
    def next_color(cls):
        """Order of Army colors is hard-coded"""
        try:
            return cls.COLORS[cls.next_id]
        except IndexError:
            raise RuntimeError("No additional armies can be created")

    def __init__(self):
        super(Army, self).__init__()
        self.color = self.next_color()
        self.my_id = Army.get_id()
        self.waypoint = Vector2()
        self.formations = []
        self.max_velocity = self.MARCH_SPEED
        self.max_rotation = self.ROTATION_SPEED

    def set_waypoint(self, x_pos, y_pos):
        """Waypoint is the destination of the Army"""
        self.waypoint.x = x_pos
        self.waypoint.y = y_pos

    def update(self, delta):
        self.reset_steering()
        BehaviorTree.aim(self, self.waypoint)
        BehaviorTree.arrive(self, self.waypoint)
        self.handle_steering(delta)

        # Update all the formations
        for form in self.formations:
            form.update(delta, self.pos)

    def draw(self, renderer):
        if renderer.tactics_enabled:
            renderer.draw_circle(self.color, self.pos, self.ANCHOR_RADIUS)
            renderer.draw_circle(self.color, self.pos, self.ANCHOR_RADIUS, width=1)
        for form in self.formations:
            form.draw(renderer)

    def add_formation(self, formation, x_pos, y_pos):
        """Add the given formation to this Army"""
        formation.set_army(self)
        formation.set_position(x_pos, y_pos, self.facing)
        formation.refresh_army_offset()
        self.formations.append(formation)

    def remove_formation(self, formation):
        self.formations = [form for form in self.formations if form is not formation]

    def anchor_overlaps(self, x_pos, y_pos):
        """Returns True iff the given position falls within the anchor point"""
        dist = util.distance(self.pos.x, self.pos.y, x_pos, y_pos)
        return dist <= self.ANCHOR_RADIUS


