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

    def set_items(self, value):
        self.all_items = value

    def get_items(self):
        return self.all_items

    def add_to_stored_items(self, value):
        # print('Attempting to add {}'.format(value.name))
        self.stored_items.append(value)
        self.owned_items.append(value)

    def equip_item(self, value):
        # print('Attempting to equip {} type {}'.format(value.name, value.type))
        if value.type in EQUIPABLE_TYPES:
            if value.type == 'weapon':
                # self.stow_item(self.equipped_items['Held'])
                self.equipped_items['Held'] = self.stored_items.pop(self.stored_items.index(value))
                print('Equipped {} in hands.\n'.format(self.equipped_items['Held'].name))

            elif value.type == 'armor':
                # self.stow_item(self.equipped_items['Body'])
                self.equipped_items['Body'] = self.stored_items.pop(self.stored_items.index(value))
                print('Equipped {} on body.\n'.format(self.equipped_items['Body'].name))
            
            elif value.type == 'trinket':
                if value not in self.equipped_items['Trinkets']:
                    self.equipped_items['Trinkets'].append(value)
                    self.stored_items.remove(value)
                    print('Equipped {} as a trinket.\n'.format(self.equipped_items['Trinkets'][-1].name))

        else:
            print('You can not equip {}.'.format(value))

    def stow_item(self, value):
        if value.type == 'weapon':
            self.equipped_items['Held'] = None
            self.stored_items.append(self.equipped_items['Held'])
            print('Stowed {} in bag'.format(value.name))
        elif value.type == 'armor':
            self.equipped_items['Body'] = None
            self.stored_items.append(self.equipped_items['Body'])
            print('Stowed {} in bag'.format(value.name))

    def open_bag(self):
        # for i in self.stored_items:
            # print('stored item {}'.format(i))
        print('You open your worn rucksack and carefully arrange the conetnts around you.')
        print()
        """
        if self.equipped_items['Held'] is not None:
            print('You are currently weilding a {} as your weapon.'.format(self.equipped_items['Held'].name))
        if self.equipped_items['Body'] is not None:
            print('You are currently wearing {} for armor.'.format(self.equipped_items['Body'].name))
        
        if self.equipped_items['Trinkets']:
            formated_trinkets = ''
            for i, v in enumerate(self.equipped_items['Trinkets']):
                if i == len(self.equipped_items['Trinkets']) - 1:
                    trinket = '{}'.format(v.name)
                else:
                    trinket = '{}, '.format(v.name)
                formated_trinkets += trinket
                
            print('You are currently wearing {} as your trinkets.'.format(formated_trinkets))
        print()
        """
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