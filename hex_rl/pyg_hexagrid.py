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
import datetime
from pathlib import Path
from pyg_button import Button
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
    caption = 'Hex RL by @htnminh'
    

    def __post_init__(self):
        """Initializes properties that need calculations (or not constants)"""
        self._minimal_radius = HexagonTile(
            radius=self.radius, position=(0,0), colour=(0,0,0)).minimal_radius
        self.screen_size = (
            3   * self._minimal_radius * self.n_rows_and_cols + self.radius * 2,
            1.5 * self.radius          * self.n_rows_and_cols + self.radius * 3 + 50
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

        # draw colored edges
        mid = lambda x, y: ((x[0] + y[0]) / 2, (x[1] + y[1]) / 2)
        upper_right_mid = mid(
            hexagons[0][self.n_rows_and_cols - 1].vertices[5],
            hexagons[0][self.n_rows_and_cols - 1].vertices[0])
        lower_left_mid = mid(
            hexagons[self.n_rows_and_cols - 1][0].vertices[2],
            hexagons[self.n_rows_and_cols - 1][0].vertices[3])
        pygame.draw.aalines(screen, (255, 0, 0), closed=False, points=
            [hexagons[0][j].vertices[k]
                for j in range(self.n_rows_and_cols - 1)
                for k in [1, 0, 5]]
            + [hexagons[0][self.n_rows_and_cols - 1].vertices[0]]
            + [upper_right_mid]
        )
        pygame.draw.aalines(screen, (0, 0, 255), closed=False, points=
            [upper_right_mid]
            + [hexagons[0][self.n_rows_and_cols - 1].vertices[5]]
            + [hexagons[i][self.n_rows_and_cols - 1].vertices[k]
                for i in range(1, self.n_rows_and_cols)
                for k in [0, 5, 4]
            ]
        )
        pygame.draw.aalines(screen, (0, 0, 255), closed=False, points=
            [hexagons[i][0].vertices[k]
                for i in range(0, self.n_rows_and_cols - 1)
                for k in [1, 2, 3]] 
            + [hexagons[self.n_rows_and_cols - 1][0].vertices[2]]
            + [lower_left_mid]
        )
        pygame.draw.aalines(screen, (255, 0, 0), closed=False, points=
            [lower_left_mid]
            + [hexagons[self.n_rows_and_cols - 1][0].vertices[3]]
            + [hexagons[self.n_rows_and_cols - 1][j].vertices[k]
                for j in range(1, self.n_rows_and_cols)
                for k in [2, 3, 4]]
        )
        
        # buttons
        buttons = []

        reset_button = Button(60, self.screen_size[1] - 45, text="Reset")
        buttons.append(reset_button)

        screenshot_button = Button(180, self.screen_size[1] - 45, text="Screenshot")
        buttons.append(screenshot_button)

        for button in buttons:
            button.render(screen)


        pygame.display.flip()

    
    def main(self):
        """Main function"""
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(self.caption)
        clock = pygame.time.Clock()
        hexagons = self.init_hexagons()
        # pprint.pprint(hexagons)
        terminated = False

        hex = Hex(size=self.n_rows_and_cols, rich_exceptions=False)
        player = hex.player

        while not terminated:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    # TODO: remove this test of capturing the screen
                    time_str = str(datetime.datetime.now().strftime('%Y %m %d'))  # %H %M %S
                    Path('hex_rl/screenshots').mkdir(parents=True, exist_ok=True)
                    pygame.image.save(screen, f'hex_rl/screenshots/{time_str}.png')

                    terminated = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # left click
                    
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


