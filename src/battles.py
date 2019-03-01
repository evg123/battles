
import pygame

class Battles(object):

    SCREEN_SIZE = [1280, 720]

    def __init__(self):
        pygame.init()
        pygame.display.set_mode(Battles.SCREEN_SIZE)
        self.running = True

    def run(self):
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE):
                    self.running = False
            pygame.display.update()


if __name__ == "__main__":
    prog = Battles()
    prog.run()