import os
from scripts.location import Location
from scripts.entity import Entity
from scripts.item import Item


LOCATION_PATH = 'assets/locations/'
ENEMY_PATH = 'assets/enemies/'
ITEM_PATH = 'assets/items/'


class Builder():
    def __init__(self) -> None:
        pass

    def create_character(self):
        player = Entity()
        player.name = input('What is your name? ')
        print()
        print('1. Quarryman')
        print('2. Loom-runner')
        print('3. Waller')
        print('4. Pest-culler')
        print()
        background = int(input('What is your background? '))
        if background == 1:
            player.attack = 5
            player.defense = 3
            player.speed = 1

        elif background == 2:
            player.attack = 3
            player.defense = 1
            player.speed = 5

        elif background == 3:
            player.attack = 1
            player.defense = 5
            player.speed = 3

        elif background == 4:
            player.attack = 4
            player.defense = 1
            player.speed = 4
        
        player.reset_health()
        player.print_entity()

    def build_areas(self):
        area_list = []
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

                            area_list.append(location)
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")

        return area_list
    
    def build_enemies(self):
        enemy_list = []
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
                    
                            enemy_list.append(enemy)
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")
        
        return enemy_list
    
    def build_items(self):
        item_list = []
        for dirpath, _, filenames in os.walk(ITEM_PATH):
            for filename in filenames:
                print('Attempting to walk through {}'.format(filename))
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, "r") as file:
                            name = filename
                            type = 'None'
                            description = []
                            stat_modifiers = {}
                            location = []
                            for i, line in enumerate(file):
                                if i == 0:
                                    type_line = line.strip()
                                    print('Setting {} type to {}'.format(name, type_line))
                                    type = type_line
                                elif i == 1:
                                    stat_line = line.strip()
                                    print('Setting {} stat modifiers'.format(name))
                                    stat_modifiers = eval(stat_line)
                                elif i == 2:
                                    location_line = line.strip()
                                    check = eval(location_line)
                                    if not check:
                                        location = ['global']
                                    else:
                                        location = check
                                    print('Setting the drop locations as {}'.format(location))
                                else:
                                    description.append(line.strip())
                                    print('Setting {} description'.format(name))
                            
                            item = Item()
                            item.name = name
                            item.type = type
                            print('Built item {} {}'.format(item.name, item.type))
                            
                            item.description = description
                            print('Set description as {}'.format(item.description))

                            item.spawn_location = location
                            print('Added to {}\n'.format(item.spawn_location))

                            item.stat_modifiers = stat_modifiers
                            item_list.append(item)
                    except Exception as e:
                        print(f"Error reading file {filepath}: {e}")
        
        return item_list