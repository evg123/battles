"""
Class representing a formation of soldiers
"""
import os
from pygame import Vector2
from src.movable import Movable
from src.behavior import BehaviorTree
from src.graphics import Colors


class InvalidFormation(Exception):
    pass


class Slot:

    FONT_SIZE = 12
    ANY, FIGHTER, RANGED = range(3)
    EMPTY = 0

    def __init__(self, type, x_off, y_off):
        self.formation_offset = Vector2(x_off, y_off)
        self.type = type
        self.soldier_id = self.EMPTY
        self.color = None

    def get_score_for_soldier(self, soldier):
        if self.soldier_id != self.EMPTY:
            return None
        return soldier.slot_costs[self.type]

    def draw(self, renderer, formation_pos):
        if renderer.tactics_enabled:
            #TODO switch to drawing the slot type
            renderer.draw_text(self.color, formation_pos + self.formation_offset, self.FONT_SIZE, "X")

    def assign_soldier(self, soldier):
        self.soldier_id = soldier.my_id


class Formation(Movable):

    ANCHOR_RADIUS = 2

    def __init__(self):
        super(Formation, self).__init__()
        self.army_offset = Vector2()
        self.slots = []
        self.army = None

    def set_army(self, army):
        self.army = army
        self.max_velocity = army.max_velocity * 1.1
        self.max_rotation = army.max_rotation
        for slot in self.slots:
            slot.color = self.army.color

    def update(self, delta, army_pos):
        #TODO update max speed to match slowest unit
        #TODO or make march speed slower than any unit
        destination = army_pos + self.army_offset
        self.reset_steering()
        BehaviorTree.aim(self, destination)
        BehaviorTree.arrive(self, destination)
        self.handle_steering(delta)

    def draw(self, renderer):
        if renderer.tactics_enabled:
            renderer.draw_circle(self.army.color, self.pos, self.ANCHOR_RADIUS)
        for slot in self.slots:
            slot.draw(renderer, self.pos)

    def add_soldier(self, soldier, snap_to_location=True):
        best_slot = None
        best_score = float("inf")
        for slot in self.slots:
            score = slot.get_score_for_soldier(soldier)
            if score is not None and score < best_score:
                best_slot = slot
                best_score = score
        if best_slot is not None:
            best_slot.assign_soldier(soldier)
            soldier.formation = self
            soldier.army = self.army
            if snap_to_location:
                soldier.set_position_vec(self.pos + best_slot.formation_offset)
            return True
        return False


class FormationLoader:

    FORMATION_DIRECTORY = "./formations"

    EMPTY = 'X'
    SLOT_MAP = {
        'A': Slot.ANY,
        'F': Slot.FIGHTER,
        'R': Slot.RANGED,
    }
    SLOT_WIDTH = 20
    SLOT_HEIGHT = 20

    available_formations = []

    @classmethod
    def find_formations(cls):
        for form_file in os.listdir(cls.FORMATION_DIRECTORY):
            if not os.path.isfile(form_file):
                continue
            form = cls.load(form_file)
            cls.available_formations.append(form)
        if not cls.available_formations:
            raise FileNotFoundError(f"No formation files found in {cls.FORMATION_DIRECTORY}")

    @staticmethod
    def offsets_from_coords(row, column, formation_width, formation_height):
        pixel_width = formation_width * FormationLoader.SLOT_WIDTH
        pixel_height = formation_height * FormationLoader.SLOT_HEIGHT
        x_off = column * FormationLoader.SLOT_WIDTH - pixel_width // 2
        y_off = row * FormationLoader.SLOT_HEIGHT - pixel_height // 2
        return x_off, y_off

    @staticmethod
    def load(file_path):
        try:
            with open(file_path) as def_file:
                lines = def_file.readlines()
            formation = Formation()
            formation_width = len(max(lines, key=len))
            formation_height = len(lines)
            for row in range(len(lines)):
                line = lines[row]
                for column in range(len(line)):
                    orig_slot_char = line[column]
                    slot_char = orig_slot_char.upper()
                    if slot_char == ' ' or slot_char == '\n' or slot_char == FormationLoader.EMPTY:
                        # This space in the grid is not set to a role
                        continue
                    if slot_char not in FormationLoader.SLOT_MAP:
                        raise InvalidFormation(f"Formation file {file_path} contains an invalid slot specifier: '{orig_slot_char}'")
                    type = FormationLoader.SLOT_MAP[slot_char]
                    x_off, y_off = FormationLoader.offsets_from_coords(row, column, formation_width, formation_height)
                    slot = Slot(type, x_off, y_off)
                    formation.slots.append(slot)
            return formation
        except FileNotFoundError:
            raise InvalidFormation(f"Formation definition file not found: {file_path}")

