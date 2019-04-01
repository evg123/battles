"""
Main class with game loop
"""
import pygame
from src.util import FrameTimer
from src.graphics import Renderer, Colors
from src.army import Army
from src.soldier import Swordsperson, Archer
from src.behavior import BehaviorTree, Blackboard
from src.formation import FormationLoader


# Game states
class GameModes:
    WATCH, \
        PLACE_ARMY, \
        SET_ARMY_WAYPOINT, \
        PLACE_FORMATION,\
        MOVE_FORMATION,\
        PLACE_SOLDIER, \
        REMOVE \
        = range(7)


class Battles:

    WINDOW_TITLE = "Battle Demo"
    SCREEN_SIZE = (1280, 720)

    def __init__(self):
        pygame.init()
        self.renderer = Renderer(self.WINDOW_TITLE, self.SCREEN_SIZE)
        self._running = True
        self._paused = False
        self._mode = GameModes.WATCH
        self._display_help = False
        self.armies = {}
        self.soldiers = {}
        self.buttons = []
        self.active_army = None
        FormationLoader.find_formations()
        self.active_formation_type = FormationLoader.available_formations[0]

    def create_army(self, position):
        army = Army()
        army.pos.x = position[0]
        army.pos.y = position[1]
        self.armies[army.my_id] = army
        return army

    def create_soldier(self, soldier_class):
        soldier = soldier_class()
        self.soldiers[soldier.my_id] = soldier
        return soldier

    def setup(self):
        # Left Army
        army = self.create_army((200, 350))
        army.add_formation("basic_1", 150, 300)
        army.add_formation("basic_1", 200, 400)

        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))

        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))

        #army.set_waypoint(1000, 350)

        # Right Army
        army = self.create_army((1080, 350))
        army.add_formation("basic_1", 1080, 200)
        army.add_formation("basic_1", 1080, 350)
        army.add_formation("basic_1", 1080, 500)

        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))
        army.formations[0].add_soldier(self.create_soldier(Archer))

        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))

        army.formations[2].add_soldier(self.create_soldier(Swordsperson))
        army.formations[2].add_soldier(self.create_soldier(Archer))
        army.formations[2].add_soldier(self.create_soldier(Archer))
        army.formations[2].add_soldier(self.create_soldier(Archer))

        #army.set_waypoint(200, 350)

    def run(self):
        frame_timer = FrameTimer()

        while self._running:
            delta = frame_timer.next_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYUP:
                    self.handle_keypress(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_click(event)

            self.update(delta)
            self.handle_interactions()
            self.clean_up()
            self.draw()

    def update(self, delta):
        # Refresh blackboard shared data
        BehaviorTree.board()[Blackboard.SOLDIERS] = self.soldiers
        BehaviorTree.board()[Blackboard.ARMIES] = self.armies

        for army in self.armies.values():
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

    def toggle_pause(self):
        self._paused = not self._paused

    def toggle_help(self):
        self._display_help = not self._display_help

    def draw(self):
        self.renderer.start_frame()

        for army in self.armies.values():
            army.draw(self.renderer)

        for soldier in self.soldiers.values():
            soldier.draw(self.renderer)

        self.renderer.end_frame()

    def set_mode(self, mode):
        self._mode = mode

    def handle_keypress(self, event):
        if event.key == pygame.K_h:
            self.toggle_help()
        if event.key == pygame.K_ESCAPE:
            self.set_mode(GameModes.WATCH)
        if event.key == pygame.K_SPACE or event.key == pygame.K_p:
            self.toggle_pause()
        if event.key == pygame.K_i:
            self.renderer.influence_enabled = not self.renderer.influence_enabled
        if event.key == pygame.K_t:
            self.renderer.tactics_enabled = not self.renderer.tactics_enabled
        if event.key == pygame.K_a:
            self.set_mode(GameModes.PLACE_ARMY)
        if event.key == pygame.K_f:
            self.set_mode(GameModes.PLACE_FORMATION)
        if event.key == pygame.K_s:
            self.set_mode(GameModes.PLACE_SOLDIER)
        if event.key == pygame.K_x or event.key == pygame.K_r:
            self.set_mode(GameModes.REMOVE)

    def handle_mouse_click(self, event):
        if event.button != 1:
            return
        if self._mode == GameModes.PLACE_ARMY:
            self.create_army(event.pos)
        if self._mode == GameModes.PLACE_FORMATION:
            self.active_army.add_formation(self.active_formation_type, event.pos.x, event.pos.y)
        if self._mode == GameModes.PLACE_SOLDIER:
            self.place_soldier(event.pos)
        if self._mode == GameModes.SET_ARMY_WAYPOINT:
            self.active_army.set_waypoint(event.pos.x, event.pos.y)
        if self._mode == GameModes.MOVE_FORMATION:
            self.active_formation.pos.x = event.pos[0]
            self.active_formation.pos.y = event.pos[1]
        if self._mode == GameModes.MOVE_FORMATION:
            self.remove_at(event.pos.x, event.pos.y)




if __name__ == "__main__":
    BT = Battles()
    BT.setup()
    BT.run()
