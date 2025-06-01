import arcade
from scripts.entity import Entity
from scripts.combat import Combat
from scripts.travel import Travel
import sys


TITLE = 'Miniquest'
WIDTH = 1080
HEIGHT = 720

LOCATION_PATH = 'miniquest/assets/locations/'
ART_PATH = 'miniquest/assets/art/'
SOUND_PATH = 'moniquest/assets/sound/'


def main():
    loop = True

    while loop:
        print("""Miniquest\n
            1. Fight
            2. Travel
            3. Create Character
            4. Exit Game
            """)
        
        i = input('Enter selection: ')

        if i == '1':
            loop = False

            player = Entity()
            player.is_player = True
            player.name = 'Player'
            player.attack = 3
            player.defense = 1
            player.speed = 5
            player.reset_health()
            player.print_entity()

            monster = Entity()
            monster.name = 'Monster'
            monster.attack = 2
            monster.defense = 1
            monster.speed = 3
            monster.reset_health()
            monster.print_entity()

            fight = Combat()
            fight.add_combatant(player)
            fight.add_combatant(monster)
            fight.print_combatants()
            fight.start_combat() 
        
        elif i == '2':
            travel = Travel()
            travel.build_areas()  
            loop = True

            while loop:
                travel.display_current_area()
                loop = False

        elif i == '3':
            print('Feature in progress...')

        elif i == '4':
            loop = False
            sys.exit

        else:
            pass


if __name__ == "__main__":
    main()