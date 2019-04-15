"""
Code related to user interface
"""

import pygame
import numpy
from scipy.ndimage import gaussian_filter


class InfluenceMap:
    """
    Updates and displays the influence map based on soldier positions
    """
    GRID_RESOLUTION = 25
    CONVOLUTION_SIGMA = 16
    MAX_INFLUENCE = 0.01
    MAX_INFLUENCE_ALPHA = 150

    def __init__(self, screen_size, soldiers, armies):
        self.screen_size = screen_size
        self.soldiers = soldiers
        self.armies = armies
        self._maps = self._blank_maps()

    def _blank_maps(self):
        """Create a blank set of maps, one for each army"""
        self.rows = int(self.screen_size[1] // self.GRID_RESOLUTION)
        self.columns = int(self.screen_size[0] // self.GRID_RESOLUTION)

        new_maps = {}
        for army_id in self.armies.keys():
            new_maps[army_id] = numpy.zeros((self.rows, self.columns))
        return new_maps

    def position_to_grid(self, position):
        """Find the grid square that this position falls in"""
        row = int(position.y // self.GRID_RESOLUTION)
        col = int(position.x // self.GRID_RESOLUTION)
        return row, col

    def update(self):
        """Run the convolution to update the influence map"""
        self._update_maps()
        self._apply_convolution()

    def _update_maps(self):
        """Update our maps based on the current position of the soldiers"""
        self._maps = self._blank_maps()
        for soldier in self.soldiers.values():
            if not soldier.is_alive():
                continue
            row, col = self.position_to_grid(soldier.pos)
            if row < 0 or row >= self.rows or col < 0 or col >= self.columns:
                # Out of bounds
                continue
            for army_id, army_map in self._maps.items():
                # +1 for this army, -1 for an enemy
                influence_val = 1.0 if army_id is soldier.army.my_id else -1.0
                army_map[row][col] += influence_val

    def _apply_convolution(self):
        """Apply the gaussian filter to the maps to spread out the influence"""
        for army_id, base_map in self._maps.items():
            self._maps[army_id] = gaussian_filter(base_map, sigma=self.CONVOLUTION_SIGMA,
                                                  mode="constant")

    def draw(self, renderer):
        """Draw the current influence map to the screen"""
        if not self._maps or not renderer.influence_enabled:
            return

        # Find the influence value for each square
        for row in range(self.rows):
            for col in range(self.columns):
                # Find which army has the highest influence here
                best = None
                influence = 0.0
                for army_id, army_map in self._maps.items():
                    if army_map[row][col] > influence:
                        # This is the new highest influence for this square
                        influence = army_map[row][col]
                        best = army_id
                if best is not None:
                    self._draw_army_influence_at(renderer, row, col, best, influence)

    def _draw_army_influence_at(self, renderer, row, col, army_id, influence):
        """Draw the square the proper color and translucency based on influence"""
        army_color = self.armies[army_id].color
        influence_percent = min(influence / self.MAX_INFLUENCE, 1.0)
        alpha = self.MAX_INFLUENCE_ALPHA * influence_percent
        rect = pygame.Rect(col * self.GRID_RESOLUTION, row * self.GRID_RESOLUTION,
                           self.GRID_RESOLUTION, self.GRID_RESOLUTION)
        renderer.draw_transparent_rect(army_color, rect, alpha)

