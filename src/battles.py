"""
Main class with game loop
"""
import pygame
from src.util import FrameTimer
from src.graphics import Renderer, Colors
from src.army import Army
from src.soldier import Swordsperson, Archer
from src.behavior import BehaviorTree, Blackboard


class Battles:

    WINDOW_TITLE = "Battle Demo"
    SCREEN_SIZE = (1280, 720)

    def __init__(self):
        pygame.init()
        self.renderer = Renderer(self.WINDOW_TITLE, self.SCREEN_SIZE)
        self._running = True
        self.armies = {}
        self.soldiers = {}

    def setup(self):
        # Left Army
        army = Army(Colors.cyan)
        army.pos.x = 200
        army.pos.y = 350
        army.add_formation("basic_1", 150, 300)
        army.add_formation("basic_1", 200, 400)

        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())

        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())

        army.set_waypoint(1000, 350)

        # Right Army
        army = Army(Colors.cyan)
        army.pos.x = 1080
        army.pos.y = 350
        army.add_formation("basic_1", 1080, 200)
        army.add_formation("basic_1", 1080, 350)
        army.add_formation("basic_1", 1080, 500)

        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Swordsperson())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())
        army.formations[0].add_soldier(Archer())

        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())
        army.formations[1].add_soldier(Swordsperson())

        army.formations[2].add_soldier(Swordsperson())
        army.formations[2].add_soldier(Archer())
        army.formations[2].add_soldier(Archer())
        army.formations[2].add_soldier(Archer())

        army.set_waypoint(200, 350)

    def run(self):
        frame_timer = FrameTimer()

        while self._running:
            delta = frame_timer.next_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    self._running = False

            self.update(delta)
            self.handle_interactions()
            self.clean_up()
            self.draw()

    def update(self, delta):
        # Refresh blackboard shared data
        BehaviorTree.board()[Blackboard.SOLDIERS] = self.soldiers
        BehaviorTree.board()[Blackboard.ARMIES] = self.armies

        for army in self.armies:
            army.update(delta)

        for soldier in self.soldiers.values():
            soldier.update(delta)

    def handle_interactions(self):
        #TODO optimize
        for soldier1 in self.soldiers.values():
            for soldier2 in self.soldiers.values():
                if soldier1 == soldier2:
                    continue
                soldier1.interact(soldier2)

    def clean_up(self):
        # Remove fully gone soldiers
        self.soldiers = {sid: soldier for sid, soldier in self.soldiers.items() if not soldier.needs_removal()}

    def draw(self):
        self.renderer.start_frame()

        for army in self.armies:
            army.draw(self.renderer)

        for soldier in self.soldiers.values():
            soldier.draw(self.renderer)

        self.renderer.end_frame()


if __name__ == "__main__":
    BT = Battles()
    BT.setup()
    BT.run()
