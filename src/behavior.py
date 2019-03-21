"""
Implementation of behavior trees
"""


class Blackboard(dict):
    SOLDIERS = "soldiers"
    ARMIES = "armies"
    TARGET = "target"

    def get_for_id(self, key, sid):
        parent = self.get(key, None)
        if parent is None:
            return None
        return parent.get(sid, None)


class BehaviorTree:
    _blackboard = Blackboard()

    def __init__(self):
        self.root = None

    def run(self, my_id, delta):
        if self.root is None:
            return True
        return self.root.run(my_id, delta)

    class Node:

        @staticmethod
        def board():
            return BehaviorTree._blackboard

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
        def run(self, my_id, delta):
            soldier = self.board().get_for_id(Blackboard.SOLDIERS, my_id)
            target = self.board().get_for_id(Blackboard.TARGET, my_id)

