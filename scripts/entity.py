from random import Random
from abc import ABC, abstractmethod
import math


class Entity():
    def __init__(self):
        self.is_player = False
        self.name = 'Joe'
        self.level = 1
        self.attack = 1
        self.defense = 1
        self.speed = 1
        
        self.damage_reduction = 0
        self.attack_bonus = 0
        self.speed_bonus = 0
        
        self.health_base = 5
        self.damage_taken = 0
        
    @property
    def attack(self):
        return self._attack
    
    @attack.setter
    def attack(self, value):
        self._attack = self.round_up(value)

    @property
    def defense(self):
        return self._defense
    
    @defense.setter
    def defense(self, value):
        self._defense = self.round_up(value)

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        self._speed = self.round_up(value)

    def reset_health(self):
        self.health = self.health_base + self.round_up(self.defense / 2)
    
    def roll_attack(self):
        r = Random()
        
        self.attack_modifier_high = self.round_up(self.attack * 2)
        self.attack_modifier_low = self.round_up(self.attack / 2)
        self.damage = r.randint(self.attack_modifier_low, self.attack_modifier_high)

        print('{} rolled {} for damage...'.format(self.name, self.damage))
        
        total_damage = self.roll_crit(self.damage)
        return total_damage
    
    def roll_crit(self, damage):
        r = Random()

        self.crit_modifier = self.round_up(self.speed / 2)
        self.crit_chance = 10
        self.crit_damage_bonus = self.speed

        roll = r.randrange(1, 101, 1) - self.crit_modifier

        print('{} needs a {} or less to crit...'.format(self.name, self.crit_chance))
        print('{} rolled a {} to crit with a modifier of {}...'.format(self.name, roll, self.crit_modifier))
        
        if roll <= self.crit_chance:
            total_damage = (damage * 2) + self.round_up(self.crit_damage_bonus)

            print('{} lands a crit for {} damage...'.format(self.name, total_damage))
            
            return total_damage
        else:
            return damage
        
    def take_damage(self, damage, defended=False, combat=True):
        if combat:
            if defended:
                total_damage = damage - self.round_up(self.defense * 1.5)
            else:
                total_damage = damage - self.round_up(self.defense / 2)
            
            if total_damage < 0:
                total_damage = 0
            
            print('{} took {} damage after defenses...'.format(self.name, total_damage))
            
            self.health -= total_damage

    def print_entity(self):
        print('{} level {}: Health {}, Attack {}, Defense {}, Speed {}'.format(self.name, self.level, self.health, self.attack, self.defense, self.speed))

    def round_up(self, num):
        rouned = math.ceil(num)
        return rouned
    
    def update(self):
        pass

    def is_dead(self):
        if self.damage_taken >= self.health:
            return True
        else:
            return False