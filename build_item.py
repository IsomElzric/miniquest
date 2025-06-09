import os


def create_new_item():
    print('Item Builder')
    print('')
    print("--- Creating New Item ---")
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
        speed = "'speed': {}".format(input('What is the item\'s speed? '))
        stats = "{} {} {}".format(attack, defense, speed)
        value = '{' + stats + '}'
    else:
        value = '0'
    location = input('What is the item\'s location? (if more than one, seperate with a comma)\n - ').split(', ')
    if location[0] == '':
        checked_l = '[]'
    else:
        checked_l = str(location)
    icon_filename = input('What is the icon filename (e.g., sword.png)? ')  # Keep this line
    description = input('What is the item description? ').split('. ')

    lines = [type, value, checked_l, icon_filename]

    # Assuming build_item.py is in the main project directory (e.g., 'miniquest/'),
    # and 'assets' is a subdirectory within it.
    directory = "assets/items/{}/".format(area)
    full_path = os.path.join(os.path.dirname(__file__), directory, name)

    with open(full_path, "w") as file:
        for line in lines:
            file.write(line + "\n")
        for i in description:
            file.write(i + '\n')

    print(f"File saved to: {full_path}")

def update_all_item_icon_paths():
    print("\n--- Updating All Item Icon Paths ---")
    # Assuming build_item.py is in the main project directory (e.g., 'miniquest/'),
    # and 'assets' is a subdirectory within it.
    project_root = os.path.dirname(os.path.abspath(__file__))
    items_base_dir = os.path.join(project_root, "assets", "items")

    if not os.path.isdir(items_base_dir):
        print(f"Error: Items directory not found at {items_base_dir}")
        return

    updated_files_count = 0
    for dirpath, _, filenames in os.walk(items_base_dir):
        for filename in filenames:
            if filename.endswith(".txt"):
                item_name_from_file = os.path.splitext(filename)[0]
                # Generate icon filename: lowercase, spaces to underscores, add .png
                icon_filename_generated = item_name_from_file.lower().replace(' ', '_') + ".png"
                
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r") as file:
                        lines = file.readlines()
                    
                    # Ensure lines are stripped of trailing newlines for easier manipulation
                    lines = [line.rstrip('\n') for line in lines]

                    if len(lines) < 3:
                        print(f"Warning: File {filepath} has fewer than 3 lines. Skipping icon update.")
                        continue
                    
                    if len(lines) == 3: # File has type, stats, location, but no icon line yet
                        lines.append(icon_filename_generated)
                    else: # File has 4 or more lines, update the 4th line (index 3)
                        lines[3] = icon_filename_generated
                    
                    with open(filepath, "w") as file:
                        for line in lines:
                            file.write(line + "\n")
                    
                    print(f"Updated icon path in {filepath} to '{icon_filename_generated}'")
                    updated_files_count += 1
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
    print(f"\nFinished updating. {updated_files_count} item files processed.")

def main():
    while True:
        print("\nItem Management Utility")
        print("1. Create New Item")
        print("2. Update All Item Icon Paths")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            create_new_item()
        elif choice == '2':
            update_all_item_icon_paths()
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()