import arcade
from scripts.entity import Entity
from scripts.combat import Combat
from scripts.world import World
import sys


TITLE = 'Miniquest'
WIDTH = 1080
HEIGHT = 720

LOCATION_PATH = 'miniquest/assets/locations/'
ART_PATH = 'miniquest/assets/art/'
SOUND_PATH = 'moniquest/assets/sound/'


def main():
    world = World()
    loop = True

    while loop:
        print("""Miniquest\n
            1. Create Character
            2. Travel
            3. Exit Game
            """)
        
        i = input('Enter selection: ')

        if i == '1':
            world.create_character()
        
        elif i == '2':
            world.build_areas()  
            loop = True

            while loop:
                world.display_current_area()
                loop = False

        elif i == '3':
            loop = False
            sys.exit

        else:
            pass


if __name__ == "__main__":
    main()