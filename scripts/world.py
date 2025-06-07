# scripts/world.py
from abc import ABC, abstractmethod
from scripts.combat import Combat
from scripts.entity import Entity
from scripts.builder import Builder # Ensure Builder is imported
from scripts.location import Location
from scripts.inventory import Inventory
from scripts.loot import Loot
import sys
import os
import random

# Add these lines at the top of world.py to enable logging
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')


LOCATION_PATH = 'assets/locations/'
ENEMY_PATH = 'assets/enemies/'
ART_PATH = 'assets/art/'
SOUND_PATH = 'assets/sound/'


class World():
    def __init__(self) -> None:
        print("--- World.__init__ called! ---") # TRACE 1: See if World is initialized multiple times
        # --- CRITICAL FIX: Initialize message_log FIRST ---
        self.message_log = []
        self.append_message("Welcome to Miniquest!")

        # --- Pass message_log to Builder ---
        self.builder = Builder(self.message_log)

        self.loot = Loot()

        self.time = 0
        self.current_area = Location() # This defaults to 'Unset'
        print(f"DEBUG: Initial current_area after Location() creation: {self.current_area.name}") # TRACE 2

        self.area_list = self.builder.build_areas()
        print(f"DEBUG: Builder finished building areas. Found {len(self.area_list)} areas.") # TRACE 3
        # TRACE 4: Check if 'Lastholm' is actually in the loaded list
        lastholm_found_in_list = False
        for area in self.area_list:
            if area.name == 'Lastholm':
                lastholm_found_in_list = True
                print(f"DEBUG: 'Lastholm' object found in area_list: {area}")
                break
        if not lastholm_found_in_list:
            print(f"ERROR: 'Lastholm' was NOT found in area_list. Available areas: {[a.name for a in self.area_list]}")

        self.set_location('Lastholm')
        self.camp = 'Lastholm' # Ensure this is also correctly set later, though current_area is the main focus

        print(f"DEBUG: After set_location('Lastholm'), current_area is now: {self.current_area.name}") # TRACE 5

        self.player = Entity()
        # The character creation logic can be a bit tricky. If player is not created until later,
        # its inventory/stats won't be ready immediately.
        # It's better to ensure self.player is fully set up if self.player.update_stats() is called early.

        self.enemy_list = self.builder.build_enemies()

        self.all_items = self.builder.build_items()

        self.player.inventory.set_items(self.all_items)
        self.loot.set_items(self.all_items)

        # New state for handling travel flow
        self.in_travel_selection_mode = False
        self.available_travel_destinations = []


    def append_message(self, message):
        self.message_log.append(message)
        # Optional: Limit log size to prevent excessive memory use
        if len(self.message_log) > 100: # Keep last 100 messages
            self.message_log = self.message_log[-100:]

    def get_messages(self):
        messages = list(self.message_log) # Get a copy
        self.message_log.clear() # Clear the internal log after retrieval
        return messages

    def create_character(self):
        # Builder.create_character now sets default player properties
        self.builder.create_character()
        self.player = self.builder.get_player()
        self.player.is_player = True
        self.append_message(f"You have created a new character: {self.player.name}!")
        self.append_message(f"Current Stats: Lvl {self.player.level}, HP {self.player.current_health}/{self.player.max_health}, Atk {self.player.attack}, Def {self.player.defense}, Spd {self.player.speed}")
        print(f"DEBUG: Player created. Player name: {self.player.name}") # TRACE for character creation

    def set_location(self, value):
        print(f"DEBUG: set_location called with value: '{value}'") # TRACE 6
        found = False
        for i, v in enumerate(self.area_list):
            if v.name == value:
                self.current_area = v
                # This complex 'camp' logic should probably be encapsulated or simplified
                # For now, keeping it as is.
                if self.current_area.name in ['Lastholm', 'Aethelwood', 'Scorlends', 'Shadowsun']:
                    self.camp = self.current_area.name
                elif self.current_area.name == 'Shadowed residential blocks':
                    self.camp = 'Broken hearth'
                elif self.current_area.name == 'Petrified grove':
                    self.camp = 'Quiet glade'
                elif self.current_area.name == 'Scavenger\'s ridge':
                    self.camp = 'Iron spring'
                elif self.current_area.name == 'Magma veins':
                    self.camp = 'Last anvil'
                found = True
                print(f"DEBUG: set_location found '{value}'. current_area set to: {self.current_area.name}") # TRACE 7
                break
        if not found:
            self.append_message(f"Error: Area '{value}' not found in area_list.")
            print(f"DEBUG: Error: Area '{value}' not found in area_list during set_location. Available: {[a.name for a in self.area_list]}") # TRACE 8

    def display_current_area(self):
        # Ensure player stats are updated before displaying.
        # This implicitly relies on player being created. If it's not, this might error.
        self.player.update_stats()
        self.append_message(f"Current location: {self.current_area.name}")
        # Assuming description is a list of strings, join them
        self.append_message(" ".join(self.current_area.description))
        print(f"DEBUG: Displaying area: {self.current_area.name}") # TRACE 9

    def increment_time(self, value):
        self.time += value
        self.append_message(f"You are on hour {self.time}")

        if self.time >= 12:
            self.append_message('Exhaustion takes you')
            self.rest()
        elif self.time > 8:
            self.append_message('Night has fallen')
        elif self.time == 8:
            self.append_message('Dusk is upon you')
        elif self.time < 8:
            self.append_message('You have daylight yet')

    def start_day(self):
        self.time = 0
        self.append_message('A new dawn breaks')

    def rest(self):
        self.start_day()
        self.player.reset_health()
        self.set_location(self.camp)
        self.append_message(f"You rested and recovered. You are now at your camp: {self.current_area.name}.")

    def display_location_options(self):
        options = ['Fight', 'Travel', 'Rest']
        if self.current_area.name == self.camp:
            options.append('Prepare')
        return options

    def get_travel_options(self):
        """
        Returns a list of location names that the player can travel to from the current area.
        """
        if self.current_area and self.current_area.connections:
            return self.current_area.get_connections()
        return []

    def handle_player_choice(self, choice_text):
        """
        A centralized method for the GUI to call based on player action choice.
        Returns a string indicating the desired display mode for GameView.
        """
        self.append_message(f"You chose: {choice_text}") # Log the raw choice
        logging.debug(f"Handling player choice: '{choice_text}'")

        if self.in_travel_selection_mode:
            return self.handle_travel_choice(choice_text)

        if 'Fight' in choice_text:
            if not self.current_area.enemies:
                self.append_message('There are no enemies here to fight...')
                return "area_description" # Stay in description mode
            else:
                self.fight()
                self.increment_time(1)
                return "combat_log" # Switch to combat log mode
        elif 'Travel' in choice_text:
            self.append_message("Where would you like to travel?")
            self.in_travel_selection_mode = True
            # Populate available_travel_destinations for the GUI
            self.available_travel_destinations = self.get_travel_options()
            return "travel_options" # Indicate to GUI to show travel options
        elif 'Rest' in choice_text:
            self.rest()
            return "area_description" # Resting usually just updates the area description
        elif 'Prepare' in choice_text:
            self.prepare()
            return "area_description" # Preparation details would show up in log/description area

        else:
            self.append_message(f"'{choice_text}' is not a valid action or you cannot do that here.")
            return "area_description" # Default to showing message in log for invalid actions


    def handle_travel_choice(self, destination_name):
        """
        Handles the actual travel action when the player has selected a destination
        from the travel menu.
        """
        logging.debug(f"Handling travel choice: '{destination_name}'")

        if destination_name == "Stay": # Added "Stay" option for cancelling travel
            self.append_message("You decide not to travel at this time.")
            self.in_travel_selection_mode = False
            self.available_travel_destinations.clear()
            self.display_current_area()
            return "area_description"

        # Check if the chosen destination is valid from current_area's connections
        if destination_name in self.current_area.get_connections():
            self.set_location(destination_name) # THIS IS THE CRITICAL LINE
            self.increment_time(1) # Travel takes time
            self.append_message(f"You traveled to {destination_name}.")
            self.in_travel_selection_mode = False # Exit travel selection mode
            self.available_travel_destinations.clear() # Clear cache
            self.display_current_area() # Update description for new area
            return "area_description"
        else:
            self.append_message(f"You cannot travel to '{destination_name}' from here.")
            self.append_message("Please choose a valid destination or 'Stay'.")
            # Remain in travel selection mode if invalid choice
            return "travel_options"


    def fight(self):
        self.player.print_entity(self.append_message) # Pass log_func to print_entity

        enemy = self.generate_enemy()

        # Handle case where generate_enemy returns None (no enemies in area or error)
        if enemy is None:
            self.append_message("Combat cannot start as no enemy was generated.")
            return # Exit fight function if no enemy

        fight = Combat(self.current_area.name, self.loot, self.append_message) # Pass append_message
        fight.add_combatant(self.player)
        fight.add_combatant(enemy)
        fight.print_combatants() # This will now append to log

        # Combat loop will generate many messages.
        fight.start_combat()

        # After combat, check results
        if not self.player.is_dead() and enemy.is_dead():
            self.append_message(f"You defeated the {enemy.name}!")

            dropped_item = self.loot.get_drop_by_area(enemy, self.current_area.name) # Pass defeated enemy and area
            if dropped_item:
                self.append_message(f"You found a {dropped_item.name}!")
                self.player.inventory.add_to_stored_items(dropped_item)
            else:
                self.append_message(f"The {enemy.name} yielded no loot.")

        elif self.player.is_dead():
            self.append_message("You have been defeated...")
            # Consider adding game over state or returning to main menu
            # For now, the GameView will detect player.is_dead() and handle it.


    def generate_enemy(self):
        enemy_pool = self.current_area.get_enemies()

        if not enemy_pool:
            return None

        selected_enemy_name = random.choice(enemy_pool)

        # Find the template in self.enemy_list
        enemy_template = None
        for v in self.enemy_list:
            if v.name == selected_enemy_name: # Ensure names match
                enemy_template = v
                break

        if enemy_template:
            # --- Use the builder to clone the enemy ---
            cloned_enemy = self.builder.clone_enemy(enemy_template)            # NOTE: If clone_enemy is only for Player, then you need a generic clone_entity
            # or a specific clone_enemy in Builder that returns an Entity object.
            # Assuming Builder.clone_entity handles both or you have a dedicated clone_enemy.

            # These messages are appended after cloning the entity
            cloned_enemy.print_entity(self.message_log) # Prints entity stats to log
            self.append_message(f"A {cloned_enemy.name} appeared!")
            return cloned_enemy
        else:
            self.append_message(f"Error: Could not find enemy template for '{selected_enemy_name}'.")
            return None

    def prepare(self):
        self.append_message("You enter your camp and begin to prepare.")
        self.player.print_entity(self.append_message)
        self.append_message("What would you like to do in preparation? (Inventory, Crafting, etc.)")


"""
from abc import ABC, abstractmethod
from scripts.combat import Combat
from scripts.entity import Entity
from scripts.builder import Builder
from scripts.location import Location
from scripts.inventory import Inventory
from scripts.loot import Loot
import sys
import os
import random


LOCATION_PATH = 'assets/locations/'
ENEMY_PATH = 'assets/enemies/'
ART_PATH = 'assets/art/'
SOUND_PATH = 'assets/sound/'


class World():
    def __init__(self) -> None:
        self.builder = Builder()
        self.loot = Loot()
        
        self.time = 0
        self.current_area = Location()
        self.area_list = self.builder.build_areas()

        self.set_location('Lastholm')
        self.camp = 'Lastholm'

        self.player = Entity()
        
        self.enemy_list = self.builder.build_enemies()
        
        self.all_items = self.builder.build_items()
        # for i in self.all_items:
            # print('Item {} built and added to World'.format(i.name))

        self.player.inventory.set_items(self.all_items)
        self.loot.set_items(self.all_items)

    def create_character(self):
        self.builder.create_character()
        self.player = self.builder.get_player()
        self.player.is_player = True

    def set_location(self, value):
        for i, v in enumerate(self.area_list):
            # print('Looking for {} in {}'.format(value, v.name))
            if v.name == value:
                self.current_area = v
                # print('Found {} and set current location as {}'.format(value, self.current_area.name))
                if self.current_area.name in ['Lastholm', 'Aethelwood', 'Scorlends', 'Shadowsun']:
                    self.camp = self.current_area.name
                elif self.current_area.name == 'Shadowed residential blocks':
                    self.camp = 'Broken hearth'
                elif self.current_area.name == 'Petrified grove':
                    self.camp = 'Quiet glade'
                elif self.current_area.name == 'Scavenger\'s ridge':
                    self.camp = 'Iron spring'
                elif self.current_area.name == 'Magma veins':
                    self.camp = 'Last anvil'
                break
            else:
                # print('Area not found')
                pass
  
    def move_area(self):
        connections = self.current_area.get_connections()
        c = 1
        for i, n in enumerate(connections):
            print('{}. {}'.format(i + 1, n))
            c += 1
        print('{}. Stay'.format(c))
        print()
        new_location = input('What is your destination? ')
        print()

        try:
            index = 0
            try:
                index = int(new_location) - 1
            except:
                name = new_location.capitalize()
                index = connections.index(name)

            # print('Player has moved to {}'.format(value))
            self.set_location(connections[index])
            self.increment_time(self.current_area.travel_time)
            self.display_current_area()
        except:
            self.display_current_area()

    def display_current_area(self):
        self.player.update_stats()        
        print('Current location: {}'.format(self.current_area.name))
        print()
        print(self.current_area.description)
        print()
        print(self.display_location_options())

    def increment_time(self, value):
        self.time += value
        print('You are on hour {}'.format(self.time))

        if self.time >= 12:
            print('Exhaustion takes you')
            self.rest()
        elif self.time > 8:
            print('Night has fallen')
        elif self.time == 8:
            print('Dusk is upon you')
        elif self.time < 8:
            print('You have daylight yet')

    def start_day(self):
        self.time = 0
        print('A new dawn breaks')

    def rest(self):
        self.start_day()
        self.player.reset_health()
        self.set_location(self.camp)
        self.display_current_area()

    def display_location_options(self):
        print('1. Fight')
        print('2. Travel')
        print('3. Rest')
        if self.current_area.name == self.camp:
            print('4. Prepare')
        print()
        choice = input('What will you do? ')
        print()

        if int(choice) == 1:
            if not self.current_area.enemies:
                print('There are no enemies here...')
            else:
                self.fight()
                self.increment_time(1)
            self.display_current_area()

        elif int(choice) == 2:
            self.move_area()

        elif int(choice) == 3:    
            self.rest()

        elif int(choice) == 4:
            self.prepare()
        else:
            sys.exit()

    def fight(self):
        fight = Combat(self.current_area.name, self.loot)
        player = self.player
        player.print_entity()

        enemy = self.generate_enemy()

        fight.add_combatant(player)
        fight.add_combatant(enemy)
        fight.print_combatants()
        fight.start_combat()

    def generate_enemy(self):
        # print('Generating enemy')
        
        enemy_pool = self.current_area.get_enemies()
        # print(enemy_pool)
        
        selected_enemy = random.choice(enemy_pool)
        # print('Selected enemy {}'.format(selected_enemy))
        for i, v in enumerate(self.enemy_list):
            if v.name == selected_enemy:
                enemy = v
                enemy.scaling()
                enemy.update_stats()
                enemy.reset_health()
                enemy.print_entity()
                return enemy
            else:
                # print('No enemy found named {}'.format(selected_enemy))
                pass

    def prepare(self):
        self.player.print_entity()
        self.player.inventory.open_bag()
        print()
        self.display_current_area()
"""