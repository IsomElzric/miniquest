from scripts.loot import Loot


class Combat():
    def __init__(self, area, loot, message_log): # NEW: Accept message_log
        self.combatant_list = []
        self.loot = loot
        self.area = area
        self.run = True
        self.message_log = message_log # NEW: Store message_log reference

    def add_combatant(self, fighter):
        try:
            # Note: speed_mod is already included in fighter.speed @property calculation
            # if fighter.speed > self.combatant_list[0].speed + self.combatant_list[0].speed_mod:
            if fighter.speed + fighter.speed_mod > self.combatant_list[0].speed + self.combatant_list[0].speed_mod: # Use property directly
                self.combatant_list.insert(0, fighter)
            else:
                self.combatant_list.append(fighter)
        except IndexError:
            self.combatant_list.append(fighter)

    def print_combatants(self):
        # NEW: Append to message_log instead of print
        self.message_log('{} acts first with base speed {}! {} acts second with base speed {}!'.format( # Changed from .append
            self.combatant_list[0].name,
            self.combatant_list[0].speed + self.combatant_list[0].speed_mod,
            self.combatant_list[1].name,
            self.combatant_list[1].speed + self.combatant_list[1].speed_mod))
        
    # The start_combat loop is now managed by the World class through discrete actions.
    # def start_combat(self):
        # ... old loop removed ...

    def execute_player_attack(self, attacker, defender): # Renamed from player_turn
        # Message "It's your turn!" is now handled by World class
        damage = attacker.roll_attack(self.message_log) # NEW: Pass message_log to roll_attack
        self.message_log(f'{attacker.name} deals {damage} damage!') # Use attacker.name for consistency
        
        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log(f'{defender.name} has {defender.current_health} health.') # Changed from .append
        self.message_log('') # Add spacing
        # Death check and loot generation will be handled by the World class after this method returns.

    def execute_enemy_attack(self, attacker, defender): # Renamed from enemy_turn
        # Message about enemy attacking is now handled by World class
        damage = attacker.roll_attack(self.message_log) # NEW: Pass message_log to roll_attack
        self.message_log(f'{attacker.name} deals {damage} damage to you!') # Changed from .append

        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log(f'You have {defender.current_health} health left.') # Changed from .append
        self.message_log('') # Add spacing
        # Death check for player will be handled by the World class.

    def update_fighters(self):
        pass

    def check_death(self, entity):
        return entity.is_dead()
    
    def generate_loot(self, player, defeated_enemy): 
        """Determines loot drop, logs finding it, and returns the item (or None)."""
        drop = self.loot.get_drop_by_area(player, self.area) # CORRECTED: Pass the actual player object
        if drop:
            self.message_log(f'As the creature lays dead you find a {drop.name}!') # Changed from .append
            return drop # Return the item to be handled by World
        else:
            self.message_log(f'The {defeated_enemy.name} yielded no loot.') # Changed from .append
            self.message_log('') # Add spacing
            return None