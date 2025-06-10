import random


class Loot():
    def __init__(self) -> None:
        self.all_items = []

    def set_items(self, value):
        self.all_items = value

    def get_drop_by_area(self, player, area):
        """
        Determines a loot drop for the player based on the area.
        Trinkets will only drop if the player does not already own one of the same name.
        Returns the item object (template for now) or None if no drop.
        """
        pool = []
        # Build the initial drop pool based on area spawn locations
        for item_template in self.all_items:
            if area in item_template.spawn_location or ('global' in item_template.spawn_location and len(item_template.spawn_location) == 1): # Check for explicit 'global'
                pool.append(item_template)

        # Filter the pool: remove trinkets the player already owns (by name)
        # Keep other item types (weapon, armor, crafting, wealth) as duplicates are allowed
        filtered_pool = []
        owned_trinket_names = {item.name for item in player.inventory.owned_items if item.type == 'trinket'}

        for item_candidate in pool:
            if item_candidate.type == 'trinket':
                if item_candidate.name not in owned_trinket_names:
                    filtered_pool.append(item_candidate)
            else:
                # Always add non-trinkets to the filtered pool
                filtered_pool.append(item_candidate)

        # Now, select a random item from the filtered pool
        if filtered_pool:
            # NOTE: Returning the item template object directly for now.
            # A more robust solution would clone the item here.
            # For now, returning the template object is sufficient to test the uniqueness logic.
            drop = random.choice(filtered_pool)
            return drop # Return the selected item template
        else:
            # If the filtered pool is empty, it means all potential drops were trinkets the player already owned.
            # In this case, there is no drop.
            # print("DEBUG: Filtered drop pool is empty. No item dropped.")
            return None # No drop


    def roll_type(self):
        pass

    def check_inventory(self, player):
        pass

    def add_item_to_inventory(self, player, item, message_log_func): # Accept message_log_func
        # The inventory's add_to_stored_items method now handles capacity checks and logging.
        # It returns True if successful, False otherwise.
        success = player.inventory.add_to_stored_items(item, message_log_func)
        # message_log_func('') # Spacing is handled by add_to_stored_items or if no item found