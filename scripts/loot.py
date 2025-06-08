import random


class Loot():
    def __init__(self) -> None:
        self.all_items = []

    def set_items(self, value):
        self.all_items = value

    def get_drop_by_area(self, player, area):
        pool = []
        # print('Building the drop pool')
        for i, v in enumerate(self.all_items):
            # print('Checking {} which drops in {} against {}'.format(v.name, v.spawn_location, area))
            
            if area in v.spawn_location or 'global' in v.spawn_location[0]:
                # print('{} drops in {}, adding to drop pool\n'.format(v.name, area))
                pool.append(v)
        
        # if pool:
            # print('\nDrop pool built\n')
        # else:
            # print('\nDrop pool failed to build\n')

        drop = self.all_items[0]
        searching = True
        while searching:
            # print('Rolling on drop pool')
            checked = pool
            choice = random.choice(pool)
            # print('Chose {} from drop pool'.format(choice.name))
            # print('Checking type {} against type rules'.format(choice.type))

            if choice.type in ['weapon', 'armor']:
                # print('Choice follows weapon and armor rules')
                if choice not in player.inventory.owned_items:
                    # print('Player does not already own {}'.format(choice.name))
                    drop = choice
                    break
                else: 
                    # print('Player already owns {}'.format(choice.name))
                    checked.remove(choice)
            
            elif choice.type == 'trinket':
                # print('Choice follows trinket rules')
                if choice not in player.inventory.owned_items:
                    # print('Player does not already own {}'.format(choice.name))
                    drop = choice
                    break
                else:
                    # print('Player already owns {}'.format(choice.name))
                    checked.remove(choice)

            elif choice.type in ['crafting', 'wealth']:
                # print('Choice follows crafting and wealth rules')
                drop = choice
                break
            
            if not checked:
                # print('Pool exhausted and drop rules could not be satisfied\nUsing full item list!')
                pool = self.all_items

        return drop

    def roll_type(self):
        pass

    def check_inventory(self, player):
        pass

    def add_item_to_inventory(self, player, item, message_log_func): # Accept message_log_func
        player.inventory.add_to_stored_items(item)
        message_log_func(f'You have added a {item.name} to your bag.')
        message_log_func('') # Add spacing