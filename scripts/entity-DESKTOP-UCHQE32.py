from scripts.inventory import Inventory
from random import Random
from abc import ABC, abstractmethod
import math


class Entity():
    def __init__(self):
        self.is_player = False
        self._name = 'Joe'
        self.level = 1

        self.target = 20

        self._attack = 1
        self._defense = 1
        self._speed = 1

        self.health_base = 5 * self.level
        self.max_health = self.health_base
        self.current_health = self.max_health
        
        self.attack_mod = 0
        self.defense_mod = 0
        self.speed_mod = 0

        self._damage = 0
        self._mitigation = 0
        self._finesse = 0

        self.inventory = Inventory()
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        removed_suffix = value.removesuffix('.txt')
        self._name = removed_suffix.capitalize()

    @property
    def damage(self):
        return self._damage
    
    @damage.setter
    def damage(self, value):
        self._damage = self.round_down(value / 2)

    @property
    def mitigation(self):
        return self._mitigation
    
    @mitigation.setter
    def mitigation(self, value):
        self._mitigation = self.round_down(value / 2)

    @property
    def finesse(self):
        return self._finesse
    
    @finesse.setter
    def finesse(self, value):
        self._finesse = self.round_down(value / 2)

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
        self.current_health = self.max_health

    def set_health(self, value):
        self.current_health += value
    
    def roll_attack(self):
        r = Random()
        attack = self.attack + self.attack_mod
        
        attack_modifier_high = self.round_up(attack * 2) + self.damage
        attack_modifier_low = self.round_up(attack / 2) + self.damage
        # print('Range that can be rolled is from {} - {}'.format(attack_modifier_low, attack_modifier_high))

        damage = r.randint(attack_modifier_low, attack_modifier_high)

        print('{} rolled {} for damage...'.format(self.name, damage))
        
        total_damage = self.roll_crit(damage)
        return total_damage
    
    def roll_crit(self, damage):
        r = Random()
        speed = self.speed + self.speed_mod

        crit_modifier = self.round_up((speed / 2) + self.finesse)
        crit_chance = 10
        crit_damage_bonus = speed

        roll = r.randrange(1, 101, 1) - crit_modifier

        print('{} needs a {} or less to crit...'.format(self.name, crit_chance))
        print('{} rolled a {} to crit with a modifier of {}...'.format(self.name, roll, crit_modifier))
        
        if roll <= crit_chance:
            total_damage = (damage * 2) + self.round_up(crit_damage_bonus)

            print('{} lands a crit for {} damage...'.format(self.name, total_damage))
            
            return total_damage
        else:
            return damage
        
    def take_damage(self, damage, combat=True):
        defense = self.defense + self.defense_mod
        if combat:
            total_damage = damage - self.round_up((defense / 2) + self.mitigation)
            
            if total_damage < 0:
                total_damage = 0
            
            print('{} took {} damage after {} defense...'.format(self.name, total_damage, (damage - total_damage)))
            
            self.current_health -= total_damage

    def print_entity(self):
        attack = self.attack + self.attack_mod
        defense = self.defense + self.defense_mod
        speed = self.speed + self.speed_mod

        print('{} level {}: Health {}, Attack {}, Defense {}, Speed {}'.format(self.name, self.level, self.current_health, attack, defense, speed))
        if self.inventory.equipped_items['Held'] is not None:
            print('You are currently weilding a {} as your weapon.'.format(self.inventory.equipped_items['Held'].name))
        if self.inventory.equipped_items['Body'] is not None:
            print('You are currently wearing {} for armor.'.format(self.inventory.equipped_items['Body'].name))
        
        if self.inventory.equipped_items['Trinkets']:
            formated_trinkets = ''
            for i, v in enumerate(self.inventory.equipped_items['Trinkets']):
                if i == len(self.inventory.equipped_items['Trinkets']) - 1:
                    trinket = '{}'.format(v.name)
                else:
                    trinket = '{}, '.format(v.name)
                formated_trinkets += trinket
                
            print('You are currently wearing {} as your trinkets.'.format(formated_trinkets))
        print()

    def round_up(self, num):
        rouned = math.ceil(num)
        return rouned
    
    def round_down(self, num):
        rounded = math.floor(num)
        return rounded
    
    def update_stats(self):
        self.health_base = 5 * self.level
        self.max_health = self.health_base + self.round_up(self.defense / 2)

        total_stats = self.inventory.get_stat_modifiers()
        for key, value in total_stats.items():
            if key == 'damage':
                self.damage = value
            elif key == 'mitigation':
                self.mitigation = value
            elif key == 'finesse':
                self.finesse = value
            elif key == 'attack':
                self.attack_mod = value
            elif key == 'defense':
                self.defense_mod = value
            elif key == 'speed':
                self.speed_mod = value

        self.accounting()

    def is_dead(self):
        if self.current_health <= 0:
            return True
        else:
            return False
        
    def equip_item(self, value):
        self.inventory.equip_item(value)
        self.update_stats()

    def accounting(self):
        if self.inventory.income >= self.target:
            self.level += 1
            self.target *= 2