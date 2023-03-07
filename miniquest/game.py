"""
game.py
Holds the game class for miniquest.

by Alexander Turner
"""


from menu import Menu
from entity import Entity


class Game():
    """
    The game class holds the functions to loop through and run the game.
    """
    def __init__(self):
        """
        Initializes our game objects and sets the game loop running.
        """
        self.run = True

    def start_game(self):
        """
        Begins the game loop.
        """
        
        self.do_output()

    def do_output(self):
        pass


def debug(location, message):
    print("DEBUG@game.{}: {}".format(location, message)) 