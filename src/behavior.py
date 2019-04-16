"""
Implementation of behavior trees
"""

import os
import json


class InvalidBehaviorTree(Exception):
    pass


class Blackboard:
    """Holds references to game objects needed by Behaviors"""
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
    """Loads Behaviors from disk"""
    @staticmethod
    def file_path_from_name(tree_name):
        return os.path.normpath(f"./behaviors/{tree_name}.json")

    @staticmethod
    def node_from_string(node_type_name):
        """Looks for a Behavior class with the given name"""
        try:
            return getattr(BehaviorTree, node_type_name)()
        except AttributeError:
            raise InvalidBehaviorTree(f"No behavior named '{node_type_name}'' found")

    @staticmethod
    def load_from_file(tree_name):
        """Load a Behavior tree from disk.
        """
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
        """Load a Behavior tree from the given JSON.
        Follows references to files and loads them as well.
        """
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
    """Holds a tree made up of Behaviors"""
    ARRIVE_SLOW_RADIUS = 100
    ARRIVE_STOP_RADIUS = 25
    AIM_SLOW_RADIUS = 40.0
    AIM_STOP_RADIUS = 2.0

    _blackboard = Blackboard()

    @staticmethod
    def board():
        """Gets the blackboard for this tree"""
        return BehaviorTree._blackboard

    def __init__(self, file_path):
        self.root = TreeLoader.load_from_file(file_path)

    def run(self, soldier, delta):
        if self.root is None:
            return True
        return self.root.run(soldier, delta)

    @staticmethod
    def arrive(movable, destination, flee=False,
               slow_radius=ARRIVE_SLOW_RADIUS, stop_radius=ARRIVE_STOP_RADIUS):
        """Helper with arrive steering behavior"""
        if flee:
            direction = movable.pos - destination
        else:
            direction = destination - movable.pos
        dist = direction.length()
        if dist < stop_radius:
            goal_speed = 0
        else:
            direction.normalize_ip()
            if dist > slow_radius:
                goal_speed = movable.max_velocity
            else:
                goal_speed = movable.max_velocity * dist / slow_radius
        goal_velocity = direction * goal_speed
        movable.add_velocity_steering(goal_velocity - movable.velocity)
        return True

    @staticmethod
    def aim(movable, destination, slow_radius=AIM_SLOW_RADIUS, stop_radius=AIM_STOP_RADIUS):
        """Helper with aim steering behavior"""
        rotation = movable.get_rotation_to_dest(destination)
        rot_size = abs(rotation)
        if rot_size < stop_radius:
            goal_rot = 0
        else:
            if rot_size > slow_radius:
                goal_rot = movable.max_rotation
            else:
                goal_rot = movable.max_rotation * rot_size / slow_radius
            goal_rot *= rotation / rot_size
        movable.add_rotation_steering(goal_rot - movable.rotation)
        return True

    class LeafNode:
        """Parent class for non-composite behaviors"""
        def run(self, soldier, delta):
            raise NotImplementedError()

        def add_child(self, child):
            raise InvalidBehaviorTree(f"{self.__class__} does not support adding children")

    class CompositeNode:
        """Parent class for behaviors that hold other behaviors"""
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
            BehaviorTree.CompositeNode.add_child(self, child)

    class AlwaysTrue(CompositeNode):
        def run(self, soldier, delta):
            self.children[0].run(soldier, delta)
            return True

        def add_child(self, child):
            if self.children:
                raise InvalidBehaviorTree("AlwaysTrue supports at most 1 child")
            BehaviorTree.CompositeNode.add_child(self, child)

    class ArriveTarget(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            return BehaviorTree.arrive(soldier, target.pos)

    class ArriveWaypoint(LeafNode):
        SLOW_RAD = 30
        STOP_RAD = 2

        def run(self, soldier, delta):
            waypoint = BehaviorTree.board().get_for_id(Blackboard.WAYPOINT, soldier.my_id)
            if not waypoint:
                return False
            return BehaviorTree.arrive(soldier, waypoint, slow_radius=self.SLOW_RAD,
                                       stop_radius=self.STOP_RAD)

    class AimTarget(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            return BehaviorTree.aim(soldier, target.pos)

    class AimWaypoint(LeafNode):
        def run(self, soldier, delta):
            waypoint = BehaviorTree.board().get_for_id(Blackboard.WAYPOINT, soldier.my_id)
            if not waypoint:
                return False
            return BehaviorTree.aim(soldier, waypoint)

    class FleeTarget(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            return BehaviorTree.arrive(soldier, target.pos, flee=True)

    class SpreadOut(LeafNode):
        SPREAD_DIST = 20

        def run(self, soldier, delta):
            soldiers = BehaviorTree.board()[Blackboard.SOLDIERS]
            for other in soldiers.values():
                if soldier.my_id == other.my_id or not other.is_alive():
                    continue
                displacement = soldier.pos - other.pos
                if displacement.length() < self.SPREAD_DIST:
                    displacement.normalize()
                    steering = displacement * soldier.max_velocity
                    soldier.add_velocity_steering(steering)
            return True

    class HasTarget(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if target is None or not target.is_alive():
                return False
            return True

    class TargetEnemy(LeafNode):
        def run(self, soldier, delta):
            soldiers = BehaviorTree.board()[Blackboard.SOLDIERS]
            closest_enemy = None
            closest_dist = float("inf")
            for enemy in soldiers.values():
                if enemy.army == soldier.army:
                    # Same team
                    continue
                if not enemy.is_alive():
                    continue
                dist = soldier.pos.distance_to(enemy.pos)
                if dist <= soldier.sight_range and dist <= closest_dist:
                    # This is the closest so far
                    closest_enemy = enemy
                    closest_dist = dist
            if not closest_enemy:
                # No enemies in range
                return False
            BehaviorTree.board()[Blackboard.TARGET][soldier.my_id] = closest_enemy
            return True

    class TargetInAttackRange(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            return soldier.pos.distance_to(target.pos) <= soldier.get_attack_range()

    class FacingTarget(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            rotation = soldier.get_rotation_to_dest(target.pos)
            rot_size = abs(rotation)
            return rot_size <= BehaviorTree.AIM_STOP_RADIUS

    class TargetInFleeRange(LeafNode):
        def run(self, soldier, delta):
            target = BehaviorTree.board().get_for_id(Blackboard.TARGET, soldier.my_id)
            if not target or not target.is_alive():
                return False
            return soldier.pos.distance_to(target.pos) <= soldier.get_flee_range()

    class Attack(LeafNode):
        def run(self, soldier, delta):
            soldier.attack()
            return True

    class TakeFormationWaypoint(LeafNode):
        def run(self, soldier, delta):
            if not soldier.formation:
                return False
            waypoint = soldier.formation.get_soldier_slot_position(soldier.my_id)
            if not waypoint:
                return False
            BehaviorTree.board()[Blackboard.WAYPOINT][soldier.my_id] = waypoint
            return True

