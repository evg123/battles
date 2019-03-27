"""
Main class with game loop
"""
import pygame
from src.util import FrameTimer
from src.graphics import Renderer, Colors
from src.army import Army
from src.soldier import Soldier
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
        #TODO temporary 2v2 setup
        army = Army(Colors.cyan)
        sldr = Soldier()
        sldr.army = army
        sldr.set_position(200, 250)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(1080, 250)

        sldr = Soldier()
        sldr.army = army
        sldr.set_position(200, 300)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(1080, 250)

        army = Army(Colors.orange)
        sldr = Soldier()
        sldr.army = army
        sldr.set_position(1080, 275)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(200, 350)

        sldr = Soldier()
        sldr.army = army
        sldr.set_position(1080, 350)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
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

        for sldr in self.soldiers.values():
            sldr.update(delta)

    def handle_interactions(self):
        #TODO optimize
        for sldr1 in self.soldiers.values():
            for sldr2 in self.soldiers.values():
                if sldr1 == sldr2:
                    continue
                sldr1.interact(sldr2)

    def clean_up(self):
        # Remove fully gone soldiers
        self.soldiers = {sid: sldr for sid, sldr in self.soldiers.items() if not sldr.needs_removal()}

    def draw(self):
        self.renderer.start_frame()

        for sldr in self.soldiers.values():
            sldr.draw(self.renderer)

        self.renderer.end_frame()


if __name__ == "__main__":
    BT = Battles()
    BT.setup()
    BT.run()
