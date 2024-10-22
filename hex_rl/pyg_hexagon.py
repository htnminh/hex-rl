"""
This file uses some parts of the code implemented by Richard Baltrusch on
Sun Jan 23 14:07:18 2022 in the GitHub repository "pygame_examples" at
https://github.com/rbaltrusch/pygame_examples. Note that the repository
is licensed under the MIT License.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List
from typing import Tuple
from pyg_utils import brighten_color

import pygame


@dataclass
class HexagonTile:
    """Hexagon class"""

    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...]
    highlight_offset: int = 5
    max_highlight_ticks: int = 10

    player = None


    def __post_init__(self):
        self.vertices = self.compute_vertices()
        self.highlight_tick = 0


    def update(self):
        """Updates tile highlights"""
        if self.highlight_tick > 0:
            self.highlight_tick -= 1


    def compute_vertices(self) -> List[Tuple[float, float]]:
        """
        Returns a list of the hexagon's vertices as x, y tuples
            0
        1       5

        2       4
            3
        """
        # pylint: disable=invalid-name
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (x, y),
            (x - minimal_radius, y + half_radius),
            (x - minimal_radius, y + 3 * half_radius),
            (x, y + 2 * self.radius),
            (x + minimal_radius, y + 3 * half_radius),
            (x + minimal_radius, y + half_radius),
        ]
    

    def compute_neighbours(self, hexagons: List[HexagonTile]) -> List[HexagonTile]:
        """Returns hexagons whose centres are two minimal radiuses away from self.centre"""
        # could cache results for performance
        return [hexagon for hexagon in hexagons if self.is_neighbour(hexagon)]


    def collide_with_point(self, point: Tuple[float, float]) -> bool:
        """Returns True if distance from centre to point is less than horizontal_length"""
        return math.dist(point, self.centre) < self.minimal_radius
    

    def is_neighbour(self, hexagon: HexagonTile) -> bool:
        """Returns True if hexagon centre is approximately
        2 minimal radiuses away from own centre
        """
        distance = math.dist(hexagon.centre, self.centre)
        return math.isclose(distance, 2 * self.minimal_radius, rel_tol=0.05)


    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""
        pygame.draw.polygon(screen, self.highlight_colour, self.vertices)
        pygame.draw.aalines(screen, (0, 0, 0), closed=True, points=self.vertices)
        x, y = self.centre
        if self.player == 1:
            pygame.draw.circle(screen, (255, 0, 0), (x+0.75, y+0.75), 0.7 * self.radius)
        elif self.player == -1:
            pygame.draw.circle(screen, (0, 0, 255), (x+0.75, y+0.75), 0.7 * self.radius)


    def render_highlight(self) -> None:
        self.highlight_tick = self.max_highlight_ticks
        

    def play(self, player) -> None:
        if self.player is None:
            self.player = player
        else:
            raise ValueError("Invalid action")  # TODO: define an exception
        
    
    def mark_winner_group(self, screen) -> None:
        x, y = self.centre
        pygame.draw.circle(screen, (255, 255, 255), (x+0.75, y+0.75), 0.2 * self.radius)


    @property
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position  # pylint: disable=invalid-name
        return (x, y + self.radius)

    @property
    def minimal_radius(self) -> float:
        """Horizontal length of the hexagon"""
        # https://en.wikipedia.org/wiki/Hexagon#Parameters
        return self.radius * math.cos(math.radians(30))

    @property
    def highlight_colour(self) -> Tuple[int, ...]:
        """Colour of the hexagon tile when rendering highlight"""
        offset = self.highlight_offset * self.highlight_tick
        return brighten_color(self.colour, offset)

