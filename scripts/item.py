from abc import ABC, abstractmethod


TYPE_LIST = ['weapon', 'armor', 'crafting', 'wealth', 'trinket']


class Item(ABC):
    def __init__(self) -> None:
        self._name = ''
        self._description = ''
        self._type = ''
        self.rarity = 'Common'
        self._stat_modifiers = {}
        self.damage = 0
        self.mitigation = 0
        self.finesse = 0
        self.spawn_location = []

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        removed_suffix = value.removesuffix('.txt')
        self._name = removed_suffix.capitalize()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        for i in value:
            if i != '':
                self._description += i + '\n'
            else:
                value.remove(i)

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        if value not in TYPE_LIST:
            self._type = 'Unknown'

    @property
    def stat_modifiers(self):
        return self._stat_modifiers
    
    @stat_modifiers.setter
    def stat_modifiers(self, value):
        self._damage = value['damage']
        self._mitigation = value['mitigation']
        self._finesse = value['finesse']
        self.stat_modifiers = value