"""
This file uses some parts of the code implemented by Richard Baltrusch on
Sun Jan 23 14:07:18 2022 in the GitHub repository "pygame_examples" at
https://github.com/rbaltrusch/pygame_examples. Note that the repository
is licensed under the MIT License.
"""

from typing import List, Optional
from dataclasses import dataclass
from itertools import chain
from hex import Hex

# import pprint

import pygame
from pyg_hexagon import HexagonTile


@dataclass
class HexagonGrid:
    n_rows_and_cols: Optional[int] = 11

    radius = 25
    colour = (220, 220, 220)
    init_position = (50, 25)
    screen_fill_colour = (200, 200, 200)
    

    def __post_init__(self):
        """Initializes properties that need calculations (or not constants)"""
        self._minimal_radius = HexagonTile(
            radius=self.radius, position=(0,0), colour=(0,0,0)).minimal_radius
        self.screen_size = (
            3   * self._minimal_radius * self.n_rows_and_cols + 50,
            1.5 * self.radius          * self.n_rows_and_cols + 75
        )

        
    def init_hexagons(self) -> List[List[HexagonTile]]:
        """Creates a hexaogonal tile map of size num_x * num_y"""
        hexagon_row = []
        hexagons = []
        for i in range(self.n_rows_and_cols):
            if i == 0:
                leftmost_hexagon = HexagonTile(
                    radius=self.radius, position=self.init_position, colour=self.colour)
            else:
                position = leftmost_hexagon.vertices[4]
                leftmost_hexagon = HexagonTile(
                    radius=self.radius, position=position, colour=self.colour)
            hexagon_row.append(leftmost_hexagon)

            # place hexagons to the left of leftmost hexagon, with equal y-values.
            hexagon = leftmost_hexagon
            for j in range(1, self.n_rows_and_cols):
                x, y = hexagon.position  # type: ignore
                hexagon = HexagonTile(
                    radius=self.radius,
                    position=(x + hexagon.minimal_radius * 2, y),
                    colour=self.colour
                )
                hexagon_row.append(hexagon)

            hexagons.append(hexagon_row)
            hexagon_row = []

            # print("i:", i)
            # pprint.pprint(hexagons)

        return hexagons


    @staticmethod
    def _flatten_hexagons(hexagons: List[List[HexagonTile]]) -> List[HexagonTile]:
        """Flattens a list of lists of hexagons"""
        return list(chain.from_iterable(hexagons))


    def render(self, screen, hexagons):
        """Renders hexagons on the screen"""
        screen.fill(self.screen_fill_colour)
        for hexagon in self._flatten_hexagons(hexagons):
            hexagon.render(screen)

        # draw borders around colliding hexagons and neighbours
        mouse_pos = pygame.mouse.get_pos()
        colliding_hexagons = [
            hexagon for hexagon in self._flatten_hexagons(hexagons)
                        if hexagon.collide_with_point(mouse_pos)
        ]
        for hexagon in colliding_hexagons:
            for neighbour in hexagon.compute_neighbours(self._flatten_hexagons(hexagons)):
                neighbour.render_highlight()
            hexagon.render_highlight()
        pygame.display.flip()

    
    def main(self):
        """Main function"""
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        clock = pygame.time.Clock()
        hexagons = self.init_hexagons()
        # pprint.pprint(hexagons)
        terminated = False

        # TODO: add core game here. check duplicate code with cli.
        hex = Hex(size=self.n_rows_and_cols, rich_exceptions=False)
        player = hex.player

        while not terminated:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminated = True

                if event.type == pygame.MOUSEBUTTONUP:
                    for i, hexagon_row in enumerate(hexagons):
                        for j, hexagon in enumerate(hexagon_row):
                            if hexagon.collide_with_point(pygame.mouse.get_pos()):
                                try:
                                    hex.play((i, j))
                                    hexagon.play(player)
                                except Exception as e:
                                    print(e)
                                player = hex.player
                                break

            for hexagon in self._flatten_hexagons(hexagons):
                hexagon.update()

            self.render(screen, hexagons)
            clock.tick(60)  # max fps
        pygame.display.quit()


if __name__ == "__main__":
    HexagonGrid().main()


