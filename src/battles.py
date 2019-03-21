"""
Main class with game loop
"""

import pygame

from src.util import FrameTimer
from src.soldier import Soldier


class Battles(object):

    SCREEN_SIZE = [1280, 720]

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(Battles.SCREEN_SIZE)
        self._running = True
        self.soldiers = []

    def setup(self):
        sld = Soldier()
        sld.moveTo(100, 300)
        self.soldiers.append(sld)

        sld = Soldier()
        sld.moveTo(500, 300)
        self.soldiers.append(sld)

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
        for sld in self.soldiers:
            sld.update(delta)

    def handle_interactions(self):
        #TODO optimize
        for sld1 in self.soldiers:
            for sld2 in self.soldiers:
                if sld1 == sld2:
                    continue
                sld1.interact(sld2)

    def clean_up(self):
        # Remove fully gone soldiers
        self.soldiers = [sld for sld in self.soldiers if not sld.needs_removal()]

    def draw(self):
        for sld in self.soldiers:
            sld.draw(self.window)

        pygame.display.update()


if __name__ == "__main__":
    prog = Battles()
    prog.setup()
    prog.run()
