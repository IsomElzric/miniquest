"""
entity.py
Holds the class for all Entities in the game.

by Alexander Turner
"""


from random import Random


class Entity:
    def __init__(self, name, level, attack, defense, speed):
        self.name = name
        self.level = level
        
        self.attack = attack
        self.defense = defense
        self.speed = speed

        self.health = round((self.level * 5) + (self.defense * 1.1) + (self.speed * 0.15), 2)
        self.random = Random()

    def wound(self, damage):
        self.health -= damage
        round(self.health, 2)

    def heal(self, damage):
        self.health += damage
        round(self.health, 2)

    def get_damage(self):
        base_attack = (self.level * 0.25) + (self.attack * 0.5) + (self.speed * 0.1)
        random_roll = self.random.random()
        return round(random_roll + base_attack, 2)

    
def debug(location, message):
    print("DEBUG@entity.{}: {}".format(location, message))