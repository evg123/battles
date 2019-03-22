"""
Implementation of behavior trees
"""

import json


class InvalidBehaviorTree(Exception):
    pass


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


class TreeLoader:
    @staticmethod
    def file_path_from_name(tree_name):
        return f"./behavior_trees/{tree_name}.json"

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
            for child_json in bt_json[0:]:
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

    def run(self, my_id, delta):
        if self.root is None:
            return True
        return self.root.run(my_id, delta)

    class Node:
        def __init__(self):
            self.children = []

        def run(self, my_id, delta):
            raise NotImplementedError()

        def add_child(self, child):
            self.children.append(child)

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

    class Invert(Node):
        def run(self, my_id, delta):
            return not self.children[0].run(my_id, delta)

        def add_child(self, child):
            if self.children:
                raise InvalidBehaviorTree("Invert supports at most 1 child")
            BehaviorTree.Node.add_child(self, child)

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

        def add_child(self, child):
            raise InvalidBehaviorTree("Arrive does not support adding children")

    class Align(Node):
        SLOW_RADIUS = 20.0
        STOP_RADIUS = 2.0

        def run(self, my_id, delta):
            sldr = BehaviorTree.board().get_for_id(Blackboard.SOLDIERS, my_id)
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, my_id)
            if not target:
                return False

            direction = target.pos - sldr.pos
            rotation = direction.angle_to(sldr.facing)
            if rotation > 180:
                rotation -= 360
            elif rotation < -180:
                rotation += 360

            rot_size = abs(rotation)
            if rot_size < self.STOP_RADIUS:
                goal_rot = 0
            elif rot_size > self.SLOW_RADIUS:
                goal_rot = sldr.max_rotation
            else:
                goal_rot = sldr.max_rotation * rot_size / self.SLOW_RADIUS

            goal_rot *= rotation / rot_size
            sldr.add_rotation_steering(goal_rot - sldr.rotation)
            return True

        def add_child(self, child):
            raise InvalidBehaviorTree("Align does not support adding children")

