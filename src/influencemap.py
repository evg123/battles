"""
Code related to user interface
"""

import pygame
from scipy import signal


class InfluenceMap:

    GRID_RESOLUTION = 10

    FILTER = [
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1],
    ]

    def __init__(self, screen_size, soldiers, armies):
        self.screen_size = screen_size
        self.soldiers = soldiers
        self.armies = armies
        self._maps = self._blank_maps()

    def _blank_maps(self):
        self.rows = int(self.screen_size[1] // self.GRID_RESOLUTION)
        self.columns = int(self.screen_size[0] // self.GRID_RESOLUTION)

        new_maps = {}
        for army_id in self.armies.keys():
            new_maps[army_id] = [[0.0] * self.columns for _ in range(self.rows)]
        return new_maps

    def position_to_grid(self, position):
        row = int(position.y // self.GRID_RESOLUTION)
        col = int(position.x // self.GRID_RESOLUTION)
        return row, col

    def update(self):
        """Run the convolution to update the influence map"""
        self._update_maps()
        self._apply_convolution()

    def _update_maps(self):
        self._maps = self._blank_maps()
        for soldier in self.soldiers.values():
            row, col = self.position_to_grid(soldier.pos)
            for army_id, army_map in self._maps.items():
                # +1 for this army, -1 for an enemy
                influence_val = 1.0 if army_id is soldier.army.my_id else -1.0
                army_map[row][col] += influence_val

    def _apply_convolution(self):
        for base_map in self._maps.values():
            signal.convolve2d(base_map, self.FILTER, mode='same')

    def draw(self, renderer):
        """Draw the current influence map to the screen"""
        if not self._maps:
            return

        for row in range(self.rows):
            for col in range(self.columns):
                best = None
                influence = 0.0
                for army_id, army_map in self._maps.items():
                    if army_map[row][col] > influence:
                        influence = army_map[row][col]
                        best = army_id
                if best:
                    self._draw_army_influence_at(renderer, row, col, best, influence)

    def _draw_army_influence_at(self, renderer, row, col, army_id, influence):
        army_color = self.armies[army_id].color
        color = [min(int(part * influence), 100) for part in army_color]
        rect = pygame.Rect(row * self.GRID_RESOLUTION, col * self.GRID_RESOLUTION,
                           self.GRID_RESOLUTION, self.GRID_RESOLUTION)
        renderer.draw_rect(color, rect, 0)


