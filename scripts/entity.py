# scripts/entity.py
from scripts.inventory import Inventory
from random import Random
from abc import ABC, abstractmethod
import random # For volatile stat gain
import math # For rounding functions
from typing import Callable # Import Callable for more specific type hinting


TEMPORARY_WEAVE_START = 50


class Entity():
    def __init__(self):
        self.is_player = False
        self._name = 'Joe'
        self.level = 1

        self.target = 20

        self._attack = 1.0
        self._defense = 1.0
        self._speed = 1.0

        self.health_base = 5 * self.level
        self.max_health = self.health_base
        self.current_health = self.max_health

        self.weave_base = TEMPORARY_WEAVE_START
        # self.weave_base = 3 * self.level # Example: Weave based on level
        self.max_weave = self.weave_base
        self.current_weave = self.max_weave
        
        self.attack_mod = 0.0 # Initialize as float
        self.defense_mod = 0.0 # Initialize as float
        self.speed_mod = 0.0 # Initialize as float

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

        # For conditions and temporary effects
        self.active_conditions = {} # e.g., {"burning": {"duration": 3, "potency": 2}}
        self.temporary_stat_mods = {} # e.g., {"attack": {"amount": 5, "duration": 2}}
    
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
        self._attack = value # No rounding on set

    @property
    def defense(self):
        return self._defense + self.defense_mod

    @defense.setter
    def defense(self, value):
        self._defense = value # No rounding on set

    @property
    def speed(self):
        return self._speed + self.speed_mod
    @speed.setter
    def speed(self, value):
        self._speed = self.round_up(value)

    def reset_health(self):
        self.current_health = self.max_health

    def reset_weave(self):
        self.current_weave = self.max_weave

    def set_health(self, value):
        self.current_health += value
    
    def roll_attack(self, message_log): 
        r = Random()
        attack = self.attack # + self.attack_mod
        
        attack_modifier_high = self.round_up(attack * 2) + self.damage
        attack_modifier_low = self.round_up(attack / 2) + self.damage
        
        # Convert bounds to integers for randint
        low_bound = int(self.round_up(attack_modifier_low))
        high_bound = int(self.round_up(attack_modifier_high))

        # Ensure high_bound is not less than low_bound after integer conversion
        if high_bound < low_bound:
            high_bound = low_bound # Avoids error with randint if, e.g., low=2.8 (int 2) and high=2.1 (int 2)
                                   # or if low=0.9 (int 0) and high=0.2 (int 0)

        base_roll_damage = r.randint(low_bound, high_bound)
        base_roll_damage = max(1, base_roll_damage)
        
        total_damage = self.roll_crit(base_roll_damage, message_log) 
        return total_damage
    
    def roll_crit(self, damage, message_log): 
        r = Random()
        speed = self.speed # + self.speed_mod

        # Reduce speed's impact on crit chance, finesse has more impact.
        crit_modifier = self.round_up((speed / 4) + (self.finesse / 2))
        crit_chance = 10
        # Crit damage bonus now based on attacker's attack and finesse, not raw speed.
        # And base crit damage multiplier reduced.
        crit_damage_bonus_value = self.round_up((self.attack / 4) + (self.finesse / 2))

        roll = r.randrange(1, 101, 1) - crit_modifier

        if roll <= crit_chance:
            # Crits now do 1.5x base damage + the new crit_damage_bonus_value
            total_damage = self.round_up(damage * 1.5) + crit_damage_bonus_value

            message_log(f'{self.name} lands a mortal wound!')
            
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

        message_log(f'{self.name} level {self.level}: Health {self.current_health}/{self.max_health}, Attack {self._attack:.1f} ({self.attack:.1f}), Defense {self._defense:.1f} ({self.defense:.1f}), Speed {self._speed:.1f} ({self.speed:.1f})')
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
        # Rounds up to one decimal place
        return math.ceil(num * 10) / 10
    
    def round_down(self, num):
        # Rounds down to one decimal place
        return math.floor(num * 10) / 10
    
    def update_stats(self):         
        self.health_base = 5 * self.level
        self.max_health = self.health_base + self.round_up(self.defense / 2)
        self.max_weave = self.weave_base # Add weave calculation if it depends on other stats

        # Reset mods before applying from abilities and items
        self.attack_mod = 0.0
        self.defense_mod = 0.0
        self.speed_mod = 0.0
        # self.damage, self.mitigation, self.finesse are base item stats, not mods in the same way.

        # Apply temporary stat mods from conditions/effects
        for stat, mod_info in self.temporary_stat_mods.items():
            if stat == "attack": self.attack_mod += mod_info["amount"]
            elif stat == "defense": self.defense_mod += mod_info["amount"]
            elif stat == "speed": self.speed_mod += mod_info["amount"]

        # Apply passive ability stat bonuses
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                if ability_def.get("type") == "passive" and "effect" in ability_def:
                    effect = ability_def["effect"]
                    # Apply flat bonuses
                    if "stat_bonus_flat" in effect:
                        for stat, bonus in effect["stat_bonus_flat"].items():
                            if stat == "attack": self.attack_mod += bonus
                            elif stat == "defense": self.defense_mod += bonus
                            elif stat == "speed": self.speed_mod += bonus
                    # Apply percentage bonuses (based on base stats)
                    if "stat_bonus_percent" in effect:
                        for stat, bonus_percent in effect["stat_bonus_percent"].items():
                            if stat == "attack":
                                self.attack_mod += self._attack * bonus_percent
                            elif stat == "defense":
                                self.defense_mod += self._defense * bonus_percent
                            elif stat == "speed":
                                self.speed_mod += self._speed * bonus_percent
        
        # Apply item stat modifiers
        total_stats_from_items = self.inventory.get_stat_modifiers()
        for key, value in total_stats_from_items.items():
            if key == 'damage':
                self.damage = value
            elif key == 'mitigation':
                self.mitigation = value
            elif key == 'finesse':
                self.finesse = value
            # Item stat modifiers ADD to existing mods from abilities
            elif key == 'attack': 
                self.attack_mod += value # Corrected from = to +=
            elif key == 'defense':
                self.defense_mod += value # Corrected from = to +=
            elif key == 'speed':
                self.speed_mod += value # Corrected from = to +=
        

        self.accounting()

    def can_use_skill(self, skill_id: str) -> tuple[bool, str]:
        """Checks if the entity can use the specified skill. Returns (can_use, reason_string)."""
        if skill_id not in self.world_abilities_data:
            return False, "Skill unknown."
        if skill_id not in self.abilities: # Check if player actually knows the skill
            return False, "You do not know this skill."

        skill_def = self.world_abilities_data[skill_id]
        if skill_def.get("type") != "active_combat":
            return False, "This is not an active skill."

        cost = skill_def.get("cost", {})
        if "weave" in cost and self.current_weave < cost["weave"]:
            return False, f"Not enough weave (requires {cost['weave']}, have {self.current_weave})."
        # Add other resource checks (stamina, health, items) here if needed

        return True, ""

    def use_skill(self, skill_id: str, target: 'Entity | None', message_log_func: Callable[[str], None]):
        """Uses a skill on a target. Assumes can_use_skill was checked."""
        if not message_log_func: message_log_func = lambda x: print(x) # Fallback

        skill_def = self.world_abilities_data[skill_id]
        skill_name = skill_def.get("name", skill_id)
        message_log_func(f"{self.name} uses {skill_name}!")

        # Deduct cost
        cost = skill_def.get("cost", {})
        if "weave" in cost:
            self.current_weave -= cost["weave"]
            message_log_func(f"Used {cost['weave']} weave. ({self.current_weave}/{self.max_weave} remaining)")

        # Apply effects
        effect = skill_def.get("effect", {})
        # Effects that apply to a target (which could be self if skill_def["target"] == "self")
        if target: 
            if "damage" in effect:
                damage_info = effect["damage"]
                base_damage_amount = damage_info.get("amount", 0)
                # Future: Could scale with player stats, e.g., self.attack * damage_info.get("attack_scaling", 0)
                # For now, direct damage amount
                actual_damage = base_damage_amount # Potentially add randomness or scaling later
                message_log_func(f"{skill_name} hits {target.name} for {actual_damage:.1f} {damage_info.get('type','')} damage.")
                target.take_damage(actual_damage, message_log_func)

            if "damage_multiplier" in effect: # For skills like "Power Strike"
                # This assumes the skill enhances a basic attack action that follows,
                # or it's a direct damage skill where the multiplier applies to some base.
                # For a direct damage skill:
                base_attack_damage = self.roll_attack(message_log_func) # Get base physical damage
                multiplied_damage = self.round_up(base_attack_damage * effect["damage_multiplier"]) # Ensure rounding
                message_log_func(f"{skill_name} empowers the attack, dealing {multiplied_damage:.1f} damage to {target.name}!")
                target.take_damage(multiplied_damage, message_log_func)

            # Apply_condition and temporary_stat_bonus can apply to self or enemy based on target
            if "apply_condition" in effect:
                condition_info = effect["apply_condition"]
                target.add_condition(condition_info["name"], 
                                     condition_info.get("duration", 1), 
                                     condition_info.get("potency", 1), 
                                     skill_name, message_log_func)

            if "temporary_stat_bonus" in effect:
                bonus_info = effect["temporary_stat_bonus"]
                duration = effect.get("duration_turns", 1) # duration_turns should be at the same level as temporary_stat_bonus
                for stat_to_buff, amount in bonus_info.items():
                    target.add_temporary_stat_mod(stat_to_buff, amount, duration, skill_name, message_log_func)

        # Add other effect types: healing, buffs on self, debuffs on enemy, etc.
        if "heal" in effect:
            heal_amount = effect["heal"].get("amount", 0)
            self.current_health = min(self.max_health, self.current_health + heal_amount)
            message_log_func(f"{self.name} heals for {heal_amount} HP.")

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
            
            # Also restore mana on level up
            self.reset_weave()

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

    def log_stat_breakdown(self):
        """Prints a breakdown of the player's stats and their sources to the terminal."""
        if not self.is_player: # Only log for the player
            return

        print("\n--- Player Stat Breakdown ---")
        print(f"  Base Stats: Attack: {self._attack:.1f}, Defense: {self._defense:.1f}, Speed: {self._speed:.1f}")

        # Temporary Stat Mods
        if self.temporary_stat_mods:
            print("  Temporary Mods:")
            for stat, mod_info in self.temporary_stat_mods.items():
                print(f"    - {stat.capitalize()}: +{mod_info['amount']:.1f} (Duration: {mod_info['duration']} turns)")
        else:
            print("  Temporary Mods: None")

        # === Active Abilities ===
        print("  Active Abilities:")
        active_abilities_found = False
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                if ability_def.get("type") == "active_combat":
                    ability_name = ability_def.get("name", ability_key)
                    print(f"    - {ability_name}")
                    active_abilities_found = True
        if not active_abilities_found:
            print("    - None")

        # === Passive Leveling Abilities ===
        print("  Passive Leveling Abilities:")
        passive_leveling_abilities_found = False
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                if ability_def.get("type") == "passive_leveling":
                    ability_name = ability_def.get("name", ability_key)
                    print(f"    - {ability_name}")
                    passive_leveling_abilities_found = True
        if not passive_leveling_abilities_found:
            print("    - None")

        # === Other Passive Abilities ===
        print("  Other Passive Abilities:")
        other_passive_abilities_found = False
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                ability_name = ability_def.get("name", ability_key)
                print(f"    - {ability_name}")
                other_passive_abilities_found = True
        # Passive Ability Mods
        passive_ability_mods_found = False # Using same vars for brevity
        print("  Passive Ability Mods:")
        for ability_key in self.abilities:
            if ability_key in self.world_abilities_data:
                ability_def = self.world_abilities_data[ability_key]
                ability_name = ability_def.get("name", ability_key)
                if ability_def.get("type") == "passive" and "effect" in ability_def:
                    effect = ability_def["effect"]
                    if "stat_bonus_flat" in effect:
                        for stat, bonus in effect["stat_bonus_flat"].items(): # No change necessary to print
                            print(f"    - {ability_name} ({stat.capitalize()}): +{bonus:.1f}")
                            passive_ability_mods_found = True
                    if "stat_bonus_percent" in effect: # Example if you add percentage bonuses
                        for stat, bonus_percent in effect["stat_bonus_percent"].items():
                            calculated_bonus = 0.0
                            if stat == "attack": calculated_bonus = self._attack * bonus_percent
                            elif stat == "defense": calculated_bonus = self._defense * bonus_percent
                            elif stat == "speed": calculated_bonus = self._speed * bonus_percent
                            print(f"    - {ability_name} ({stat.capitalize()}): +{bonus_percent*100:.1f}% (adds +{self.round_up(calculated_bonus):.1f})") # Display rounded contribution
                            passive_ability_mods_found = True
        if not passive_ability_mods_found:
            print("    - None")

        # Item Mods
        item_stats = self.inventory.get_stat_modifiers()
        print("  Item Mods:")
        print(f"    - Damage (from items): +{item_stats.get('damage', 0):.1f}")
        print(f"    - Mitigation (from items): +{item_stats.get('mitigation', 0):.1f}")
        print(f"    - Finesse (from items): +{item_stats.get('finesse', 0):.1f}")
        print(f"    - Attack Mod (from items): +{item_stats.get('attack', 0):.1f}")
        print(f"    - Defense Mod (from items): +{item_stats.get('defense', 0):.1f}")
        print(f"    - Speed Mod (from items): +{item_stats.get('speed', 0):.1f}")

        # Final Calculated Stats (after update_stats would have run)
        print("  Final Calculated Stats (including all mods):")
        print(f"    - Attack: {self.attack:.1f}, Defense: {self.defense:.1f}, Speed: {self.speed:.1f}")
        print(f"    - Damage: {self.damage:.1f}, Mitigation: {self.mitigation:.1f}, Finesse: {self.finesse:.1f}")
        print("--- End Stat Breakdown ---\n")


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
            "max_weave": self.max_weave,
            "current_weave": self.current_weave,
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
        instance.max_weave = data.get("max_weave", instance.weave_base) # Restore saved max_weave
        instance.current_weave = data.get("current_weave", instance.max_weave)
        
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

    def add_condition(self, condition_name: str, duration: int, potency: int, source_name: str, message_log_func: Callable[[str], None]):
        """Adds a condition to the entity."""
        self.active_conditions[condition_name] = {"duration": duration, "potency": potency, "source": source_name}
        message_log_func(f"{self.name} is now {condition_name} (Potency: {potency}, Duration: {duration} turns).")
        self.update_stats() # Recalculate if condition applies immediate stat mods

    def has_condition(self, condition_name: str) -> bool:
        """Checks if the entity has a specific active condition."""
        return condition_name in self.active_conditions

    def add_temporary_stat_mod(self, stat_name: str, amount: float, duration: int, source_name: str, message_log_func: Callable[[str], None]):
        """Adds a temporary modifier to a specific stat."""
        # For simplicity, new applications overwrite old ones for the same stat.
        # Could be enhanced to stack or refresh duration.
        self.temporary_stat_mods[stat_name] = {"amount": amount, "duration": duration, "source": source_name}
        if amount >= 0:
            message_log_func(f"{self.name} gains a temporary bonus to {stat_name} (+{amount:.1f}) from {source_name} for {duration} turns.")
        else:
            message_log_func(f"{self.name} suffers a temporary penalty to {stat_name} ({amount:.1f}) from {source_name} for {duration} turns.")
        self.update_stats() # Recalculate stats immediately

    def has_ability(self, ability_id: str) -> bool:
        """Checks if the entity has a specific ability."""
        return ability_id in self.abilities

    def process_conditions_at_turn_start(self, message_log_func: Callable[[str], None]):
        """Applies effects of conditions at the start of the entity's turn (e.g., DoTs)."""
        if not message_log_func: message_log_func = lambda x: print(x)
        
        conditions_to_remove = []
        for name, data in list(self.active_conditions.items()): # Iterate over a copy for safe modification
            if name == "burning":
                damage = data.get("potency", 1) # Damage based on potency
                message_log_func(f"{self.name} takes {damage} damage from burning.")
                self.take_damage(damage, message_log_func, combat=False) # combat=False to bypass mitigation for DoT
                if self.is_dead():
                    message_log_func(f"{self.name} succumbs to the flames.")
                    # Combat end will be handled by World
            # Add other conditions like "poisoned" here

    def process_conditions_at_turn_end(self, message_log_func: Callable[[str], None]):
        """Decrements duration of active conditions. Removes expired ones."""
        if not message_log_func: message_log_func = lambda x: print(x)

        expired_conditions = []
        for name, data in self.active_conditions.items():
            data["duration"] -= 1
            if data["duration"] <= 0:
                expired_conditions.append(name)
            else:
                message_log_func(f"{name} on {self.name} has {data['duration']} turns remaining.")


        for name in expired_conditions:
            del self.active_conditions[name]
            message_log_func(f"{name} has worn off from {self.name}.")
        
        # Also process temporary stat mods
        expired_temp_mods = []
        for stat, mod_info in self.temporary_stat_mods.items():
            mod_info["duration"] -=1
            if mod_info["duration"] <= 0:
                expired_temp_mods.append(stat)
        
        removed_mod = False
        for stat in expired_temp_mods:
            del self.temporary_stat_mods[stat]
            message_log_func(f"Temporary bonus to {stat} on {self.name} has worn off.")
            removed_mod = True

        if expired_conditions or removed_mod:
            self.update_stats() # Recalculate stats if any condition/mod expired