import pygame
from typing import Tuple
from dataclasses import dataclass



@dataclass
class Button:
    x: float
    y: float
    width: float = 50
    height: float = 30
    text: str = ""
    colour: Tuple[int, int, int] = (180, 180, 180)
    text_colour: Tuple[int, int, int] = (0, 0, 0)
    font_size = 30


    def __post_init__(self):
        self.font = pygame.font.Font(None, self.font_size)
        self.text = self.font.render(self.text, True, self.text_colour)
        self.text_rect = self.text.get_rect(
            center = (self.x, self.y),
            )

    def render(self, screen):
        pygame.draw.rect(screen, self.colour, self.text_rect)
        screen.blit(self.text, self.text_rect)


    def is_collide(self, mouse_pos):
        return self.text_rect.collidepoint(mouse_pos)
    
    
    def update(self):
        if self.is_collide(pygame.mouse.get_pos()):
            self.colour = (255, 255, 255)
            