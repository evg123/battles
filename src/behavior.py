"""
Implementation of behavior trees
"""


class Blackboard(dict):
    TARGET = "target"


class BehaviorTree(object):

    def __init__(self):
        self.root = None
        self.blackboard = Blackboard()

    def run(self, delta):
        if self.root is None:
            return True
        return self.root.run(delta, self.blackboard)

    class Node(object):
        def __init__(self):
            self.children = []

        def run(self, delta, blackboard):
            raise NotImplementedError()

    class Selector(Node):
        def run(self, delta, blackboard):
            for node in self.children:
                result = node.run(delta, blackboard)
                if result:
                    return True
            return False

    class Sequence(Node):
        def run(self, delta, blackboard):
            for node in self.children:
                result = node.run(delta, blackboard)
                if not result:
                    return False
            return True

    class Arrive(Node):
        def run(self, delta, blackboard):
            soldier = blackboard.getSoldier()
            target = blackboard.get(Blackboard.TARGET, None)

