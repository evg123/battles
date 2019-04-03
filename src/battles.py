"""
Main class with game loop
"""
import itertools
import copy
import pygame
from src.util import FrameTimer
from src.graphics import Renderer, Colors
from src.ui import Ui
from src.army import Army
from src.soldier import Soldier, Swordsperson, Archer, SoldierLoader
from src.behavior import BehaviorTree, Blackboard
from src.formation import FormationLoader, Formation


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

    SOLDIER_TYPES = (Swordsperson, Archer)

    def __init__(self):
        pygame.init()
        self.renderer = Renderer(self.WINDOW_TITLE, self.SCREEN_SIZE)
        self.ui = Ui(self.renderer)
        self._running = True
        self._paused = False
        self._mode = GameModes.WATCH
        self._display_help = False
        self.armies = {}
        self.soldiers = {}
        self.buttons = []
        self.active_army = None
        self.active_formation = None
        self.active_soldier = None
        FormationLoader.find_formations()
        self.formation_types = itertools.cycle(FormationLoader.available_formations)
        self.active_formation_template = FormationLoader.get_next_template()
        self.active_soldier_type = SoldierLoader.get_next_type()

    def create_army(self, position):
        army = Army()
        army.pos.x = army.waypoint.x = position[0]
        army.pos.y = army.waypoint.y = position[1]
        self.armies[army.my_id] = army
        self.active_army = army
        return army

    def create_soldier(self, soldier_class, make_active=True):
        soldier = soldier_class()
        if make_active:
            self.soldiers[soldier.my_id] = soldier
        return soldier

    def setup(self):
        # Left Army
        army = self.create_army((200, 350))
        army.add_formation(FormationLoader.get_for_name("basic_1"), 150, 300)
        army.add_formation(FormationLoader.get_for_name("basic_1"), 200, 400)

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
        army.add_formation(FormationLoader.get_for_name("basic_1"), 1080, 200)
        army.add_formation(FormationLoader.get_for_name("basic_1"), 1080, 350)
        army.add_formation(FormationLoader.get_for_name("basic_1"), 1080, 500)

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

        self.ui.draw()
        self.draw_cursor()

        self.renderer.end_frame()

    def draw_cursor(self):
        cursor_pos = pygame.mouse.get_pos()
        if self._mode == GameModes.PLACE_ARMY:
            self.renderer.draw_circle(Army.next_color(), cursor_pos, Army.ANCHOR_RADIUS)
        if self._mode == GameModes.SET_ARMY_WAYPOINT:
            self.renderer.draw_line(self.active_army.color, self.active_army.pos, cursor_pos)
            self.renderer.draw_circle(self.active_army.color, cursor_pos, Army.WAYPOINT_RADIUS)
        elif self.active_formation:
            self.active_formation.pos.x = cursor_pos[0]
            self.active_formation.pos.y = cursor_pos[1]
            self.active_formation.draw(self.renderer) #TODO don't double draw if moving a placed formation
        elif self.active_soldier:
            self.active_soldier.pos.x = cursor_pos[0]
            self.active_soldier.pos.y = cursor_pos[1]
            self.active_soldier.draw(self.renderer)

    def reset_mode_attrs(self):
        self.active_soldier = None
        self.active_formation = None

    def set_mode(self, mode):
        mode_changed = mode != self._mode
        if mode == GameModes.WATCH:
            self.reset_mode_attrs()
        elif mode == GameModes.PLACE_SOLDIER:
            if not mode_changed:
                self.active_soldier_type = SoldierLoader.get_next_type()
            self.active_soldier = self.create_soldier(self.active_soldier_type, False)
        elif mode == GameModes.PLACE_FORMATION:
            if not mode_changed:
                self.active_formation_template = FormationLoader.get_next_template()
            self.active_formation = copy.deepcopy(self.active_formation_template)
            self.active_army.add_formation(self.active_formation, 0, 0)

        self._mode = mode

    def remove_army(self, army_id):
        sldr_ids_to_remove = [sldr.my_id for sldr in self.soldiers if sldr.army.my_id == army_id]
        for soldier_id in sldr_ids_to_remove:
            del self.soldiers[soldier_id]
        del self.armies[army_id]

    def remove_soldier(self, soldier_id):
        soldier = self.soldiers[soldier_id]
        soldier.cleanup()
        del self.soldiers[soldier_id]

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

        if self.ui.handle_click(event.pos[0], event.pos[1]):
            # The click was consumed by the UI
            return

        if self._mode == GameModes.WATCH:
            self.activate_at_pos(event.pos[0], event.pos[1])
        elif self._mode == GameModes.PLACE_ARMY:
            self.create_army(event.pos)
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.PLACE_FORMATION:
            self.active_army.add_formation(self.active_formation, event.pos[0], event.pos[1])
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.PLACE_SOLDIER:
            self.place_soldier(event.pos[0], event.pos[1])
            self.set_mode(GameModes.PLACE_SOLDIER)
        elif self._mode == GameModes.SET_ARMY_WAYPOINT:
            self.active_army.set_waypoint(event.pos[0], event.pos[1])
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.MOVE_FORMATION:
            self.active_formation.pos.x = event.pos[0]
            self.active_formation.pos.y = event.pos[1]
            self.active_formation.refresh_army_offset()
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.MOVE_FORMATION:
            self.remove_at_pos(event.pos[0], event.pos[1])

    def get_at_pos(self, x_pos, y_pos):
        for army in self.armies.values():
            if army.anchor_overlaps(x_pos, y_pos):
                return army
            for formation in army.formations:
                if formation.anchor_overlaps(x_pos, y_pos):
                    return formation
        for soldier in self.soldiers.values():
            if soldier.overlaps(x_pos, y_pos):
                return soldier
        return None

    def activate_at_pos(self, x_pos, y_pos):
        obj = self.get_at_pos(x_pos, y_pos)
        if not obj:
            return False
        if isinstance(obj, Army):
            self.active_army = obj
            self.set_mode(GameModes.SET_ARMY_WAYPOINT)
            return True
        if isinstance(obj, Formation):
            self.active_formation = obj
            self.set_mode(GameModes.MOVE_FORMATION)
            return True
        return False

    def remove_at_pos(self, x_pos, y_pos):
        obj = self.get_at_pos(x_pos, y_pos)
        if not obj:
            return False
        if isinstance(obj, Army):
            self.remove_army(obj.my_id)
            return True
        if isinstance(obj, Formation):
            obj.army.remove_formation(obj)
            return True
        if isinstance(obj, Soldier):
            self.remove_soldier(obj.my_id)
            return False
        return False

    def place_soldier(self, x_pos, y_pos):
        obj = self.get_at_pos(x_pos, y_pos)
        if obj and isinstance(obj, Formation) and obj.army == self.active_army:
            obj.add_soldier(self.active_soldier)
            self.soldiers[self.active_soldier.my_id] = self.active_soldier
            self.active_soldier = None


if __name__ == "__main__":
    BT = Battles()
    BT.setup()
    BT.run()
