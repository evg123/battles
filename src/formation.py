"""
Class representing a formation of soldiers
"""
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
        self.formation_offset = Vector2.__new__(x_off, y_off)
        self.type = type
        self.soldier_id = self.EMPTY
        self.color = None

    def get_score_for_soldier(self, soldier):
        if self.soldier_id != self.EMPTY:
            return 0
        return soldier.slot_costs[self.type]

    def draw(self, renderer, formation_pos):
        if renderer.tactics_enabled:
            #TODO switch to drawing the slot type
            renderer.draw_text(self.color, formation_pos + self.formation_offset, self.FONT_SIZE, "X")


class Formation(Movable):

    ANCHOR_RADIUS = 2

    def __init__(self):
        super(Formation, self).__init__()
        self.army_offset = Vector2()
        self.slots = []
        self.color = Colors.black

    def set_color(self, color):
        self.color = color
        for slot in self.slots:
            slot.color = self.color

    def update(self, delta, army_pos):
        #TODO update max speed to match slowest unit
        destination = army_pos + self.army_offset
        self.reset_steering()
        BehaviorTree.aim(self, destination)
        BehaviorTree.arrive(self, destination)
        self.handle_steering(delta)

    def draw(self, renderer):
        if renderer.tactics_enabled:
            renderer.draw_circle(self.color, self.pos, self.ANCHOR_RADIUS)
        for slot in self.slots:
            slot.draw(renderer, self.pos)


class FormationLoader:

    EMPTY = 'X'
    SLOT_MAP = {
        'A': Slot.ANY,
        'F': Slot.FIGHTER,
        'R': Slot.RANGED,
    }
    SLOT_WIDTH = 20
    SLOT_HEIGHT = 20

    @staticmethod
    def file_path_from_name(name):
        return f"./formations/{name}.json"

    @staticmethod
    def offsets_from_coords(row, column, formation_width, formation_height):
        pixel_width = formation_width * FormationLoader.SLOT_WIDTH
        pixel_height = formation_height * FormationLoader.SLOT_HEIGHT
        x_off = column * FormationLoader.SLOT_WIDTH - pixel_width / 2
        y_off = row * FormationLoader.SLOT_HEIGHT - pixel_height / 2
        return x_off, y_off

    @staticmethod
    def load(formation_name):
        file_path = FormationLoader.file_path_from_name(formation_name)
        try:
            with open(file_path) as def_file:
                lines = def_file.readlines()
            formation = Formation()
            formation_width = max(lines, key=len)
            formation_height = len(lines)
            for row in range(len(lines)):
                line = lines[row]
                for column in range(len(line)):
                    orig_slot_char = line[column]
                    slot_char = orig_slot_char.upper()
                    if slot_char not in FormationLoader.SLOT_MAP:
                        raise InvalidFormation(f"Formation {formation_name} contains an invalid slot specifier: '{orig_slot_char}'")
                    if slot_char == ' ' or slot_char == FormationLoader.EMPTY:
                        # This space in the grid is not set to a role
                        continue
                    type = FormationLoader.SLOT_MAP[slot_char]
                    x_off, y_off = FormationLoader.offsets_from_coords(row, column, formation_width, formation_height)
                    slot = Slot(type, x_off, y_off)
                    formation.slots.append(slot)
            return formation
        except FileNotFoundError:
            raise InvalidFormation(f"Formation definition file not found: {file_path}")

