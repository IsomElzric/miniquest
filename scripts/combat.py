from scripts.loot import Loot


class Combat():
    def __init__(self, area, loot):
        self.combatant_list = []
        self.loot = loot
        self.area = area
        self.run = True

    def add_combatant(self, fighter):
        try:
            if fighter.speed > self.combatant_list[0].speed:
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
        