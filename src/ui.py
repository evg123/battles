"""
Code related to user interface
"""

import pygame
from src.graphics import Colors


class Button:
    """
    A button or text box in the UI
    """
    BUTTON_COLOR = Colors.gray
    BUTTON_TEXT_SIZE = 16

    def __init__(self, callback, args, text, rect, display=True):
        self.callback = callback
        self.args = args
        self.text = text
        self.rect = rect
        self.display = display

    def draw(self, renderer):
        if not self.display:
            return
        renderer.draw_rect(self.BUTTON_COLOR, self.rect)
        renderer.draw_text(Colors.black, self.rect.center,
                           self.BUTTON_TEXT_SIZE, self.text)

    def call(self):
        """Run the callback for this button"""
        if self.callback:
            self.callback(*self.args)

    def toggle_display(self):
        """Show or hid the button"""
        self.display = not self.display


class Ui:
    """
    Holds buttons and provider helpers for creating them
    """
    BUTTON_BUFFER = 10

    def __init__(self, renderer):
        self.renderer = renderer
        self.buttons = []
        self.next_button_top = self.BUTTON_BUFFER

    def add_button(self, text, size, callback, args=(), centered=False, display=True):
        """Create a new button and add it to the UI"""
        rect = self.get_rect(size[0], size[1], centered)
        button = Button(callback, args, text, rect, display)
        self.buttons.append(button)
        return button

    def get_rect(self, width, height, centered):
        """Figure out where a new button with the given parameters would go"""
        if centered:
            left = (self.renderer.window.get_width() / 2) - (width / 2)
            top = (self.renderer.window.get_height() / 2) - (height / 2)
            rect = pygame.Rect((left, top), (width, height))
        else:
            # Place on the right side of the screen underneath the last button
            left = self.renderer.window.get_width() - width - self.BUTTON_BUFFER
            rect = pygame.Rect(left, self.next_button_top, width, height)
            self.next_button_top = self.next_button_top + height + self.BUTTON_BUFFER
        return rect

    def draw(self):
        for button in self.buttons:
            button.draw(self.renderer)

    def handle_click(self, x_pos, y_pos):
        """Dispatch the click to a button if it was on one.
        Return True iff the click hit something.
        """
        for button in self.buttons:
            if button.display and button.rect.collidepoint(x_pos, y_pos):
                button.call()
                return True
        return False

