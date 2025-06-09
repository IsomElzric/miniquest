# scripts/builder.py
import os
from scripts.location import Location
from scripts.entity import Entity
from scripts.item import Item
import copy # NEW: Import copy module for deep copying entities


# Determine the absolute path to the 'miniquest' package directory
# __file__ is '.../miniquest/scripts/builder.py'
# os.path.dirname(__file__) is '.../miniquest/scripts'
# os.path.dirname(os.path.dirname(__file__)) is '.../miniquest' (this is the package root)
PACKAGE_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PACKAGE_ROOT_DIR, 'assets')

LOCATION_PATH = os.path.join(ASSETS_DIR, 'locations')
ENEMY_PATH = os.path.join(ASSETS_DIR, 'enemies')
ITEM_PATH = os.path.join(ASSETS_DIR, 'items')

class Builder():
    def __init__(self, message_log) -> None:  # Accept message_log here
        self.player = Entity()
        self.message_log = message_log # Store message_log

    def create_character(self):
        # This method is now non-interactive for GUI compatibility.
        # It sets up a default character. The GUI will handle input.
        self.player.name = "Nameless Adventurer" # Default name
        
        # Default stats for a balanced start
        self.player.attack = 3
        self.player.defense = 3
        self.player.speed = 3
        
        self.player.update_stats()
        self.player.reset_health()
        # Ensure print_entity uses the message_log
        self.player.print_entity(self.message_log)

    def get_player(self):
        return self.player

    def build_areas(self):
        area_list = []
        for dirpath, _, filenames in os.walk(LOCATION_PATH):
            for filename in filenames:
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
                                    connections = eval(connection_line)
                                elif i == 1:
                                    enemy_line = line.strip()
                                    enemies = eval(enemy_line)
                                else:
                                    description.append(line.strip())
                            
                            location = Location()
                            # Remove .txt from filename for the name
                            location.name = os.path.splitext(filename)[0] 
                            
                            location.description = description
                            
                            for i in connections:
                                location.build_connection(i)
                            
                            for e in enemies:
                                location.add_enemy(e)

                            area_list.append(location)
                    except Exception as e:
                        self.message_log(f"Error reading location file {filepath}: {e}") # Changed from .append
                        # Keeping print for console debugging during development
                        print(f"Error reading location file {filepath}: {e}") 

        return area_list
    
    def build_enemies(self):
        enemy_list = []
        for dirpath, _, filenames in os.walk(ENEMY_PATH):
            for filename in filenames:
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, "r") as file:
                            name = os.path.splitext(filename)[0] # Get name without .txt
                            attack = 1
                            defense = 1
                            speed = 1
                            level = 1
                            for i, line in enumerate(file):
                                if i == 0:
                                    attack_line = line.strip()
                                    attack = int(attack_line)
                                elif i == 1:
                                    defense_line = line.strip()
                                    defense = int(defense_line)
                                elif i == 2:
                                    speed_line = line.strip()
                                    speed = int(speed_line)
                                elif i == 3:
                                    level_line = line.strip()
                                    level = int(level_line)
                                else:
                                    self.message_log(f'Warning: Unexpected line in enemy file {filename}') # Changed from .append
                                    print(f'Warning: Unexpected line in enemy file {filename}')
                            
                            enemy = Entity()
                            enemy.name = name
                            enemy.level = level
                            
                            enemy.attack = attack
                            enemy.defense = defense
                            enemy.speed = speed
                        
                            enemy_list.append(enemy)
                    except Exception as e:
                        self.message_log(f"Error reading enemy file {filepath}: {e}") # Changed from .append
                        print(f"Error reading enemy file {filepath}: {e}")
        
        return enemy_list
    
    def clone_enemy(self, enemy_template: Entity) -> Entity:
        """
        Clones an enemy template to create a new, fresh instance for combat.
        """
        # Using deepcopy is a clean way to ensure all attributes, including nested ones, are copied.
        cloned_enemy = copy.deepcopy(enemy_template)
        cloned_enemy.reset_health() # Ensure cloned entity starts with full health
        
        # No message appended here; the World.generate_enemy method will announce the enemy's appearance.
        return cloned_enemy

    def build_items(self):
        item_list = []
        for dirpath, _, filenames in os.walk(ITEM_PATH):
            for filename in filenames:
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, "r") as file:
                            name = os.path.splitext(filename)[0] # Get name without .txt
                            item_type = 'None' # Renamed from 'type' to avoid conflict with built-in type()
                            description = []
                            stat_modifiers = {}
                            location = []
                            icon_filename = None # Initialize icon filename
                            icon_subfolder = None # Initialize icon subfolder

                            # Determine the icon_subfolder from the dirpath
                            relative_dirpath = os.path.relpath(dirpath, ITEM_PATH)
                            if relative_dirpath and relative_dirpath != '.': # Ensure it's a subfolder
                                icon_subfolder = os.path.basename(relative_dirpath) # Get the last part of the path (subfolder name)
                            worth = 0
                            for i, line in enumerate(file):
                                if i == 0:
                                    item_type = line.strip()
                                elif i == 1:
                                    stat_line = line.strip()
                                    if item_type in ['weapon', 'armor', 'crafting', 'trinket']:
                                        stat_modifiers = eval(stat_line)
                                    elif item_type == 'wealth':
                                        worth = int(stat_line)
                                elif i == 2:
                                    location_line = line.strip()
                                    check = eval(location_line)
                                    if not check:
                                        location = ['global']
                                    else:
                                        location = check
                                elif i == 3: # Expect icon filename on the 4th line (index 3)
                                    icon_filename = line.strip()
                                else:
                                    description.append(line.strip()) # Description now starts from 5th line (index 4)
                            
                            item = Item()
                            item.name = name
                            item.type = item_type
                            item.description = description
                            item.spawn_location = location
                            item.icon_filename = icon_filename # Set the icon filename
                            item.icon_subfolder = icon_subfolder # Set the icon subfolder
                            
                            if item_type == 'wealth':
                                item.worth = worth
                            else:
                                item.stat_modifiers = stat_modifiers
                            
                            item_list.append(item)
                        
                    except Exception as e:
                        self.message_log(f"Error reading item file {filepath}: {e}") # Changed from .append
                        print(f"Error reading item file {filepath}: {e}\n")
        
        return item_list