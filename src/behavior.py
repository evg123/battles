"""
Implementation of behavior trees
"""

import json
from pygame import Vector2


class InvalidBehaviorTree(Exception):
    pass


class Blackboard:
    SOLDIERS = "soldiers"
    ARMIES = "armies"
    TARGET = "target"
    WAYPOINT = "waypoint"

    def __init__(self):
        self._bb = {
            Blackboard.SOLDIERS: {},
            Blackboard.ARMIES: {},
            Blackboard.TARGET: {},
            Blackboard.WAYPOINT: {},
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


class TreeLoader:
    @staticmethod
    def file_path_from_name(tree_name):
        return f"./behaviors/{tree_name}.json"

    @staticmethod
    def node_from_string(node_type_name):
        try:
            return getattr(BehaviorTree, node_type_name)()
        except AttributeError:
            raise InvalidBehaviorTree(f"No behavior named '{node_type_name}'' found")

    @staticmethod
    def load_from_file(tree_name):
        #TODO detect cycles
        file_path = TreeLoader.file_path_from_name(tree_name)
        try:
            with open(file_path) as def_file:
                bt_json = json.load(def_file)
            return TreeLoader.load_from_json(bt_json)
        except FileNotFoundError:
            raise InvalidBehaviorTree(f"Behavior tree definition file not found: {file_path}")
        except json.JSONDecodeError as ex:
            raise InvalidBehaviorTree(f"Behavior tree definition '{file_path}' could not be parsed: {ex}")

    @staticmethod
    def load_from_json(bt_json):
        if isinstance(bt_json, list):
            # This node is a composite
            ntype = bt_json[0]
            node = TreeLoader.node_from_string(ntype)
            for child_json in bt_json[1:]:
                child = TreeLoader.load_from_json(child_json)
                node.add_child(child)
            return node
        if isinstance(bt_json, str):
            # This is a leaf behavior node or reference to a sub-tree file
            try:
                # Check for a leaf behavior
                return TreeLoader.node_from_string(bt_json)
            except InvalidBehaviorTree:
                pass
                # This could be a sub-tree defined in a file
            # Look for a tree definition json file with this name
            return TreeLoader.load_from_file(bt_json)
        # Should not reach here
        raise InvalidBehaviorTree(f"Malformed behavior tree: {bt_json}")


class BehaviorTree:

    _blackboard = Blackboard()

    @staticmethod
    def board():
        return BehaviorTree._blackboard

    def __init__(self, file_path):
        self.root = TreeLoader.load_from_file(file_path)

    def run(self, soldier, delta):
        if self.root is None:
            return True
        return self.root.run(soldier, delta)

    @staticmethod
    def _arrive(soldier, destination, slow_radius, stop_radius):
        direction = destination - soldier.pos
        dist = direction.length()
        if dist < stop_radius:
            goal_speed = 0
        else:
            direction.normalize_ip()
            if dist > slow_radius:
                goal_speed = soldier.max_velocity
            else:
                goal_speed = soldier.max_velocity * dist / slow_radius
        goal_velocity = direction * goal_speed
        soldier.add_velocity_steering(goal_velocity - soldier.velocity)
        return True

    @staticmethod
    def _aim(soldier, destination, slow_radius, stop_radius):
        direction = destination - soldier.pos
        facing = Vector2(0, 1)
        facing.rotate_ip(soldier.facing)
        rotation = direction.angle_to(facing)
        if rotation > 180:
            rotation -= 360
        elif rotation < -180:
            rotation += 360

        rot_size = abs(rotation)
        if rot_size < stop_radius:
            goal_rot = 0
        elif rot_size > slow_radius:
            goal_rot = soldier.max_rotation
        else:
            goal_rot = soldier.max_rotation * rot_size / slow_radius

        goal_rot *= rotation / rot_size
        soldier.add_rotation_steering(goal_rot - soldier.rotation)
        return True

    class LeafNode:
        def run(self, soldier, delta):
            raise NotImplementedError()

        def add_child(self, child):
            raise InvalidBehaviorTree(f"{self.__class__} does not support adding children")

    class CompositeNode:
        def __init__(self):
            self.children = []

        def run(self, soldier, delta):
            raise NotImplementedError()

        def add_child(self, child):
            self.children.append(child)

    class Selector(CompositeNode):
        def run(self, soldier, delta):
            for node in self.children:
                result = node.run(soldier, delta)
                if result:
                    return True
            return False

    class Sequence(CompositeNode):
        def run(self, soldier, delta):
            for node in self.children:
                result = node.run(soldier, delta)
                if not result:
                    return False
            return True

    class Invert(CompositeNode):
        def run(self, soldier, delta):
            return not self.children[0].run(soldier, delta)

        def add_child(self, child):
            if self.children:
                raise InvalidBehaviorTree("Invert supports at most 1 child")
            BehaviorTree.Node.add_child(self, child)

    class ArriveTarget(LeafNode):
        SLOW_RADIUS = 100
        STOP_RADIUS = 50

        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target:
                return False
            return BehaviorTree._arrive(soldier, target.pos, self.SLOW_RADIUS, self.STOP_RADIUS)

    class ArriveWaypoint(LeafNode):
        SLOW_RADIUS = 100
        STOP_RADIUS = 50

        def run(self, soldier, delta):
            waypoint = BehaviorTree.board().get_for_id(Blackboard.WAYPOINT, soldier.my_id)
            if not waypoint:
                return False
            return BehaviorTree._arrive(soldier, waypoint, self.SLOW_RADIUS, self.STOP_RADIUS)

    class AimTarget(LeafNode):
        SLOW_RADIUS = 20.0
        STOP_RADIUS = 2.0

        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target:
                return False
            return BehaviorTree._aim(soldier, target.pos, self.SLOW_RADIUS, self.STOP_RADIUS)

    class AimWaypoint(LeafNode):
        SLOW_RADIUS = 20.0
        STOP_RADIUS = 2.0

        def run(self, soldier, delta):
            waypoint = BehaviorTree.board().get_for_id(Blackboard.WAYPOINT, soldier.my_id)
            if not waypoint:
                return False
            return BehaviorTree._aim(soldier, waypoint, self.SLOW_RADIUS, self.STOP_RADIUS)

    class TargetEnemy(LeafNode):
        def run(self, soldier, delta):
            armies = BehaviorTree.board()[Blackboard.ARMIES]
            #TODO select randomly instead of the first one you find
            for army_id, army in armies.items():
                if army_id == soldier.army_id:
                    continue
                for enemy in army.soldiers:
                    if soldier.pos.distance_to(enemy.pos) <= soldier.sight_range:
                        BehaviorTree.board()[Blackboard.TARGET][soldier.my_id] = enemy
                        return True
            return False

    class TargetInRange(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            return soldier.pos.distance_to(target.pos) <= soldier.attack_range

    class Attack(LeafNode):
        def run(self, soldier, delta):
            soldier.attack()

    class TakeArmyWaypoint(LeafNode):
        def run(self, soldier, delta):
            army = BehaviorTree.board().get_for_id(Blackboard.ARMIES, soldier.army_id)
            BehaviorTree.board()[Blackboard.WAYPOINT][soldier.my_id] = army.waypoint
            return True

