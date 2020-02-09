#######################################################
# Program   : game_stats.py
# Author    : Aaron Rioflorido
#
# Function  : Stores the GameStats class for the Alien Invasion game.
#
#######################################################
from game_functions import load_high_score


class GameStats:
    """Track statistics for Alien Invasion"""

    def __init__(self, ai_settings):
        """Initialize statistics."""
        self.ai_settings = ai_settings

        # Start the game in an active state
        self.game_active = True

        # High score should never be reset.
        self.high_score = 0

        # Reload high score from save file
        load_high_score(self.ai_settings, self)

        self.reset_stats()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1

