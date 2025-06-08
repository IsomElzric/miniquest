class Location():
    def __init__(self) -> None:
        self._name = 'Unset'
        self._description = ''
        self.connections = []
        self.travel_time = 1
        self.enemies = []

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
        # textwrap in __main__.py will handle all visual line breaking.
        self._description = " ".join(line for line in value if line.strip())
    def build_connection(self, area):
        # print('Adding connection {}'.format(area))
        if area not in self.connections:
            self.connections.append(area)
            # print('No conflicts, connection {} appended'.format(area))
        else:
            # print('{} already has a connection with {}'.format(self.name, area))
            pass
    
    def get_connections(self):
        return self.connections
    
    def add_enemy(self, enemy):
        if enemy not in self.enemies:
            self.enemies.append(enemy)
        else:
            pass
    
    def get_enemies(self):
        return self.enemies