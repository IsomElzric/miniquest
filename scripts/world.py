from abc import ABC, abstractmethod
from scripts.combat import Combat
from scripts.entity import Entity
import sys
import os
import random


LOCATION_PATH = 'assets/locations/'
ENEMY_PATH = 'assets/enemies/'
ART_PATH = 'miniquest/assets/art/'
SOUND_PATH = 'miniquest/assets/sound/'


class World():
    def __init__(self) -> None:
        self.time = 0
        self.current_area = Location()
        self.area_list = []

        self.build_areas()
        self.set_location('Lastholm')
        self.camp = 'Lastholm'

        self.player = Entity()
        self.player.is_player = True
        self.enemy_list = []

        self.build_enemies()

    def set_location(self, value):
        for i, v in enumerate(self.area_list):
            # print('Looking for {} in {}'.format(value, v.name))
            if v.name == value:
                self.current_area = v
                # print('Found {} and set current location as {}'.format(value, self.current_area.name))
                if self.current_area.name in ['Lastholm', 'Aethelwood', 'Scorlends', 'Shadowsun']:
                    self.camp = self.current_area.name
                break
            else:
                # print('Area not found')
                pass

    def build_areas(self):
        for dirpath, _, filenames in os.walk(LOCATION_PATH):
            for filename in filenames:
                # print('Attempting to walk through {}'.format(filename))
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, "r") as file:
                            description = []
                            connections = []
                            enemies = []
                            for i, line in enumerate(file):
                                if i == 0:
                                    connection_line = line.strip()
                                    # print(connection_line)
                                    connections = eval(connection_line)
                                elif i == 1:
                                    enemy_line = line.strip()
                                    # print(enemy_line)
                                    enemies = eval(enemy_line)
                                else:
                                    description.append(line.strip())
                                    # print('Reading description {}'.format(description))
                            
                            location = Location()
                            location.name = filename
                            # print('Built location {}'.format(location.name))
                            
                            location.description = ''
                            location.description = description
                            # print('Set description {}'.format(location.description))
                            

                            for i in connections:
                                location.build_connection(i)
                                # print('Built connection to {}'.format(i))
                            
                            for e in enemies:
                                location.add_enemy(e)

                            self.area_list.append(location)
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")
      
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
        else:
            sys.exit()

    def fight(self):
        fight = Combat()
        player = self.player
        player.print_entity()

        enemy = self.generate_enemy()

        fight.add_combatant(player)
        fight.add_combatant(enemy)
        fight.print_combatants()
        fight.start_combat()

    def create_character(self):
        self.player.name = input('What is your name? ')
        print()
        print('1. Quarryman')
        print('2. Loom-runner')
        print('3. Waller')
        print('4. Pest-culler')
        print()
        background = int(input('What is your background? '))
        if background == 1:
            self.player.attack = 5
            self.player.defense = 3
            self.player.speed = 1

        elif background == 2:
            self.player.attack = 3
            self.player.defense = 1
            self.player.speed = 5

        elif background == 3:
            self.player.attack = 1
            self.player.defense = 5
            self.player.speed = 3

        elif background == 4:
            self.player.attack = 4
            self.player.defense = 1
            self.player.speed = 4
        
        self.player.reset_health()
        self.player.print_entity()

    def build_enemies(self):
        for dirpath, _, filenames in os.walk(ENEMY_PATH):
            for filename in filenames:
                # print('Attempting to walk through {}'.format(filename))
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, "r") as file:
                            name = filename
                            attack = 1
                            defense = 1
                            speed = 1
                            level = 1
                            for i, line in enumerate(file):
                                if i == 0:
                                    attack_line = line.strip()
                                    # print('Setting {} Attack {}'.format(name, attack_line))
                                    attack = int(attack_line)
                                elif i == 1:
                                    defense_line = line.strip()
                                    # print('Setting {} Defense {}'.format(name, defense_line))
                                    defense = int(defense_line)
                                elif i == 2:
                                    speed_line = line.strip()
                                    # print('Setting {} Speed {}'.format(name, speed_line))
                                    speed = int(speed_line)
                                elif i == 3:
                                    level_line = line.strip()
                                    # print('Setting {} Level {}'.format(name, level_line))
                                    level = int(level_line)
                                else:
                                    print('Did not find stats in {}'.format(filename))
                                    # description.append(line.strip())
                                    # print('Reading description {}'.format(description))
                            
                            enemy = Entity()
                            enemy.name = name
                            enemy.level = level
                            # print('Built enemy {} level {}'.format(enemy.name, enemy.level))
                            
                            enemy.attack = attack
                            enemy.defense = defense
                            enemy.speed = speed
                            # print('Set stats A:{} D:{} S:{}\n'.format(enemy.attack, enemy.defense, enemy.speed))
                    
                            self.enemy_list.append(enemy)
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")

    def generate_enemy(self):
        # print('Generating enemy')
        
        enemy_pool = self.current_area.get_enemies()
        # print(enemy_pool)
        
        selected_enemy = random.choice(enemy_pool)
        # print('Selected enemy {}'.format(selected_enemy))
        for i, v in enumerate(self.enemy_list):
            if v.name == selected_enemy:
                enemy = v
                enemy.reset_health()
                enemy.print_entity()
                return enemy
            else:
                # print('No enemy found named {}'.format(selected_enemy))
                pass
        

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
        for i in value:
            self._description += i + '\n'

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