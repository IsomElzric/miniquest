import os


def main():
    print('Item Builder')
    print('')
    area = input('What folder should this item be saved in? ')
    name = '{}.txt'.format(input('What is the item name? '))
    type = input('What type of item is this? ')
    if type in ['weapon', 'armor', 'crafting']:
        damage = "'damage': {},".format(input('What is the item\'s damage? '))
        mitigation = "'mitigation': {},".format(input('What is the item\'s mitigation? '))
        finesse = "'finesse': {}".format(input('What is the item\'s finesse? '))
        stats = "{} {} {}".format(damage, mitigation, finesse)
        value = '{' + stats + '}'
    elif type == 'wealth':
        value = input('What is its value? ')
    elif type == 'trinket':
        attack = "'attack': {},".format(input('What is the item\'s attack? '))
        defense = "'defense': {},".format(input('What is the item\'s defense? '))
        speed = "'speed': {},".format(input('What is the item\'s speed? '))
        stats = "{} {} {}".format(attack, defense, speed)
        value = '{' + stats + '}'
    else:
        value = '0'
    location = input('What is the item\'s location? (if more than one, seperate with a comma)\n - ').split(', ')
    if location[0] == '':
        checked_l = '[]'
    else:
        checked_l = str(location)
    description = input('What is the item description? ').split('. ')

    lines = [type, value, checked_l]

    directory = "assets/items/{}/".format(area)
    full_path = os.path.join(os.path.dirname(__file__), directory, name)

    with open(full_path, "w") as file:
        for line in lines:
            file.write(line + "\n")
        for i in description:
            file.write(i + '\n')

    print(f"File saved to: {full_path}")

main()

    