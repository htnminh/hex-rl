"""
This file uses some parts of the code implemented by Richard Baltrusch on
Sun Jan 23 14:07:18 2022 in the GitHub repository "pygame_examples" at
https://github.com/rbaltrusch/pygame_examples. Note that the repository
is licensed under the MIT License.
"""

from typing import List

import pygame
from pyg_hexagon import HexagonTile


class HexagonGrid:

    def create_hexagon(position, radius=25) -> HexagonTile:
        """Creates a hexagon tile at the specified position"""
        return HexagonTile(radius, position, colour=(220, 220, 220))
