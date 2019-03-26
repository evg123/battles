"""
Main class with game loop
"""

import pygame

from src.util import FrameTimer
from src.army import Army
from src.soldier import Soldier
from src.behavior import BehaviorTree, Blackboard


class Battles:

    WINDOW_TITLE = "Battle Demo"
    SCREEN_SIZE = (1280, 720)
    BACKGROUND_COLOR = (220, 220, 220)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(self.WINDOW_TITLE)
        self.window = pygame.display.set_mode(Battles.SCREEN_SIZE)
        self._running = True
        self.armies = {}
        self.soldiers = {}

    def setup(self):
        #TODO temporary 2v2 setup
        army = Army(pygame.color.THECOLORS['cyan'])
        sldr = Soldier()
        sldr.army = army
        sldr.move_to_coords(200, 250)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(1080, 250)

        sldr = Soldier()
        sldr.army = army
        sldr.move_to_coords(200, 300)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(1080, 250)

        army = Army(pygame.color.THECOLORS['orange'])
        sldr = Soldier()
        sldr.army = army
        sldr.move_to_coords(1080, 275)
        self.armies[army.my_id] = army
        self.soldiers[sldr.my_id] = sldr
        army.set_waypoint(200, 350)

        sldr = Soldier()
        sldr.army = army
        sldr.move_to_coords(1080, 350)
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
        self.window.fill(Battles.BACKGROUND_COLOR)

        for sldr in self.soldiers.values():
            sldr.draw(self.window)

        pygame.display.update()


if __name__ == "__main__":
    BT = Battles()
    BT.setup()
    BT.run()
