"""
Implementation of behavior trees
"""

from pygame import Vector2


class Blackboard:
    SOLDIERS = "soldiers"
    ARMIES = "armies"
    TARGET = "target"

    def __init__(self):
        self._bb = {
            Blackboard.SOLDIERS: {},
            Blackboard.ARMIES: {},
            Blackboard.TARGET: {},
        }

    def __getitem__(self, item):
        return self._bb[item]

    def __setitem__(self, key, value):
        self._bb[key] = value

    def get_for_id(self, key, sid):
        parent = self._bb.get(key, None)
        if parent is None:
            return None
        return parent.get(sid, None)


class BehaviorTree:
    _blackboard = Blackboard()

    @staticmethod
    def board():
        return BehaviorTree._blackboard

    def __init__(self):
        self.root = None

    def run(self, my_id, delta):
        if self.root is None:
            return True
        return self.root.run(my_id, delta)

    class Node:
        def __init__(self):
            self.children = []

        def run(self, my_id, delta):
            raise NotImplementedError()

    class Selector(Node):
        def run(self, my_id, delta):
            for node in self.children:
                result = node.run(my_id, delta)
                if result:
                    return True
            return False

    class Sequence(Node):
        def run(self, my_id, delta):
            for node in self.children:
                result = node.run(my_id, delta)
                if not result:
                    return False
            return True

    class Arrive(Node):
        SLOW_RADIUS = 100
        STOP_RADIUS = 50

        def run(self, my_id, delta):
            sldr = BehaviorTree.board().get_for_id(Blackboard.SOLDIERS, my_id)
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, my_id)
            if not target:
                return False

            direction = target.pos - sldr.pos
            dist = direction.magnitude()
            if dist < self.STOP_RADIUS:
                goal_speed = 0
            elif dist > self.SLOW_RADIUS:
                goal_speed = sldr.max_speed
            else:
                goal_speed = sldr.max_speed * dist / self.SLOW_RADIUS
            direction.normalize_ip()
            goal_velocity = direction * goal_speed
            sldr.add_velocity_steering(goal_velocity - sldr.velocity)

            return True

    class Align(Node):
        SLOW_RADIUS = 20.0
        STOP_RADIUS = 2.0

