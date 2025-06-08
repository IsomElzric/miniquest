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
            return True
        else:
            if message_log_func: # Optional logging
                message_log_func(f"You cannot carry any more {item_to_add.type} items.")
            return False

    def equip_item(self, value):
        # print('Attempting to equip {} type {}'.format(value.name, value.type))
        if value.type in EQUIPABLE_TYPES:
            # Ensure item is in stored_items before trying to pop/remove
            if value in self.stored_items:
                if value.type == 'weapon':
                    # self.stow_item(self.equipped_items['Held']) # Optional: auto-stow previous
                    self.equipped_items['Held'] = self.stored_items.pop(self.stored_items.index(value))
                    print('Equipped {} in hands.\n'.format(self.equipped_items['Held'].name)) # Keep for CLI, GUI would use message_log

                elif value.type == 'armor':
                    # self.stow_item(self.equipped_items['Body']) # Optional: auto-stow previous
                    self.equipped_items['Body'] = self.stored_items.pop(self.stored_items.index(value))
                    print('Equipped {} on body.\n'.format(self.equipped_items['Body'].name)) # Keep for CLI
                
                elif value.type == 'trinket':
                    if value not in self.equipped_items['Trinkets']:
                        self.equipped_items['Trinkets'].append(value)
                        self.stored_items.remove(value) # Item is now equipped, remove from general storage
                        print('Equipped {} as a trinket.\n'.format(self.equipped_items['Trinkets'][-1].name)) # Keep for CLI
            else:
                print(f"Cannot equip {value.name} as it's not in your stored items (perhaps already equipped?).")
        else:
            print('You can not equip {}.'.format(value.name))

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