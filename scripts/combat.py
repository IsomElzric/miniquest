class Combat():
    def __init__(self):
        self.combatant_list = []
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
        print('{} acts first with speed {}! {} acts second with speed {}!'.format(
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
        print('You deal {} damage!'.format(damage))
        
        defender.take_damage(damage)
        print('{} has {} health.'.format(defender.name, defender.health))

        if self.check_death(defender):
            print('You have defeated {}!'.format(defender.name))
            self.run = False

    def enemy_turn(self, attacker, defender):
        print('\nYou are being attacked!')
        damage = attacker.roll_attack()
        print('You have been dealt {} damage!'.format(damage))

        defender.take_damage(damage)
        print('You have {} health left.'.format(defender.health))

        if self.check_death(defender):
            print('You have died!')
            self.run = False

    def update_fighters(self):
        pass

    def check_death(self, entity):
        return entity.is_dead()