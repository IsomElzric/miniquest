# scripts/entity.py
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
    
    def roll_attack(self, message_log): 
        r = Random()
        attack = self.attack + self.attack_mod
        
        attack_modifier_high = self.round_up(attack * 2) + self.damage
        attack_modifier_low = self.round_up(attack / 2) + self.damage

        damage = r.randint(attack_modifier_low, attack_modifier_high)

        # message_log(f'{self.name} rolled {damage} for damage...')
        # message_log('') # Add spacing
        
        total_damage = self.roll_crit(damage, message_log) 
        return total_damage
    
    def roll_crit(self, damage, message_log): 
        r = Random()
        speed = self.speed + self.speed_mod

        crit_modifier = self.round_up((speed / 2) + self.finesse)
        crit_chance = 10
        crit_damage_bonus = speed

        roll = r.randrange(1, 101, 1) - crit_modifier

        # Removed detailed crit roll messages for brevity
        # message_log(f'{self.name} needs a {crit_chance} or less to crit...')
        # message_log(f'{self.name} rolled a {roll} to crit with a modifier of {crit_modifier}...')
        
        if roll <= crit_chance:
            total_damage = (damage * 2) + self.round_up(crit_damage_bonus)

            message_log(f'{self.name} lands a mortal wound!')
            # message_log('') # Add spacing
            
            return total_damage
        else:
            # message_log(f'{self.name} did not land a critical hit.') # Clarify no crit
            # message_log('') # Add spacing
            return damage
        
    def take_damage(self, damage, message_log, combat=True): 
        defense = self.defense + self.defense_mod
        if combat:
            total_damage = damage - self.round_up((defense / 2) + self.mitigation)
            
            if total_damage < 0:
                total_damage = 0
            
            message_log(f'{self.name} takes {total_damage} damage.') # Simplified message
            
            # message_log('') # Add spacing
            self.current_health -= total_damage

    # MODIFIED: Only changed this method to use message_log
    def print_entity(self, message_log): 
        attack = self.attack + self.attack_mod
        defense = self.defense + self.defense_mod
        speed = self.speed + self.speed_mod

        message_log(f'{self.name} level {self.level}: Health {self.current_health}/{self.max_health}, Attack {attack}, Defense {defense}, Speed {speed}')
        if self.inventory.equipped_items['Held'] is not None:
            message_log(f'You are currently wielding a {self.inventory.equipped_items["Held"].name} as your weapon.')
        if self.inventory.equipped_items['Body'] is not None:
            message_log(f'You are currently wearing {self.inventory.equipped_items["Body"].name} for armor.')
        
        if self.inventory.equipped_items['Trinkets']:
            formated_trinkets = ''
            for i, v in enumerate(self.inventory.equipped_items['Trinkets']):
                if i == len(self.inventory.equipped_items['Trinkets']) - 1:
                    trinket = '{}'.format(v.name)
                else:
                    trinket = '{}, '.format(v.name)
                formated_trinkets += trinket
                
            message_log(f'You are currently wearing {formated_trinkets} as your trinkets.')
        message_log('') # Add an empty line for spacing in the log

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
        # This method is now primarily for equipping from carried items by default.
        # For equipping from strongbox or with explicit source, use equip_item_from_storage.
        self.inventory.equip_item(value)
        self.update_stats()
    
    def accounting(self):
        if self.inventory.income >= self.target:
            self.level += 1
            self.target *= 2

    def scaling(self):
        if not self.is_player:
            self.attack *= self.level
            self.defense *= self.level
            self.speed *= self.level

    def apply_night_scaling(self, modifier, message_log_func):
        """Applies a scaling modifier to non-player entities, typically at night."""
        if not self.is_player and modifier > 1.0:
            # original_attack = self.attack # Not strictly needed unless logging specific changes
            # original_defense = self.defense
            
            self.attack = self.round_up(self.attack * modifier)
            self.defense = self.round_up(self.defense * modifier)
            # Speed could also be modified if desired
            self.update_stats() # Recalculate max_health, etc., based on new defense
            
            message_log_func(f"The encroaching darkness empowers {self.name}!")

    def equip_item_from_storage(self, item_to_equip, source_location_name, message_log_func):
        """
        Instructs the inventory to equip an item, specifying its source.
        Source can be 'carried' or 'strongbox'.
        """
        success = self.inventory.equip_item(item_to_equip, source_location_name=source_location_name, message_log_func=message_log_func)
        if success:
            self.update_stats()
        # Inventory.equip_item will handle logging success/failure