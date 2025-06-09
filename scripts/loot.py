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

            if choice.type == 'trinket':
                # print('Choice follows trinket rules')
                if choice not in player.inventory.owned_items:
                    # print('Player does not already own {}'.format(choice.name))
                    drop = choice
                    break
                else:
                    # Player already owns this trinket, remove from current consideration
                    # print(f'Player already owns trinket {choice.name}, removing from checked pool for this roll.')
                    checked.remove(choice)
            elif choice.type in ['weapon', 'armor', 'crafting', 'wealth']:
                # Weapons, armor, crafting, and wealth items can drop multiple times.
                # No uniqueness check against owned_items for these types.
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
        # The inventory's add_to_stored_items method now handles capacity checks and logging.
        # It returns True if successful, False otherwise.
        success = player.inventory.add_to_stored_items(item, message_log_func)
        # message_log_func('') # Spacing is handled by add_to_stored_items or if no item found