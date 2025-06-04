from abc import ABC, abstractmethod


TYPE_LIST = ['weapon', 'armor', 'crafting', 'wealth', 'trinket']
EQUIPABLE_TYPES = ['weapon', 'armor', 'trinket']


class Inventory():
    def __init__(self) -> None:
        self.stored_items = []
        self.equipped_items = {'Main hand': None, 'Off hand': None, 'Body': None, 'Trinkets': []}
        self.all_items = []

    def set_items(self, value):
        self.all_items = value

    def add_to_stored_items(self, value):
        print('Attempting to add {}'.format(value))

        for i, k in enumerate(self.all_items):
            if k.name == value:
                self.stored_items.append(k)
                break
            else:
                print('Item {} is not {}'.format(value, k.name))

    def equip_item(self, value):
        if value.type in EQUIPABLE_TYPES:
            if value.type == 'weapon':
                print('1. Main hand')
                print('2. Off hand')
                i = int(input('Which hand will you weild this with? '))
                
                if i == 1:
                    self.stored_items.append(self.equipped_items['Main hand'])
                    self.equipped_items['Main hand'] = self.stored_items.pop(self.stored_items.index(value))
                    print('Equipped {} in main hand'.format(self.equipped_items['Main hand'].name))

                elif i == 2:
                    self.stored_items.append(self.equipped_items['Off hand'])
                    self.equipped_items['Off hand'] = self.stored_items.pop(self.stored_items.index(value))
                    print('Equipped {} in off hand'.format(self.equipped_items['Off hand'].name))
            
            elif value.type == 'armor':
                self.stored_items.append(self.equipped_items['Body'])
                self.equipped_items['Body'] = self.stored_items.pop(self.stored_items.index(value))
                print('Equipped {} on body'.format(self.equipped_items['Body'].name))
            
            elif value.type == 'trinket':
                self.equipped_items['Trinkets'].append(value)
                print('Equipped {} as a trinket'.format(self.equipped_items['Trinkets'][-1].name))

        else:
            print('You can not equip {}'.format(value))