"""
Class representing a formation of soldiers
"""
import os
import itertools
import copy
from pygame import Vector2
import src.util as util
from src.movable import Movable
from src.behavior import BehaviorTree
from src.graphics import Colors


class InvalidFormation(Exception):
    pass


class Slot:

    FONT_SIZE = 12
    ANY, FIGHTER, RANGED = range(3)

    def __init__(self, formation_type, x_off, y_off):
        self.formation_offset = Vector2(x_off, y_off)
        self.type = formation_type
        self.soldier = None
        self.color = None

    def get_score_for_soldier(self, soldier):
        if self.soldier:
            return None
        return soldier.slot_costs[self.type]

    def draw(self, renderer, formation_pos):
        if renderer.tactics_enabled:
            #TODO switch to drawing the slot type
            renderer.draw_text(self.color, formation_pos + self.formation_offset, self.FONT_SIZE, "X")

    def assign_soldier(self, soldier):
        self.soldier = soldier

    def clear_soldier(self):
        self.soldier = None


class Formation(Movable):

    ANCHOR_RADIUS = 6

    def __init__(self, name):
        super(Formation, self).__init__()
        self.name = name
        self.army_offset = Vector2()
        self.slots = []
        self.army = None
        self.valid = True  # Formations are invalidated while being moved

    def get_soldiers(self):
        return [slot.soldier for slot in self.slots if slot.soldier]

    def set_army(self, army):
        self.army = army
        self.max_velocity = army.max_velocity * 1.1
        self.max_rotation = army.max_rotation
        for slot in self.slots:
            slot.color = self.army.color

    def refresh_army_offset(self):
        self.army_offset.x = self.pos.x - self.army.pos.x
        self.army_offset.y = self.pos.y - self.army.pos.y

    def update(self, delta, army_pos):
        #TODO update max speed to match slowest unit
        #TODO or make march speed slower than any unit
        destination = army_pos + self.army_offset
        self.reset_steering()
        BehaviorTree.aim(self, destination)
        BehaviorTree.arrive(self, destination)
        self.handle_steering(delta)

    def draw(self, renderer, override_valid=False):
        if not self.valid and not override_valid:
            return
        if renderer.tactics_enabled:
            renderer.draw_circle(self.army.color, self.pos, self.ANCHOR_RADIUS)
        for slot in self.slots:
            slot.draw(renderer, self.pos)

    def add_soldier(self, soldier, snap_to_location=True):
        if self.assign_to_best_available_slot(soldier, snap_to_location):
            self.reassign()
            return True
        return False

    def assign_to_best_available_slot(self, soldier, snap_to_location):
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

    def remove_soldier(self, soldier_id):
        for slot in self.slots:
            if slot.soldier and slot.soldier.my_id == soldier_id:
                slot.clear_soldier()
        self.reassign()

    def anchor_overlaps(self, x_pos, y_pos):
        dist = util.distance(self.pos.x, self.pos.y, x_pos, y_pos)
        return dist <= self.ANCHOR_RADIUS

    def reassign(self):
        soldiers = []
        for slot in self.slots:
            if slot.soldier:
                soldiers.append(slot.soldier)
                slot.clear_soldier()
        soldiers.sort(key=lambda x: x.my_id)
        for soldier in soldiers:
            self.assign_to_best_available_slot(soldier, snap_to_location=False)

    def get_soldier_slot_position(self, soldier_id):
        if not self.valid:
            return None
        #TODO slots should be a dict of soldierid to slot
        for slot in self.slots:
            if slot.soldier and slot.soldier.my_id == soldier_id:
                pos = self.pos + slot.formation_offset
                return pos
        return None


class FormationLoader:

    FORMATION_DIRECTORY = os.path.normpath("./formations")

    EMPTY = 'X'
    SLOT_MAP = {
        'A': Slot.ANY,
        'F': Slot.FIGHTER,
        'R': Slot.RANGED,
    }
    SLOT_WIDTH = 20
    SLOT_HEIGHT = 20

    available_formations = {}
    formation_cycle = None

    @classmethod
    def get_next_template(cls):
        form = next(cls.formation_cycle)
        return copy.deepcopy(form)

    @classmethod
    def get_for_name(cls, formation_name):
        form = cls.available_formations[formation_name]
        return copy.deepcopy(form)

    @classmethod
    def find_formations(cls):
        for base_name in os.listdir(cls.FORMATION_DIRECTORY):
            form_file = os.path.join(cls.FORMATION_DIRECTORY, base_name)
            if not os.path.isfile(form_file):
                continue
            form = cls.load(form_file)
            cls.available_formations[base_name] = form
        if not cls.available_formations:
            raise FileNotFoundError(f"No formation files found in {cls.FORMATION_DIRECTORY}")
        cls.formation_cycle = itertools.cycle(cls.available_formations.values())

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
            formation = Formation(file_path)
            formation_width = len(max(lines, key=len))
            formation_height = len(lines)
            for row, line in enumerate(lines):
                for column, orig_slot_char in enumerate(line):
                    slot_char = orig_slot_char.upper()
                    if slot_char in (' ', '\n', FormationLoader.EMPTY):
                        # This space in the grid is not set to a role
                        continue
                    if slot_char not in FormationLoader.SLOT_MAP:
                        raise InvalidFormation(f"Formation file {file_path} contains an invalid "
                                               f"slot specifier: '{orig_slot_char}'")
                    form_type = FormationLoader.SLOT_MAP[slot_char]
                    x_off, y_off = FormationLoader.offsets_from_coords(row, column, formation_width,
                                                                       formation_height)
                    slot = Slot(form_type, x_off, y_off)
                    formation.slots.append(slot)
            return formation
        except FileNotFoundError:
            raise InvalidFormation(f"Formation definition file not found: {file_path}")

