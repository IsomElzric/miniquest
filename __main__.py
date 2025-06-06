import arcade
from scripts.world import World
from scripts.builder import Builder
import sys
import os


TITLE = 'Miniquest'
WIDTH = 1080
HEIGHT = 720


def main():
    os.chdir('miniquest/')
    world = World()
    loop = True

    while loop:
        print("""Miniquest\n
            1. New Game
            2. Exit Game
            """)
        
        i = input('Enter selection: ')
        
        if i == '1':  
            loop = True
            world.create_character()

            while loop:
                world.display_current_area()
                loop = False

        elif i == '2':
            loop = False
            sys.exit

        else:
            pass


if __name__ == "__main__":
    main()