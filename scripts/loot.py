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

        # --- Enhanced Debug Prints ---
        # print(f"DEBUG LOOT: ----- Loot Check for Player: {player.name} in Area: {area} -----")
        # print(f"DEBUG LOOT: All items currently in player.inventory.owned_items (name | type):")
        # for owned_item_debug in player.inventory.owned_items:
            # print(f"DEBUG LOOT:   - '{owned_item_debug.name}' | '{owned_item_debug.type}' (repr: {repr(owned_item_debug.name)})")
        # print(f"DEBUG LOOT: Constructed owned_trinket_names set: {owned_trinket_names}")
        # print(f"DEBUG LOOT: Representational owned_trinket_names: {[repr(name) for name in owned_trinket_names]}")
        # print(f"DEBUG LOOT: --- Checking items from area pool ---")
        # --- End Enhanced Debug Prints ---

        for item_candidate in pool:
            # --- Enhanced Debug Prints ---
            # print(f"DEBUG LOOT: Considering item_candidate: '{item_candidate.name}' (Type: {item_candidate.type}) (repr: {repr(item_candidate.name)})")
            # --- End Enhanced Debug Prints ---
            if item_candidate.type == 'trinket':
                is_owned = item_candidate.name in owned_trinket_names
                # --- Enhanced Debug Prints ---
                # print(f"DEBUG LOOT:   Trinket Check: '{item_candidate.name}' in owned_trinket_names? -> {is_owned}")
                # --- End Enhanced Debug Prints ---
                if not is_owned:
                    # print(f"DEBUG LOOT:   SUCCESS: Adding '{item_candidate.name}' to filtered_pool (not in owned_trinket_names).")
                    filtered_pool.append(item_candidate)
                else:
                    # print(f"DEBUG LOOT:   SKIPPED: Trinket '{item_candidate.name}' IS in owned_trinket_names.")
                    pass
            else:
                # Always add non-trinkets to the filtered pool
                # print(f"DEBUG LOOT:   Adding non-trinket '{item_candidate.name}' to filtered_pool.")
                filtered_pool.append(item_candidate)

        # Now, select a random item from the filtered pool
        if filtered_pool:
            drop = random.choice(filtered_pool)
            # print(f"DEBUG LOOT: Dropping '{drop.name}' from filtered_pool.")
            # print(f"DEBUG LOOT: ----- End Loot Check -----")
            return drop # Return the selected item template
        
        else:
            # If the filtered pool is empty, it means all potential drops were trinkets the player already owned.
            # In this case, there is no drop.
            # print(f"DEBUG LOOT: Filtered drop pool is empty. No item dropped.")
            # print(f"DEBUG LOOT: ----- End Loot Check -----")
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