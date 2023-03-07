"""
game.py
Holds the game class for miniquest.

by Alexander Turner
"""


from miniquest.menu import Menu
from miniquest.entity import Entity


class Game():
    """
    The game class holds the functions to loop through and run the game.
    """
    def __init__(self):
        """
        Initializes our game objects and sets the game loop running.
        """
        self.run = True

        self.player = Entity("Amira", 1, 3, 2, 1)
        self.enemy = Entity("Thief", 1, 2, 1, 3)

    def start_game(self):
        """
        Begins the game loop.
        """
        self.do_output()

    def do_output(self):
        print("Player: {} Level: {} Health: {} - Attack: {} Defense: {} Speed: {}".format(
            self.player.name, self.player.level, self.player.health, 
            self.player.attack, self.player.defense, self.player.speed
        ))

        print("Enemy: {} Level: {} Health: {} - Attack: {} Defense: {} Speed: {}".format(
            self.enemy.name, self.enemy.level, self.enemy.health, 
            self.enemy.attack, self.enemy.defense, self.enemy.speed
        ))

        damage = self.player.get_damage()
        print("{} - Damage Dealt: {}".format(self.player.name, damage))

        self.enemy.wound(damage)
        print("{} - Health: {}".format(self.enemy.name, self.enemy.health))



def debug(location, message):
    print("DEBUG@game.{}: {}".format(location, message)) 