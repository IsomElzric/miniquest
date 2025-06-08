from abc import ABC, abstractmethod


TYPE_LIST = ['weapon', 'armor', 'crafting', 'wealth', 'trinket']


class Item(ABC):
    def __init__(self) -> None:
        self._name = ''
        self._description = ''
        self._type = ''
        self.ammount = 1
        
        self._stat_modifiers = {}
        self.damage = 0
        self.mitigation = 0
        self.finesse = 0

        self.attack = 0
        self.defense = 0
        self.speed = 0

        self.worth = 0

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
        # Join all lines from the file into a single string, separated by spaces.
        # Filter out empty strings to avoid excessive spacing.
        self._description = " ".join(line for line in value if line.strip())
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        if value not in TYPE_LIST:
            self._type = 'Unknown'
        else:
            self._type = value

    @property
    def stat_modifiers(self):
        return self._stat_modifiers
    
    @stat_modifiers.setter
    def stat_modifiers(self, value):
        self._stat_modifiers = value
        if 'attack' in value:
            # print('Setting stats for trinket')
            self.attack = value['attack']
            self.defense = value['defense']
            self.speed = value['speed']
        else:
            # print('Setting stats for non-trinket')
            self.damage = value['damage']
            self.mitigation = value['mitigation']
            self.finesse = value['finesse']

    def display(self):
        print('{} ({})'.format(self.name, self.type))
        if self.type in ['weapon', 'armor']:
            print('Damage +{}, Mitigation +{}, Finesse +{}'.format(self.damage, self.mitigation, self.finesse))
        elif self.type == 'trinket':
            print('Attack +{}, Defense +{}, Speed +{}'.format(self.attack, self.damage, self.speed))
        elif self.type == 'wealth':
            print('Appraised as having {} value.'.format(self.appraise_worth()))
        elif self.type == 'crafting':
            print('This can be used to improve weapons or armor.')
        
        print('Description:\n- {}'.format(self.description))
        print()
        input('Press enter to return')

    def appraise_worth(self):
        appraisal = 'worthless'
        if self.worth == 0:
            appraisal = 'worthless'
        elif self.worth == 1:
            appraisal = 'low'
        elif self.worth <= 3:
            appraisal = 'moderate'
        elif self.worth <= 5:
            appraisal = 'high'
        elif self.worth <= 9:
            appraisal = 'very high'
        elif self.worth <= 13:
            appraisal = 'extremely high'
        elif self.worth > 13:
            appraisal = 'priceless'

        return appraisal 