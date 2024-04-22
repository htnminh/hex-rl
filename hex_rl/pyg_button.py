import pygame
from typing import Tuple
from dataclasses import dataclass
from pyg_utils import brighten_color


@dataclass
class Button:
    x: float
    y: float
    # width: float = 50
    # height: float = 30
    text: str = ""
    colour: Tuple[int, int, int] = (20, 100, 20)
    highlight_offset: int = 5
    max_highlight_ticks: int = 10
    text_colour: Tuple[int, int, int] = (255, 255, 255)
    font_size: int = 30


    def __post_init__(self):
        self.font = pygame.font.Font(None, self.font_size)
        self.text_render = self.font.render(self.text, True, self.text_colour)
        self.text_rect = self.text_render.get_rect(
            center = (self.x, self.y),
        )
        self.highlight_tick = 0  # TODO: copied from hexagon.py, refactor?


    def render(self, screen):
        pygame.draw.rect(screen, self.highlight_colour, self.text_rect)
        screen.blit(self.text_render, self.text_rect)


    def is_collide(self, mouse_pos):
        return self.text_rect.collidepoint(mouse_pos)


    # TODO: copied from hexagon.py, refactor?
    def update(self):
        """Updates tile highlights"""
        if self.highlight_tick > 0:
            self.highlight_tick -= 1
    
    
    def render_highlight(self) -> None:
        self.highlight_tick = self.max_highlight_ticks

    
    @property
    def highlight_colour(self) -> Tuple[int, ...]:
        """Colour of the hexagon tile when rendering highlight"""
        offset = self.highlight_offset * self.highlight_tick
        return brighten_color(self.colour, offset)