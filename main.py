import arcade
from scripts.entity import Entity
from scripts.combat import Combat
from scripts.travel import Travel
from scripts.travel import Location
from scripts.travel import Region
import sys


TITLE = 'Miniquest'
WIDTH = 1080
HEIGHT = 720

LOCATION_PATH = 'assets/locations/'
ART_PATH = 'assets/art/'
SOUND_PATH = 'assets/sound/'


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
            travel.build_locations()
            current_region = 'lastholm'
            current_location = 'Lastholm'
            
            loop = True

            while loop:
                l = travel.get_location(current_region, current_location)

                print()
                print(l.location_name)
                print()
                print(l.location_description)
                print()

                for i in range(len(travel.location_dictionary[current_region])):
                    print('{}. {}'.format(i + 1, travel.location_dictionary[current_region][i].location_name))
                
                print('Type any letter to return to main menu...')
                loc_select = input('Enter your destination: ')
                
                try:
                    current_location = travel.location_dictionary[current_region][int(loc_select) - 1].location_name
                except ValueError:
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