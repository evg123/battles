"""
Code related to user interface
"""

import pygame
from src.graphics import Colors


class Button:

    BUTTON_COLOR = Colors.gray

    def __init__(self, callback, text, rect):
        self.callback = callback
        self.text = text
        self.rect = rect

    def draw(self, renderer):
        renderer.draw_rect(self.BUTTON_COLOR, self.rect)

    def call(self):
        self.callback()


class Ui:

    BUTTON_BUFFER = 10

    def __init__(self, renderer):
        self.renderer = renderer
        self.buttons = []
        self.next_button_top = self.BUTTON_BUFFER

    def add_button(self, callback, text, width, height, centered=False):
        rect = self.get_rect(width, height, centered)
        button = Button(callback, text, rect)
        self.buttons.append(button)

    def get_rect(self, width, height, centered):
        if centered:
            rect = pygame.Rect()
        else:
            left = self.renderer.window.width - width - self.BUTTON_BUFFER
            rect = pygame.Rect(left, self.next_button_top, width, height)
            self.next_button_top = self.next_button_top + height + self.BUTTON_BUFFER
        return rect

    def draw(self):
        for button in self.buttons:
            button.draw(self.renderer)

    def handle_click(self, x_pos, y_pos):
        for button in self.buttons:
            if button.rect.collidepoint(x_pos, y_pos):
                button.call()
                return True
        return False

