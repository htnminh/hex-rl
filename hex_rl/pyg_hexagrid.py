"""
This file uses some parts of the code implemented by Richard Baltrusch on
Sun Jan 23 14:07:18 2022 in the GitHub repository "pygame_examples" at
https://github.com/rbaltrusch/pygame_examples. Note that the repository
is licensed under the MIT License.
"""

from typing import List
from dataclasses import dataclass

import pygame
from pyg_hexagon import HexagonTile


@dataclass
class HexagonGrid:
    radius = 25
    colour = (220, 220, 220)
    init_position = (50, 25)
    n_rows_and_cols = 7
    screen_fill_colour = (200, 200, 200)
    # screen_size = (1175+5, 700)
    _minimal_radius = HexagonTile(radius=radius, position=(0,0), colour=(0,0,0)).minimal_radius
    screen_size = (
        3 * _minimal_radius * n_rows_and_cols + 50,
        1.5 * radius * n_rows_and_cols + 75)



    def init_hexagons(self) -> List[HexagonTile]:
        """Creates a hexaogonal tile map of size num_x * num_y"""
        # pylint: disable=invalid-name
        leftmost_hexagon = HexagonTile(
            radius=self.radius, position=self.init_position, colour=self.colour)
        hexagons = [leftmost_hexagon]
        for x in range(self.n_rows_and_cols):
            if x:
                # alternate between bottom left and bottom right vertices of hexagon above
                # index = 2 if x % 2 == 1 or flat_top else 4
                index = 4
                position = leftmost_hexagon.vertices[index]
                leftmost_hexagon = HexagonTile(
                    radius=self.radius, position=position, colour=self.colour)
                hexagons.append(leftmost_hexagon)

            # place hexagons to the left of leftmost hexagon, with equal y-values.
            hexagon = leftmost_hexagon
            for i in range(self.n_rows_and_cols - 1):
                x_coord, y_coord = hexagon.position  # type: ignore
                hexagon = HexagonTile(
                    radius=self.radius,
                    position=(x_coord + hexagon.minimal_radius * 2, y_coord),
                    colour=self.colour
                )
                hexagons.append(hexagon)

        return hexagons


    def render(self, screen, hexagons):
        """Renders hexagons on the screen"""
        screen.fill(self.screen_fill_colour)
        for hexagon in hexagons:
            hexagon.render(screen)

        # draw borders around colliding hexagons and neighbours
        mouse_pos = pygame.mouse.get_pos()
        colliding_hexagons = [
            hexagon for hexagon in hexagons if hexagon.collide_with_point(mouse_pos)
        ]
        for hexagon in colliding_hexagons:
            for neighbour in hexagon.compute_neighbours(hexagons):
                neighbour.render_highlight(screen, border_colour=(100, 100, 100))
            hexagon.render_highlight(screen, border_colour=(0, 0, 0))
        pygame.display.flip()

    
    def main(self):
        """Main function"""
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        clock = pygame.time.Clock()
        hexagons = self.init_hexagons()
        terminated = False

        while not terminated:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminated = True

            for hexagon in hexagons:
                hexagon.update()

            self.render(screen, hexagons)
            clock.tick(60)  # max fps
        pygame.display.quit()


if __name__ == "__main__":
    HexagonGrid().main()


