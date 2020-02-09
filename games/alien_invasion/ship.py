#######################################################
# Program   : ship.py
# Author    : Aaron Rioflorido
#
# Function  : Contains the Ship class for the Alien Invasion Game.
#
#######################################################
import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """Ship class containing the ship's position, image, etc."""

    def __init__(self, ai_settings, screen):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.centerx = self.screen_rect.centerx   # x coordinate
        self.rect.bottom = self.screen_rect.bottom     # y coordinate

        # Store decimal values for the ship's center and bottom.
        self.center = float(self.rect.centerx)
        self.bottom = float(self.rect.bottom)

        # Flags for continuous movements
        self.moving_right = False
        self.moving_left = False
        self.moving_forward = False
        self.moving_backward = False
        self.movement_speed = ai_settings.ship_speed_factor
        self.turbo_mode = False

    def center_ship(self):
        """Center the ship on the screen"""
        self.center = float(self.screen_rect.centerx)
        self.bottom = float(self.screen_rect.bottom)

    def update(self):
        """Update the ship's position based on the movement flag."""

        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.movement_speed
        elif self.moving_left and self.rect.left > 0:
            self.center -= self.movement_speed
        elif self.moving_forward and self.bottom > self.rect.height:
            self.bottom -= self.movement_speed
        elif self.moving_backward and self.bottom < self.screen_rect.height:
            self.bottom += self.movement_speed

        if self.turbo_mode:
            self.movement_speed = self.ai_settings.ship_turbo_speed
        else:
            self.movement_speed = self.ai_settings.ship_speed_factor

        # Updates/Controls the position of the ship
        self.rect.centerx = self.center
        self.rect.bottom = self.bottom

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
