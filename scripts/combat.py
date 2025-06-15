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
            if not self.combatant_list: # First combatant to be added
                self.combatant_list.append(fighter)
            else:
                # Second combatant is being added, determine order
                existing_fighter = self.combatant_list[0]
                new_fighter = fighter

                new_has_first_strike = new_fighter.has_ability("first_strike")
                existing_has_first_strike = existing_fighter.has_ability("first_strike")

                if new_has_first_strike and not existing_has_first_strike:
                    self.combatant_list.insert(0, new_fighter) # New fighter with first_strike goes first
                elif existing_has_first_strike and not new_has_first_strike:
                    self.combatant_list.append(new_fighter) # Existing fighter with first_strike stays first
                else: # Both or neither have first_strike, compare speed
                    # fighter.speed already includes speed_mod due to @property
                    if new_fighter.speed > existing_fighter.speed:
                        self.combatant_list.insert(0, new_fighter)
                    else:
                        self.combatant_list.append(new_fighter)
        except IndexError: # Should not be strictly needed with the new logic, but kept as a fallback.
            # This case implies combatant_list was unexpectedly empty when trying to access [0]
            # which the `if not self.combatant_list:` above should prevent.
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
        self.message_log(f'{attacker.name} deals {damage:.1f} damage!') # Use attacker.name for consistency
        
        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log(f'{defender.name} has {defender.current_health:.1f} health.') # Changed from .append
        self.message_log('') # Add spacing
        # Death check and loot generation will be handled by the World class after this method returns.

    def execute_enemy_attack(self, attacker, defender): # Renamed from enemy_turn
        # Message about enemy attacking is now handled by World class
        damage = attacker.roll_attack(self.message_log) # NEW: Pass message_log to roll_attack
        self.message_log(f'{attacker.name} deals {damage:.1f} damage to you!') # Changed from .append

        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log(f'You have {defender.current_health:.1f} health left.') # Changed from .append
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