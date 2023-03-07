"""
entity.py
Holds the class for all Entities in the game.

by Alexander Turner
"""


class Entity:
    def __init__(self, name, level, attack, defense, speed):
        self.name = name
        self.level = level
        
        self.attack = attack
        self.defense = defense
        self.speed = speed

        self.health = self.level + (self.defense * 1.1) + (self.speed * 0.15)

    def wound(self, damage):
        self.health -= damage

    def heal(self, damage):
        self.health += damage

    def attack(self):
        base_attack = (self.level * 0.25) + (self.attack * 0.5) + (self.speed * 0.1)

    
def debug(location, message):
    print("DEBUG@entity.{}: {}".format(location, message))