"""
Main class with game loop
"""
import itertools
import copy
import pygame
from src.util import FrameTimer
from src.graphics import Renderer, Colors
from src.ui import Ui, Button
from src.army import Army
from src.soldier import Soldier, Swordsperson, Archer, SoldierLoader
from src.behavior import BehaviorTree, Blackboard
from src.formation import FormationLoader, Formation
from src.influence import InfluenceMap


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

    DEBUG = True

    WINDOW_TITLE = "Battle Demo"
    SCREEN_SIZE = (1800, 1000)
    BUTTON_SIZE = (100, 60)
    HELP_BOX_SIZE = (500, 800)

    SOLDIER_TYPES = (Swordsperson, Archer)

    def __init__(self):
        pygame.init()
        self.renderer = Renderer(self.WINDOW_TITLE, self.SCREEN_SIZE)
        self.ui = Ui(self.renderer)
        self._running = True
        self._paused = False
        self._mode = GameModes.WATCH
        self.help_box = None
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
        self.influence_map = InfluenceMap(self.SCREEN_SIZE, self.soldiers, self.armies)

    def create_army(self, position):
        try:
            army = Army()
        except RuntimeError:
            return None
        army.set_position(position[0], position[1])
        army.waypoint.x = position[0]
        army.waypoint.y = position[1]
        self.armies[army.my_id] = army
        self.active_army = army
        return army

    def create_soldier(self, soldier_class, make_active=True):
        soldier = soldier_class()
        if make_active:
            self.soldiers[soldier.my_id] = soldier
        soldier.army = self.active_army
        return soldier

    def create_ui(self):
        self.ui.add_button("Army", self.BUTTON_SIZE, self.set_mode, args=(GameModes.PLACE_ARMY,))
        self.ui.add_button("Formation", self.BUTTON_SIZE, self.set_mode, args=(GameModes.PLACE_FORMATION,))
        self.ui.add_button("Soldier", self.BUTTON_SIZE, self.set_mode, args=(GameModes.PLACE_SOLDIER,))
        self.ui.add_button("Remove", self.BUTTON_SIZE, self.set_mode, args=(GameModes.REMOVE,))

        self.ui.add_button("Influence", self.BUTTON_SIZE, self.toggle_influence)
        self.ui.add_button("Tactics", self.BUTTON_SIZE, self.toggle_tactics)

        self.ui.add_button("Help", self.BUTTON_SIZE, self.toggle_help)
        self.ui.add_button("Clear", self.BUTTON_SIZE, self.blank_slate)

        self.help_box = self.ui.add_button(self.help_text(), self.HELP_BOX_SIZE, None,
                                           centered=True, display=False)

    def setup(self, create_default_army):
        self.create_ui()

        if create_default_army:
            self.create_default_army()

    def run(self):
        frame_timer = FrameTimer()

        while self._running:
            delta = frame_timer.next_frame()
            if self.DEBUG:
                frame_timer.print_fps()

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

        print("Quitting")

    def update(self, delta):
        # Refresh blackboard shared data
        BehaviorTree.board()[Blackboard.SOLDIERS] = self.soldiers
        BehaviorTree.board()[Blackboard.ARMIES] = self.armies

        for army in self.armies.values():
            army.update(delta)

        for soldier in self.soldiers.values():
            soldier.update(delta)

        self.influence_map.update()

    def handle_interactions(self):
        #TODO optimize
        for soldier1 in self.soldiers.values():
            for soldier2 in self.soldiers.values():
                if soldier1 == soldier2:
                    continue
                soldier1.interact(soldier2)

    def clean_up(self):
        # Take dead soldiers out of their formations
        dead = [soldier for soldier in self.soldiers.values() if not soldier.is_alive()]
        for soldier in dead:
            soldier.formation.remove_soldier(soldier.my_id)

        # Remove fully gone soldiers
        remove_ids = [soldier.my_id for soldier in dead if soldier.needs_removal()]
        for soldier_id in remove_ids:
            self.remove_soldier(soldier_id)

    def blank_slate(self):
        self.armies.clear()
        self.soldiers.clear()
        Army.next_id = 0
        Soldier.next_id = 0

    def toggle_pause(self):
        self._paused = not self._paused

    def toggle_help(self):
        self.help_box.toggle_display()

    def toggle_influence(self):
        self.renderer.influence_enabled = not self.renderer.influence_enabled

    def toggle_tactics(self):
        self.renderer.tactics_enabled = not self.renderer.tactics_enabled

    def draw(self):
        self.renderer.start_frame()

        self.influence_map.draw(self.renderer)

        for soldier in self.soldiers.values():
            soldier.draw(self.renderer)

        for army in self.armies.values():
            army.draw(self.renderer)

        self.ui.draw()
        self.draw_cursor()

        self.renderer.end_frame()

    def draw_cursor(self):
        cursor_pos = pygame.mouse.get_pos()
        if self._mode == GameModes.PLACE_ARMY:
            try:
                self.renderer.draw_circle(Army.next_color(), cursor_pos, Army.ANCHOR_RADIUS)
            except RuntimeError:
                return
        elif self._mode == GameModes.SET_ARMY_WAYPOINT:
            self.renderer.draw_line(self.active_army.color, self.active_army.pos, cursor_pos)
            self.renderer.draw_circle(self.active_army.color, cursor_pos, Army.WAYPOINT_RADIUS)
        elif self._mode == GameModes.REMOVE:
            self.renderer.draw_x(Colors.red, cursor_pos, radius=7, width=2)
        elif self.active_formation:
            self.active_formation.set_position(cursor_pos[0], cursor_pos[1])
            self.active_formation.draw(self.renderer, override_valid=True)
        elif self.active_soldier:
            self.active_soldier.set_position(cursor_pos[0], cursor_pos[1])
            self.active_soldier.draw(self.renderer)

    def reset_mode_attrs(self):
        self.active_soldier = None
        self.active_formation = None

    def set_mode(self, mode):
        mode_changed = mode != self._mode
        if mode == GameModes.WATCH:
            self.reset_mode_attrs()
        if mode == GameModes.PLACE_ARMY:
            self.reset_mode_attrs()
        elif mode == GameModes.PLACE_SOLDIER:
            self.refresh_active_soldier()
        elif mode == GameModes.PLACE_FORMATION:
            self.refresh_active_formation()

        self._mode = mode

    def refresh_active_soldier(self):
        if not self.active_soldier or not isinstance(self.active_soldier, self.active_soldier_type):
            self.active_soldier = self.create_soldier(self.active_soldier_type, False)

    def refresh_active_formation(self):
        if not self.active_formation or not self.active_formation.name == self.active_formation_template.name:
            self.active_formation = copy.deepcopy(self.active_formation_template)
            self.active_formation.set_army(self.active_army)

    def cycle_soldier_type(self):
        self.active_soldier_type = SoldierLoader.get_next_type()
        self.refresh_active_soldier()

    def cycle_formation_type(self):
        self.active_formation_template = FormationLoader.get_next_template()
        self.refresh_active_formation()

    def remove_army(self, army_id):
        sldr_ids_to_remove = [sldr.my_id for sldr in self.soldiers.values() if sldr.army.my_id == army_id]
        for soldier_id in sldr_ids_to_remove:
            del self.soldiers[soldier_id]
        del self.armies[army_id]

    def remove_soldier(self, soldier_id):
        soldier = self.soldiers[soldier_id]
        soldier.cleanup()
        del self.soldiers[soldier_id]

    def handle_keypress(self, event):
        if event.key == pygame.K_q:
            self._running = False
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
            if self._mode == GameModes.PLACE_FORMATION:
                self.cycle_formation_type()
            else:
                self.set_mode(GameModes.PLACE_FORMATION)
        if event.key == pygame.K_s:
            if self._mode == GameModes.PLACE_SOLDIER:
                self.cycle_soldier_type()
            else:
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
            if self.place_soldier(event.pos[0], event.pos[1]):
                self.set_mode(GameModes.PLACE_SOLDIER)
        elif self._mode == GameModes.SET_ARMY_WAYPOINT:
            self.active_army.set_waypoint(event.pos[0], event.pos[1])
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.MOVE_FORMATION:
            self.active_formation.set_position(event.pos[0], event.pos[1])
            self.active_formation.refresh_army_offset()
            self.active_formation.valid = True
            self.set_mode(GameModes.WATCH)
        elif self._mode == GameModes.REMOVE:
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
            self.active_formation.valid = False
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
            soldiers = obj.get_soldiers()
            obj.army.remove_formation(obj)
            for soldier in soldiers:
                self.remove_soldier(soldier.my_id)
            obj.army.remove_formation(obj)
            return True
        if isinstance(obj, Soldier):
            self.remove_soldier(obj.my_id)
            return False
        return False

    def place_soldier(self, x_pos, y_pos):
        obj = self.get_at_pos(x_pos, y_pos)
        if obj and isinstance(obj, Formation) and obj.army == self.active_army:
            if obj.add_soldier(self.active_soldier):
                self.soldiers[self.active_soldier.my_id] = self.active_soldier
                self.active_soldier = None
                return True
        return False

    def help_text(self):
        return [
            "line 1",
            "line 2 - asdf",
            "line 3",
        ]

    def create_default_army(self):
        # Left Army
        army = self.create_army((200, 500))
        army.add_formation(FormationLoader.get_for_name("1_box"), 200, 350)
        army.add_formation(FormationLoader.get_for_name("1_box"), 200, 650)

        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
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
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))

        # Right Army
        army = self.create_army((1500, 500))
        army.add_formation(FormationLoader.get_for_name("1_box"), 1500, 350)
        army.add_formation(FormationLoader.get_for_name("1_box"), 1500, 650)

        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
        army.formations[0].add_soldier(self.create_soldier(Swordsperson))
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
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Swordsperson))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))
        army.formations[1].add_soldier(self.create_soldier(Archer))


if __name__ == "__main__":
    BT = Battles()
    BT.setup(True)
    BT.run()
