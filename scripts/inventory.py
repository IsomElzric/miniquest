from abc import ABC, abstractmethod
from collections import Counter


TYPE_LIST = ['weapon', 'armor', 'crafting', 'wealth', 'trinket']
EQUIPABLE_TYPES = ['weapon', 'armor', 'trinket']


class Inventory():
    def __init__(self) -> None:
        self.stored_items = []
        self.equipped_items = {'Held': None, 'Body': None, 'Trinkets': []}
        self.owned_items = []
        self.all_items = []
        self.income = 0
        self.strongbox_items = [] # For items stored at camp

        # Define maximum number of *un-equipped* items of each type the player can carry
        self.carry_capacities = {
            'weapon': 1,
            'crafting': 3,
            'wealth': 5,
            'trinket': 2
        }

    def set_items(self, value):
        self.all_items = value

    def get_items(self):
        return self.all_items

    def count_carried_items_by_type(self, item_type_to_count):
        """Counts how many items of a specific type are currently in stored_items (carried)."""
        count = 0
        for item in self.stored_items:
            if item.type == item_type_to_count:
                count += 1
        return count

    def can_carry_item(self, item_to_check):
        """Checks if the player has capacity to carry one more of the given item's type."""
        item_type = item_to_check.type
        if item_type in self.carry_capacities:
            current_count = self.count_carried_items_by_type(item_type)
            if current_count < self.carry_capacities[item_type]:
                return True
            else:
                # print(f"DEBUG: Cannot carry more {item_type}. Count: {current_count}, Capacity: {self.carry_capacities[item_type]}")
                return False
        return True # Default to true if type has no specific capacity (e.g., quest items later)

    def add_to_stored_items(self, item_to_add, message_log_func=None):
        # print('Attempting to add {}'.format(value.name))
        if self.can_carry_item(item_to_add):
            self.stored_items.append(item_to_add)
            self.owned_items.append(item_to_add) # Keep track of all items ever owned for loot rule purposes
            if message_log_func: # Optional logging
                message_log_func(f"{item_to_add.name} added to your bag.")
            # --- DEBUG ---
            print(f"DEBUG INV: Added '{item_to_add.name}' to owned_items. Current owned_items (names): {[oi.name for oi in self.owned_items]}")
            # --- END DEBUG ---
            return True
        else:
            if message_log_func: # Optional logging
                message_log_func(f"You cannot carry any more {item_to_add.type} items.")
            return False

    def equip_item(self, item_to_equip, source_location_name=None, message_log_func=None):
        """
        Equips an item. If an item is already in the slot, it's moved to the strongbox.
        item_to_equip: The item object to equip.
        source_location_name: String 'carried' or 'strongbox' indicating where the item comes from.
                              Defaults to 'carried' if None. (The old `equip_item` effectively assumed 'carried')
        message_log_func: Function to log messages.
        Returns True if successful, False otherwise.
        """
        if not message_log_func: message_log_func = lambda x: print(x) # Fallback logger

        if item_to_equip.type not in EQUIPABLE_TYPES:
            message_log_func(f"You cannot equip {item_to_equip.name} ({item_to_equip.type}).")
            return False

        source_list = None
        if source_location_name == "strongbox":
            source_list = self.strongbox_items
        elif source_location_name == "carried" or source_location_name is None: # Default to carried
            source_list = self.stored_items
            source_location_name = "carried" # Normalize for messages
        
        if source_list is None or item_to_equip not in source_list:
            message_log_func(f"Cannot equip {item_to_equip.name}: not found in {source_location_name} items.")
            # This might happen if the item was already equipped or list is out of sync.
            return False

        slot_to_equip = None
        # Determine the slot based on item type
        if item_to_equip.type == 'weapon': slot_to_equip = 'Held'
        elif item_to_equip.type == 'armor': slot_to_equip = 'Body'
        elif item_to_equip.type == 'trinket': slot_to_equip = 'Trinkets'

        # Handle un-equipping current item in the slot (move to strongbox)
        if slot_to_equip == 'Held' or slot_to_equip == 'Body':
            currently_equipped = self.equipped_items[slot_to_equip]
            if currently_equipped:
                message_log_func(f"Unequipping {currently_equipped.name} from {slot_to_equip} slot.")
                self.strongbox_items.append(currently_equipped) # Move old item to strongbox
                message_log_func(f"{currently_equipped.name} moved to strongbox.")
                self.equipped_items[slot_to_equip] = None
            self.equipped_items[slot_to_equip] = item_to_equip
            message_log_func(f"Equipped {item_to_equip.name} in {slot_to_equip} slot.")
        elif slot_to_equip == 'Trinkets':
            MAX_TRINKETS = 10 # Example limit
            if len(self.equipped_items['Trinkets']) >= MAX_TRINKETS:
                old_trinket = self.equipped_items['Trinkets'].pop(0) # Remove the oldest
                self.strongbox_items.append(old_trinket)
                message_log_func(f"Trinket slots full. Unequipping oldest trinket: {old_trinket.name}.")
                message_log_func(f"{old_trinket.name} moved to strongbox.")
            self.equipped_items['Trinkets'].append(item_to_equip)
            message_log_func(f"Equipped {item_to_equip.name} as a trinket.")
                
        # Remove item from its original source list (carried or strongbox)
        try:
            source_list.remove(item_to_equip)
        except ValueError:
             message_log_func(f"Warning: Could not remove {item_to_equip.name} from {source_location_name} list during equip.")

        # Add logging to show list contents after the operation
        message_log_func("--- Inventory State After Equip ---")
        message_log_func(f"Equipped: {self.equipped_items}") # Shows object representations
        message_log_func(f"Carried: {[item.name for item in self.stored_items]}")
        message_log_func(f"Strongbox: {[item.name for item in self.strongbox_items]}")
        message_log_func("---------------------------------")
        message_log_func("") # Spacing
        return True

    def drop_item(self, item_to_drop, source_location_name, message_log_func=None):
        """
        Removes (drops) an item from the specified inventory list (carried or strongbox).
        Does not currently handle dropping equipped items directly (they should be unequipped first).
        """
        if not message_log_func: message_log_func = lambda x: print(x)

        source_list = None
        if source_location_name == "carried":
            source_list = self.stored_items
        elif source_location_name == "strongbox":
            source_list = self.strongbox_items
        elif source_location_name.startswith("equipped_"):
            message_log_func(f"Cannot directly drop equipped item: {item_to_drop.name}. Please unequip it first.")
            return False # Or handle unequip then drop
        else:
            message_log_func(f"Unknown source location '{source_location_name}' for dropping {item_to_drop.name}.")
            return False

        if item_to_drop in source_list:
            source_list.remove(item_to_drop)
            # Note: item remains in self.owned_items unless you want a "permanently lose" mechanic.
            message_log_func(f"You dropped {item_to_drop.name} from your {source_location_name} items.")
            message_log_func("")
            return True
        else:
            message_log_func(f"Could not find {item_to_drop.name} in {source_location_name} items to drop.")
            return False

    def stow_item(self, value):
        if value.type == 'weapon':
            self.stored_items.append(self.equipped_items['Held'])
            self.equipped_items['Held'] = None
            print('Stowed {} in bag'.format(value.name))

        elif value.type == 'armor':
            self.stored_items.append(self.equipped_items['Body'])
            self.equipped_items['Body'] = None
            print('Stowed {} in bag'.format(value.name))

    def transfer_carried_to_strongbox(self, message_log_func):
        """Moves all items from stored_items (carried) to strongbox_items."""
        if not self.stored_items:
            message_log_func("Your carry bags are already empty.")
            return

        for item in self.stored_items:
            self.strongbox_items.append(item)
        self.stored_items.clear()
        message_log_func("You've transferred all carried items to your strongbox at camp.")

    def open_bag(self):
        # for i in self.stored_items:
            # print('stored item {}'.format(i))
        print('You open your worn rucksack and carefully arrange the contents around you.')
        print()

        consolidated_items = Counter(self.stored_items)
        for item, count in consolidated_items.items():
            if count > 1:
                item.ammount = count
            else:
                item.ammount = 1

        stored_item_set = set(self.stored_items)
        self.stored_items = list(stored_item_set)

        while True:
            for i, v in enumerate(self.stored_items):
                if v.ammount != 1:
                    print('{}. {} ({}) x{}'.format(i + 1, v.name, v.type, v.ammount))
                else:
                    print('{}. {} ({})'.format(i + 1, v.name, v.type))
            
            print()
            print('1. Inspect')
            print('2. Equip')
            print('3. Sell')
            print('4. Close bag')
            print()
            action = int(input('What would you like to do? '))

            if action == 1:
                choice = int(input('Which item would you like to inspect? '))
                print()
                self.stored_items[choice - 1].display()

            elif action == 2:
                choice = int(input('What would you like to equip? '))
                print()
                self.equip_item(self.stored_items[choice - 1])

            elif action == 3:
                choice = int(input("What would you like to sell? "))
                print()
                self.sell_wealth(self.stored_items[choice - 1])

            elif action == 4:
                break
        
    def get_stat_modifiers(self):
        total_stats = {'damage': 0, 'mitigation': 0, 'finesse': 0, 'attack': 0, 'defense': 0, 'speed': 0}

        if self.equipped_items['Held'] is not None: 
            total_stats['damage'] += self.equipped_items['Held'].damage
            total_stats['mitigation'] += self.equipped_items['Held'].mitigation
            total_stats['finesse'] += self.equipped_items['Held'].finesse

        if self.equipped_items['Body'] is not None:
            total_stats['damage'] += self.equipped_items['Body'].damage
            total_stats['mitigation'] += self.equipped_items['Body'].mitigation
            total_stats['finesse'] += self.equipped_items['Body'].finesse

        if self.equipped_items['Trinkets']:
            for i, v in enumerate(self.equipped_items['Trinkets']):
                total_stats['attack'] += v.attack
                total_stats['defense'] += v.defense
                total_stats['speed'] += v.speed
    
        return total_stats
    
    def sell_wealth(self, item):
        if item.ammount > 1:
            item.ammount -= 1
            self.income += item.worth
        else:
            self.stored_items.remove(item)
            self.income += item.worth