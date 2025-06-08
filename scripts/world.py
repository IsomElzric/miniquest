# scripts/world.py
from abc import ABC, abstractmethod
from scripts.combat import Combat
from scripts.entity import Entity
from scripts.builder import Builder # Ensure Builder is imported
from scripts.location import Location
from scripts.inventory import Inventory
from scripts.loot import Loot
from scripts.day_cycle import DayCycle # Import the new DayCycle class
import sys
import os
import random

# Add these lines at the top of world.py to enable logging
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')


# Path constants are now managed by Builder and __main__.py using absolute paths

class World():
    def __init__(self) -> None:
        print("--- World.__init__ called! ---") # TRACE 1: See if World is initialized multiple times
        # --- CRITICAL FIX: Initialize message_log FIRST ---
        self.message_log = []
        self.append_message("Welcome to Miniquest!")

        # --- Pass message_log to Builder ---
        self.builder = Builder(self.append_message) # Pass the method, not the list

        self.day_cycle = DayCycle(self.append_message) # Instantiate DayCycle
        self.loot = Loot()
        self.current_area = Location() # This defaults to 'Unset'
        self.day_cycle.message_log(f"Hour: {self.day_cycle.hour}") # Log initial hour

        # --- Initialize Player and its dependencies FIRST ---
        self.player = Entity()
        # The character creation logic can be a bit tricky. If player is not created until later,
        # its inventory/stats won't be ready immediately.
        # It's better to ensure self.player is fully set up if self.player.update_stats() is called early.
        self.enemy_list = self.builder.build_enemies()
        self.all_items = self.builder.build_items()
        self.player.inventory.set_items(self.all_items)
        self.loot.set_items(self.all_items)
        # Note: self.player will be further configured by self.create_character() later if called from __main__.py

        # --- Now that player exists, initialize areas and set initial location ---
        self.area_list = self.builder.build_areas()
        self.set_location('Lastholm')
        self.camp = 'Lastholm'
        # print(f"DEBUG: After set_location('Lastholm'), current_area is now: {self.current_area.name}")

        # New state for handling travel flow
        self.in_travel_selection_mode = False
        self.available_travel_destinations = []

        # New state for interactive combat
        self.active_combat_instance = None
        self.current_combat_enemy = None
        self.is_player_combat_turn = False # True if waiting for player's combat input
        self.player_must_flee_combat = False # New flag for defeat state

        # New state for post-combat loot decision
        self.in_loot_decision_mode = False
        self.pending_loot_item = None


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
        # print(f"DEBUG: Player created. Player name: {self.player.name}")

    def set_location(self, value):
        # print(f"DEBUG: set_location called with value: '{value}'")
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
                # If the new location is a camp, transfer carried items to strongbox
                if self.current_area.name == self.camp:
                    self.player.inventory.transfer_carried_to_strongbox(self.append_message)
                    self.append_message('') # Add spacing
                # print(f"DEBUG: set_location found '{value}'. current_area set to: {self.current_area.name}")
                break
        if not found:
            self.append_message(f"Error: Area '{value}' not found in area_list.")
            # print(f"DEBUG: Error: Area '{value}' not found in area_list during set_location. Available: {[a.name for a in self.area_list]}")

    def display_current_area(self):
        # Ensure player stats are updated before displaying.
        # This implicitly relies on player being created. If it's not, this might error.
        self.player.update_stats()
        self.append_message(f"Current location: {self.current_area.name}") # Log the name
        # The description is already a formatted string from Location.description setter
        self.append_message(self.current_area.description) # Log the description as is
        # print(f"DEBUG: Displaying area: {self.current_area.name}")

    def increment_time(self, value):
        day_ended = self.day_cycle.increment_hour(value)
        if day_ended:
            self.rest()

    def rest(self):
        self.day_cycle.reset_day() # Use DayCycle to reset time
        self.player.reset_health()
        self.set_location(self.camp)
        # transfer_carried_to_strongbox will be called by set_location if current_area becomes camp
        # self.player.inventory.transfer_carried_to_strongbox(self.append_message) # Already handled by set_location
        # Message about resting and new dawn is now handled by DayCycle and set_location/display_current_area
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

        if self.is_player_combat_turn: # Check if we are expecting a combat command
            if choice_text == "Attack":
                return self._player_attack_action()
            elif choice_text == "Flee":
                return self._player_flee_action()
            else:
                self.append_message(f"'{choice_text}' is not a valid combat action now.")
                return "player_combat_turn" # Stay in player's turn, show options again

        if self.player_must_flee_combat:
            if choice_text == "Flee Battle": # Or simply "Flee" if button text is just "Flee"
                self.player_defeated_retreat() # This handles messages, health, location to camp
                self.player_must_flee_combat = False # Reset flag
                # This new state signals GameView to pause and then refresh to camp
                return "returned_to_camp_after_defeat"
            else:
                self.append_message("You are too weak to do anything but flee.")
                return "player_defeated_must_flee" # Stay in this state, forcing flee

        if self.in_loot_decision_mode:
            if choice_text == "Take Item":
                if self.pending_loot_item:
                    # add_item_to_inventory in loot.py now uses the inventory's capacity-aware method
                    # It will log success or failure (due to capacity)
                    self.loot.add_item_to_inventory(self.player, self.pending_loot_item, self.append_message) 
                self._end_loot_decision_phase()
                self.display_current_area() # Refresh area description
                return "area_description"
            elif choice_text == "Drop Loot": # New option if player can't carry
                if self.pending_loot_item:
                    self.append_message(f"You discard the {self.pending_loot_item.name}.")
                    self.append_message('')
                self._end_loot_decision_phase()
                self.display_current_area() # Refresh area description
                return "area_description"
            elif choice_text == "Leave":
                self.append_message(f"You decide to leave the {self.pending_loot_item.name if self.pending_loot_item else 'item'}.")
                self.append_message('')
                self._end_loot_decision_phase()
                self.display_current_area() # Refresh area description
                return "area_description"

        if self.in_travel_selection_mode:
            return self.handle_travel_choice(choice_text)

        if 'Fight' in choice_text:
            if not self.current_area.enemies:
                self.append_message('There are no enemies here to fight...')
                return "area_description" # Stay in description mode
            else:
                return self.initiate_combat() # Initiate combat and return its initial state
        elif 'Travel' in choice_text:
            self.append_message("Where would you like to travel?")
            self.in_travel_selection_mode = True
            # CRITICAL FIX: Make a copy of the connections list
            self.available_travel_destinations = list(self.get_travel_options())
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


    def initiate_combat(self):
        """Sets up combat, determines the first attacker, and returns the game state."""
        self.player.print_entity(self.append_message) # Pass log_func to print_entity
        # print_entity already adds a blank line
        self.current_combat_enemy = self.generate_enemy()

        if self.current_combat_enemy is None:
            self.append_message("Combat cannot start as no enemy was generated.")
            self.is_player_combat_turn = False # Ensure flag is reset
            return "area_description"

        self.active_combat_instance = Combat(self.current_area.name, self.loot, self.append_message)
        self.active_combat_instance.add_combatant(self.player)
        self.active_combat_instance.add_combatant(self.current_combat_enemy)
        self.active_combat_instance.print_combatants() # Logs who acts first
        self.append_message('') # Add spacing

        first_attacker = self.active_combat_instance.combatant_list[0]
        if first_attacker.is_player:
            self.is_player_combat_turn = True
            self.append_message("--- Your Turn ---")
            self.append_message("It's your turn!")
            return "player_combat_turn"
        else:
            # Enemy attacks first, then it will be player's turn (if player survives)
            self.is_player_combat_turn = False # Not player's turn yet
            return self._process_enemy_turn()

    def _player_attack_action(self):
        """Processes the player's attack choice."""
        if not self.active_combat_instance or not self.current_combat_enemy:
            self.append_message("Error: Combat is not active.")
            self._end_combat_sequence()
            return "area_description"

        self.active_combat_instance.execute_player_attack(self.player, self.current_combat_enemy)
        self.is_player_combat_turn = False # Player's turn is over

        if self.current_combat_enemy.is_dead():
            self.append_message(f"You have defeated {self.current_combat_enemy.name}!")
            # self.append_message('') # Spacing will be handled by loot messages or lack thereof
            
            dropped_item = self.active_combat_instance.generate_loot(self.player, self.current_combat_enemy)
            self.increment_time(1)
            self._end_combat_sequence()

            if dropped_item:
                self.pending_loot_item = dropped_item
                self.in_loot_decision_mode = True
                return "loot_decision" # New state for GUI
            else:
                return "area_description" # No loot, combat over
        else:
            # Enemy's turn
            return self._process_enemy_turn()

    def _process_enemy_turn(self):
        """Processes the enemy's turn and returns the next game state."""
        if not self.active_combat_instance:
            self.append_message("Error: Combat instance not active for enemy turn.")
            self._end_combat_sequence()
            return "area_description"

        if self.current_combat_enemy is None: # Explicitly check if the enemy object exists
            self.append_message("Error: No valid enemy for this turn.")
            self._end_combat_sequence()
            return "area_description"

        # Safeguard: if enemy is already dead, end combat. This shouldn't normally be hit
        # if the player's attack action correctly ends combat.
        if self.current_combat_enemy.is_dead(): # Now safe to call .is_dead()
            self.append_message(f"{self.current_combat_enemy.name} was already defeated.") # Safe to call .name
            self._end_combat_sequence()
            return "area_description"

        self.append_message(f"--- {self.current_combat_enemy.name}'s Turn ---") # Now safe to call .name
        # self.append_message(f"It's {self.current_combat_enemy.name}'s turn.") # Redundant with header
        self.active_combat_instance.execute_enemy_attack(self.current_combat_enemy, self.player)

        if self.player.is_dead():
            self.append_message("You have been overcome and cannot continue fighting.") # Inform player
            self.increment_time(1) # Combat took time
            self._end_combat_sequence()
            self.player_must_flee_combat = True # Set flag
            return "player_defeated_must_flee" # New state for GameView
        else:
            # Back to player's turn
            self.is_player_combat_turn = True
            self.append_message("--- Your Turn ---")
            self.append_message("It's your turn!")
            return "player_combat_turn"

    def _player_flee_action(self):
        """Processes the player's flee choice."""
        self.append_message("You attempt to flee...")
        # For now, fleeing is always successful.
        # TODO: Implement flee chance, penalties, or enemy opportunity attacks in the future.
        flee_successful = True 
        if flee_successful:
            self.append_message("You successfully fled from combat!")
            self.append_message('') # Add spacing
            self.increment_time(1) # Fleeing takes time
            self._end_combat_sequence()
            self.display_current_area() # Refresh current area description after fleeing
            return "area_description"
        # else: # If flee fails
        #     self.append_message("You failed to flee!")
        #     self.is_player_combat_turn = False # Player's turn is over
        #     return self._process_enemy_turn() # Enemy gets a turn

    def _end_combat_sequence(self):
        """Cleans up after combat ends."""
        self.active_combat_instance = None
        self.current_combat_enemy = None
        self.is_player_combat_turn = False
        self.player_must_flee_combat = False # Reset flee flag when combat ends
        self._end_loot_decision_phase() # Also clear loot state if combat ends abruptly

    def _end_loot_decision_phase(self):
        self.in_loot_decision_mode = False
        self.pending_loot_item = None

    def player_defeated_retreat(self):
        """Handles the state changes and messages when the player is defeated and flees."""
        self.append_message("You had to flee back to safety.")
        self.player.reset_health() # Restore health
        self.set_location(self.camp) # Move to camp - this will trigger display_current_area in GameView
        self.day_cycle.reset_day() # Reset time via DayCycle
        self.append_message(f"You find yourself back at your camp: {self.current_area.name}.")
        self.append_message("A new day begins, offering a chance to recover from your ordeal.")
        # GameView will handle displaying these messages and transitioning.

    def generate_enemy(self):
        enemy_pool = self.current_area.get_enemies()

        if not enemy_pool:
            self.append_message("No enemies to generate in this area.")
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
            cloned_enemy.scaling() # Apply level-based scaling
            
            # Apply night modifier
            night_modifier = self.day_cycle.get_enemy_night_modifier()
            cloned_enemy.apply_night_scaling(night_modifier, self.append_message)
            cloned_enemy.update_stats() # Update stats after scaling
            # or a specific clone_enemy in Builder that returns an Entity object.
            # Assuming Builder.clone_entity handles both or you have a dedicated clone_enemy.

            # These messages are appended after cloning the entity
            cloned_enemy.print_entity(self.append_message) # Prints entity stats to log
            # print_entity already adds a blank line
            self.append_message(f"A {cloned_enemy.name} appeared!")
            return cloned_enemy
        else:
            self.append_message(f"Error: Could not find enemy template for '{selected_enemy_name}'.")
            return None

    def prepare(self):
        self.append_message("You enter your camp and begin to prepare.")
        # self.player.print_entity(self.append_message) # Player stats are in the banner
        # The GUI will now handle displaying inventory options.