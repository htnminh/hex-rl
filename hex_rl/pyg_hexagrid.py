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
from pyg_button import Button, TextButton
# import pprint

import pygame
from pyg_hexagon import HexagonTile
from model_random import RandomModel


@dataclass
class HexagonGrid:
    size: Optional[int] = 11
    mode: Optional[str] = "pvp"
    agent: Optional[str] = "random"

    radius = 25
    colour = (220, 220, 220)
    init_position = (50, 25)
    screen_fill_colour = (220, 220, 220)
    caption = 'Hex RL by @htnminh'
    color_edge_width = 2
    

    def __post_init__(self):
        """Initializes properties that need calculations (or not constants)"""
        if self.size <= 5:
            raise ValueError("n_rows_and_cols must be greater than 5. This can be changed "
                             "in the source code, but it may cause some rendering issues.")
        self._minimal_radius = HexagonTile(
            radius=self.radius, position=(0,0), colour=(0,0,0)).minimal_radius
        self.screen_size = (
            3   * self._minimal_radius * self.size + self.radius * 2,
            1.5 * self.radius          * self.size + self.radius * 3 + 100
        )
        if self.mode not in ["pvp", "pva", "avp", "ava"]:
            raise ValueError("Mode must be one of 'pvp', 'pva', 'avp', or 'ava'")

        
    def init_hexagons(self) -> List[List[HexagonTile]]:
        """Creates a hexaogonal tile map of size num_x * num_y"""
        hexagon_row = []
        hexagons = []
        for i in range(self.size):
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
            for j in range(1, self.size):
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


    def render_hexagrid(self, screen, hexagons, winner_group=None):
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
            hexagons[0][self.size - 1].vertices[5],
            hexagons[0][self.size - 1].vertices[0])
        lower_left_mid = mid(
            hexagons[self.size - 1][0].vertices[2],
            hexagons[self.size - 1][0].vertices[3])
        pygame.draw.lines(screen, (255, 0, 0), closed=False, points=
            [hexagons[0][j].vertices[k]
                for j in range(self.size - 1)
                for k in [1, 0, 5]]
            + [hexagons[0][self.size - 1].vertices[0]]
            + [upper_right_mid],
            width=self.color_edge_width
        )
        pygame.draw.lines(screen, (0, 0, 255), closed=False, points=
            [upper_right_mid]
            + [hexagons[0][self.size - 1].vertices[5]]
            + [hexagons[i][self.size - 1].vertices[k]
                for i in range(1, self.size)
                for k in [0, 5, 4]
            ],
            width=self.color_edge_width
        )
        pygame.draw.lines(screen, (0, 0, 255), closed=False, points=
            [hexagons[i][0].vertices[k]
                for i in range(0, self.size - 1)
                for k in [1, 2, 3]] 
            + [hexagons[self.size - 1][0].vertices[2]]
            + [lower_left_mid],
            width=self.color_edge_width
        )
        pygame.draw.lines(screen, (255, 0, 0), closed=False, points=
            [lower_left_mid]
            + [hexagons[self.size - 1][0].vertices[3]]
            + [hexagons[self.size - 1][j].vertices[k]
                for j in range(1, self.size)
                for k in [2, 3, 4]],
            width=self.color_edge_width
        )

        if winner_group is not None:
            for i, j in winner_group:
                hexagons[i][j].mark_winner_group(screen)


    def init_buttons(self, text="Hex RL by @htnminh") -> List[Button]:
        buttons = []

        reset_button = Button(60, self.screen_size[1] - 45, text="Reset")
        buttons.append(reset_button)

        screenshot_button = Button(180, self.screen_size[1] - 45, text="Screenshot")
        buttons.append(screenshot_button)
        
        return buttons


    def render_buttons(self, screen, buttons):
        for button in buttons:
            button.render(screen)

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            if button.is_collide(mouse_pos):
                button.render_highlight()


    def init_info_text(self, text="Hex RL by @htnminh"):
        return TextButton(
            self.screen_size[0]/2, self.screen_size[1] - 90, text=text,
            text_colour=(0, 0, 0), colour=(220, 220, 220)
        )

    def render_info_text(self, screen, info_text):
        info_text.render(screen)
        

    def main(self):
        """Main function"""
        pygame.init()
        screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(self.caption)
        clock = pygame.time.Clock()
        hexagons = self.init_hexagons()
        buttons = self.init_buttons()
        info_text = self.init_info_text()
        
        terminated = False

        hex = Hex(size=self.size, rich_exceptions=False)
        player = hex.player
        winner_group = None
        # TODO
        if self.agent == "random":
            model = RandomModel()
        # TODO
        # agent make the first move
        if self.mode[0] == "a":  # avp ava
            curr_player = hex.player
            action = model.predict(hex.board)
            hex.play(action)
            winner_group = hex.get_winner_group()
            hexagons[action[0]][action[1]].play(1)

            player = hex.player

        while not terminated:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    terminated = True

                # TODO
                if self.mode != 'ava':  # only if a player is involved
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # left click                    
                        for i, hexagon_row in enumerate(hexagons):
                            for j, hexagon in enumerate(hexagon_row):
                                if hexagon.collide_with_point(pygame.mouse.get_pos()):
                                    try:
                                        hex.play((i, j))
                                        winner_group = hex.get_winner_group()
                                    except Exception as e:
                                        print(e)
                                        info_text = self.init_info_text(str(e))
                                    else:
                                        hexagon.play(player)
                                        info_text = self.init_info_text()

                                        # TODO
                                        if self.mode != 'pvp':  # if an agent is involved
                                            if hex.winner is None:
                                                curr_player = hex.player
                                                action = model.predict(hex.board)
                                                hex.play(action)
                                                winner_group = hex.get_winner_group()
                                                hexagons[action[0]][action[1]].play(curr_player)

                                    player = hex.player
                else:  # if no player is involved
                    if hex.winner is None:
                        curr_player = hex.player
                        action = model.predict(hex.board)
                        hex.play(action)
                        winner_group = hex.get_winner_group()
                        hexagons[action[0]][action[1]].play(curr_player)



                    for button in buttons:
                        if button.is_collide(pygame.mouse.get_pos()):
                            if button.text == "Reset":
                                print("Reset")
                                hex = Hex(size=self.size, rich_exceptions=False)
                                player = hex.player
                                winner_group = None
                                hexagons = self.init_hexagons()
                            elif button.text == "Screenshot":
                                time_str = str(datetime.datetime.now().strftime('%Y %m %d %H %M %S')) 
                                Path('hex_rl/screenshots').mkdir(parents=True, exist_ok=True)
                                pygame.image.save(screen, f'hex_rl/screenshots/{time_str}.png')
                            

            for hexagon in self._flatten_hexagons(hexagons):
                hexagon.update()

            for button in buttons:
                button.update()

            self.render_hexagrid(screen, hexagons, winner_group)
            self.render_buttons(screen, buttons)
            self.render_info_text(screen, info_text)
            pygame.display.flip()

            clock.tick(60)  # max fps
        pygame.display.quit()


if __name__ == "__main__":
    HexagonGrid(mode='ava').main()


