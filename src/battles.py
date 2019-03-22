"""
Main class with game loop
"""

import pygame

from src.util import FrameTimer
from src.soldier import Soldier
from src.behavior import BehaviorTree, Blackboard


class Battles:

    SCREEN_SIZE = (1280, 720)
    BACKGROUND_COLOR = (100, 100, 100)

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(Battles.SCREEN_SIZE)
        self._running = True
        self.soldiers = {}

    def setup(self):
        sldr = Soldier()
        sldr.army_id = 1
        sldr.move_to_coords(100, 300)
        self.soldiers[sldr.my_id] = sldr

        sldr = Soldier()
        sldr.army_id = 2
        sldr.move_to_coords(500, 300)
        self.soldiers[sldr.my_id] = sldr

    def run(self):
        frame_timer = FrameTimer()

        while self._running:
            delta = frame_timer.next_frame()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE):
                    self._running = False

            self.update(delta)
            self.handle_interactions()
            self.clean_up()
            self.draw()

    def update(self, delta):
        # Refresh blackboard shared data
        BehaviorTree.board()[Blackboard.SOLDIERS] = self.soldiers

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
    prog = Battles()
    prog.setup()
    prog.run()
