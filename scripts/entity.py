# scripts/entity.py
from scripts.inventory import Inventory
from random import Random
from abc import ABC, abstractmethod
import random # For volatile stat gain
import math # For rounding functions
from typing import Callable # Import Callable for more specific type hinting


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

        # New attributes for abilities and background-specific progression
        self.abilities = set()
        self.background_stat_gains = {}  # e.g., {"attack": 0.5, "health_per_level_bonus": 2}
        self.background_ability_unlocks = []  # e.g., [{"level": 3, "ability": "some_new_skill"}]
        self.message_log_func: Callable[[str], None] | None = None # To be set by World for the player entity
        self.world_abilities_data = {} # To store reference to all defined abilities
    
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
        return self._attack + self.attack_mod
    
    @attack.setter
    def attack(self, value):
        self._attack = self.round_up(value)

    @property
    def defense(self):
        return self._defense + self.defense_mod
    
    @defense.setter
    def defense(self, value):
        self._defense = self.round_up(value)

    @property
    def speed(self):
        return self._speed + self.speed_mod
    
    @speed.setter
    def speed(self, value):
        self._speed = self.round_up(value)

    def reset_health(self):
        self.current_health = self.max_health

    def set_health(self, value):
        self.current_health += value
    
    def roll_attack(self, message_log): 
        r = Random()
        attack = self.attack # + self.attack_mod
        
        attack_modifier_high = self.round_up(attack * 2) + self.damage
        attack_modifier_low = self.round_up(attack / 2) + self.damage

        damage = r.randint(attack_modifier_low, attack_modifier_high)

        # message_log(f'{self.name} rolled {damage} for damage...')
        # message_log('') # Add spacing
        
        total_damage = self.roll_crit(damage, message_log) 
        return total_damage
    
    def roll_crit(self, damage, message_log): 
        r = Random()
        speed = self.speed # + self.speed_mod

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
        defense = self.defense # + self.defense_mod
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

        # Reset mods before applying from abilities and items
        self.attack_mod = 0
        self.defense_mod = 0
        self.speed_mod = 0
        # self.damage, self.mitigation, self.finesse are base item stats, not mods in the same way.

        # Apply passive ability stat bonuses
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                if ability_def.get("type") == "passive" and "effect" in ability_def:
                    effect = ability_def["effect"]
                    if "stat_bonus_flat" in effect:
                        for stat, bonus in effect["stat_bonus_flat"].items():
                            if stat == "attack": self.attack_mod += bonus
                            elif stat == "defense": self.defense_mod += bonus
                            elif stat == "speed": self.speed_mod += bonus

        total_stats = self.inventory.get_stat_modifiers()
        for key, value in total_stats.items():
            if key == 'damage':
                self.damage = value
            elif key == 'mitigation':
                self.mitigation = value
            elif key == 'finesse':
                self.finesse = value
            # Item stat modifiers are added to existing mods from abilities
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
            self.target *= 2 # Increase XP target for next level

            # Stat gains logic
            if "volatile_stat_gain" in self.abilities:
                stats_pool = ["attack", "defense", "speed"]
                major_stat = random.choice(stats_pool)
                
                gains_messages = []
                for stat_name in stats_pool:
                    gain = 3 if stat_name == major_stat else 1
                    if stat_name == "attack":
                        self._attack += gain
                    elif stat_name == "defense":
                        self._defense += gain
                    elif stat_name == "speed":
                        self._speed += gain
                    gains_messages.append(f"{stat_name.capitalize()}: +{gain}")
                
                if self.is_player and self.message_log_func:
                    self.message_log_func(f"Volatile energies surge! {major_stat.capitalize()} increased by 3, others by 1.")
            
            elif self.background_stat_gains: # Check if the dict is not empty (standard gains)
                atk_gain = self.round_up(self.background_stat_gains.get("attack", 0.2))
                def_gain = self.round_up(self.background_stat_gains.get("defense", 0.2))
                spd_gain = self.round_up(self.background_stat_gains.get("speed", 0.2))
                self._attack += atk_gain
                self._defense += def_gain
                self._speed += spd_gain
                if self.is_player and self.message_log_func:
                    self.message_log_func(f"Gained stats: Atk +{atk_gain}, Def +{def_gain}, Spd +{spd_gain}.")
            else:
                # Fallback default gains if no background data or volatile ability
                self._attack += 1 
                self._defense += 1
                self._speed += 1
                if self.is_player and self.message_log_func:
                    self.message_log_func("Gained stats: Atk +1, Def +1, Spd +1.")

            # Health bonus (can be independent of volatile stat gain for primary stats)
            if self.background_stat_gains: # Check if dict is not empty
                health_bonus = self.background_stat_gains.get("health_per_level_bonus", 1)
                self.health_base += health_bonus
                if self.is_player and self.message_log_func:
                    self.message_log_func(f"Base health increased by {health_bonus}.")
            else: # Fallback
                self.health_base += 1 
                if self.is_player and self.message_log_func:
                    self.message_log_func("Base health increased by 1.")

            # Unlock abilities based on level
            if self.background_ability_unlocks:
                for unlock_info in self.background_ability_unlocks:
                    if unlock_info["level"] == self.level:
                        self.abilities.add(unlock_info["ability"])
                        if self.is_player and self.message_log_func:
                            # TODO: Consider looking up a friendly name for the ability key
                            self.message_log_func(f"New ability unlocked: {unlock_info['ability']}!")
            
            self.update_stats() # Recalculate derived stats like max_health
            self.reset_health() # Fully heal on level up
            if self.is_player and self.message_log_func:
                 self.message_log_func(f"You have reached level {self.level}!")
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

    def to_dict(self):
        entity_data = {
            "name": self.name,
            "level": self.level,
            "target": self.target,
            "_attack": self._attack,
            "_defense": self._defense,
            "_speed": self._speed,
            "health_base": self.health_base,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "attack_mod": self.attack_mod,
            "defense_mod": self.defense_mod,
            "speed_mod": self.speed_mod,
            "_damage": self._damage,
            "_mitigation": self._mitigation,
            "_finesse": self._finesse,
            "is_player": self.is_player,
            "inventory": self.inventory.to_dict(),
            "abilities": list(self.abilities), # Convert set to list for JSON
            # background_stat_gains & background_ability_unlocks are part of the background, not saved per entity if re-applied on load
            "background_stat_gains": self.background_stat_gains,
            "background_ability_unlocks": self.background_ability_unlocks,
        }
        return entity_data

    @classmethod
    def from_dict(cls, data, all_items_lookup_map, message_log_func):
        instance = cls() # This will call __init__
        instance.name = data.get("name", "Loaded Entity")
        instance.level = data.get("level", 1)
        instance.target = data.get("target", 20)
        instance._attack = data.get("_attack", 1)
        instance._defense = data.get("_defense", 1)
        instance._speed = data.get("_speed", 1)
        
        instance.attack_mod = data.get("attack_mod", 0)
        instance.defense_mod = data.get("defense_mod", 0)
        instance.speed_mod = data.get("speed_mod", 0)
        instance._damage = data.get("_damage", 0)
        instance._mitigation = data.get("_mitigation", 0)
        instance._finesse = data.get("_finesse", 0)
        instance.is_player = data.get("is_player", False)
        
        inventory_data = data.get("inventory")
        if inventory_data:
            instance.inventory.from_dict(inventory_data, all_items_lookup_map, message_log_func)

        instance.abilities = set(data.get("abilities", [])) # Convert list back to set
        instance.background_stat_gains = data.get("background_stat_gains", {})
        instance.background_ability_unlocks = data.get("background_ability_unlocks", [])
        # world_abilities_data will be set by World after loading the entity


        instance.update_stats() # Recalculate derived stats like max_health
        instance.max_health = data.get("max_health", instance.max_health) # Restore saved max_health
        instance.current_health = data.get("current_health", instance.max_health)
        instance.current_health = min(instance.current_health, instance.max_health)
        return instance
        # Inventory.equip_item will handle logging success/failure