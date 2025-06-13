import logging
import arcade
import os
import sys

# Import necessary views and constants
from menu_view import MenuView
# World import is kept if the debug print in main() remains, otherwise it can be removed.
from scripts.world import World 
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

logging.getLogger('arcade').setLevel(logging.INFO)


def main():
    world_module_path = getattr(sys.modules.get(World.__module__), '__file__', 'N/A')
    if world_module_path != 'N/A':
        print(f"Python is loading world.py from: {world_module_path}")
        print(f"Absolute path: {os.path.abspath(world_module_path)}")
    else:
        print(f"Could not determine path for world.py module (World.__module__: {World.__module__}).")
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()