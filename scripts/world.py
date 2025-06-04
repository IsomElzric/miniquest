from abc import ABC, abstractmethod
from scripts.combat import Combat
from scripts.entity import Entity
from scripts.builder import Builder
from scripts.location import Location
from scripts.inventory import Inventory
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
        
        self.time = 0
        self.current_area = Location()
        self.area_list = self.builder.build_areas()

        self.set_location('Lastholm')
        self.camp = 'Broken hearth'

        self.player = Entity()
        self.player.is_player = True

        self.enemy_list = self.builder.build_enemies()
        
        self.player.inventory.set_items(self.builder.build_items())
        self.all_weapons = []
        self.all_armors = []
        self.all_crafting = []
        self.all_wealth = []
        self.all_trinkets = []

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