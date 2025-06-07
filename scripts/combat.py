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
            if fighter.speed > self.combatant_list[0].speed: # Use property directly
                self.combatant_list.insert(0, fighter)
            else:
                self.combatant_list.append(fighter)
        except IndexError:
            self.combatant_list.append(fighter)

    def print_combatants(self):
        # NEW: Append to message_log instead of print
        self.message_log.append('{} acts first with base speed {}! {} acts second with base speed {}!'.format(
            self.combatant_list[0].name,
            self.combatant_list[0].speed,
            self.combatant_list[1].name,
            self.combatant_list[1].speed))
        
    def start_combat(self):
        attacker = self.combatant_list[0]
        defender = self.combatant_list[1]

        # NEW: Combat loop condition will now also check if player is dead for immediate exit
        while self.run and not attacker.is_dead() and not defender.is_dead():
            if attacker.is_player:
                # NEW: Player turn no longer requires input. This makes it automatic for GUI.
                self.message_log.append('It\'s your turn!')
                self.player_turn(attacker, defender)

                # Check if defender died after player's turn
                if self.check_death(defender):
                    self.message_log.append(f'You have defeated {defender.name}!')
                    # Loot generation should also append to message_log
                    self.generate_loot(attacker, defender) # Pass defender to get enemy details
                    self.run = False
                    break # Exit loop as combat ended

            else: # Enemy's turn
                self.message_log.append(f'{attacker.name} is attacking!')
                self.enemy_turn(attacker, defender)

                # Check if defender (player) died after enemy's turn
                if self.check_death(defender):
                    self.message_log.append('You have been defeated!')
                    self.run = False
                    break # Exit loop as combat ended
            
            # Swap roles for the next turn
            attacker, defender = defender, attacker

    def player_turn(self, attacker, defender):
        # input('Press enter to attack.\n') # REMOVED: No more CLI input

        damage = attacker.roll_attack(self.message_log) # NEW: Pass message_log to roll_attack
        self.message_log.append(f'You deal {damage} damage!')
        
        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log.append(f'{defender.name} has {defender.current_health} health.')

    def enemy_turn(self, attacker, defender):
        damage = attacker.roll_attack(self.message_log) # NEW: Pass message_log to roll_attack
        self.message_log.append(f'{attacker.name} deals {damage} damage to you!')

        defender.take_damage(damage, self.message_log) # NEW: Pass message_log to take_damage
        self.message_log.append(f'You have {defender.current_health} health left.')

    def update_fighters(self):
        pass

    def check_death(self, entity):
        return entity.is_dead()
    
    # NEW: Updated generate_loot to accept defender (the enemy) and append messages
    def generate_loot(self, player, defeated_enemy): 
        drop = self.loot.get_drop_by_area(defeated_enemy, self.area) # Loot based on defeated enemy
        if drop:
            self.message_log.append(f'As the creature lays dead you find a {drop.name}!')
            self.loot.add_item_to_inventory(player, drop)
        else:
            self.message_log.append(f'The {defeated_enemy.name} yielded no loot.')


"""
from scripts.loot import Loot


class Combat():
    def __init__(self, area, loot):
        self.combatant_list = []
        self.loot = loot
        self.area = area
        self.run = True

    def add_combatant(self, fighter):
        try:
            if fighter.speed > self.combatant_list[0].speed + self.combatant_list[0].speed_mod:
                self.combatant_list.insert(0, fighter)
            else:
                self.combatant_list.append(fighter)
        except IndexError:
            self.combatant_list.append(fighter)

    def print_combatants(self):
        print('{} acts first with base speed {}! {} acts second with base speed {}!'.format(
            self.combatant_list[0].name, 
            self.combatant_list[0].speed, 
            self.combatant_list[1].name, 
            self.combatant_list[1].speed))
        
    def start_combat(self):
        attacker = self.combatant_list[0]
        defender = self.combatant_list[1]

        while self.run:
            if attacker.is_player:
                self.player_turn(attacker, defender)

                attacker, defender = defender, attacker

            else:
                self.enemy_turn(attacker, defender)

                attacker, defender = defender, attacker

    def player_turn(self, attacker, defender):
        print('It\'s your turn!\n')
        input('Press enter to attack.\n')

        damage = attacker.roll_attack()
        print('You deal {} damage!\n'.format(damage))
        
        defender.take_damage(damage)
        print('{} has {} health.\n'.format(defender.name, defender.current_health))

        if self.check_death(defender):
            print('You have defeated {}!\n'.format(defender.name))
            self.generate_loot(attacker)
            self.run = False

    def enemy_turn(self, attacker, defender):
        print('You are being attacked!\n')
        damage = attacker.roll_attack()
        print('You have been dealt {} damage!\n'.format(damage))

        defender.take_damage(damage)
        print('You have {} health left.\n'.format(defender.current_health))

        if self.check_death(defender):
            print('You have died!\n')
            self.run = False

    def update_fighters(self):
        pass

    def check_death(self, entity):
        return entity.is_dead()
    
    def generate_loot(self, player):
        # loot.set_items(player.inventory.get_items())
        drop = self.loot.get_drop_by_area(player, self.area)
        print('As the creature lays dead you find a {}!'.format(drop.name))
        self.loot.add_item_to_inventory(player, drop)
"""       