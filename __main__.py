import logging
import arcade.color
from scripts.world import World
from scripts.builder import Builder # Builder is imported but not directly used in __main__.py, might be a remnant
import arcade
import os
import sys

logging.getLogger('arcade').setLevel(logging.INFO)


# --- Constants ---
GAME_AREA_WIDTH = 512 # The fixed width for game art
MENU_PANEL_WIDTH = 240 # Width for the right-hand menu
SCREEN_WIDTH = GAME_AREA_WIDTH + MENU_PANEL_WIDTH # Total screen width
SCREEN_HEIGHT = 600 # Adjusted height to accommodate banner and buttons better
SCREEN_TITLE = "Miniquest"

# Button properties (for the main menu)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_COLOR_TRANSLUCENT = (arcade.color.DARK_BLUE[0], arcade.color.DARK_BLUE[1], arcade.color.DARK_BLUE[2], 120)
BUTTON_HOVER_COLOR = arcade.color.BLUE
BUTTON_TEXT_COLOR = arcade.color.WHITE
BUTTON_FONT_SIZE = 18

# Background image filepath for the main menu
BACKGROUND_IMAGE = "miniquest/assets/art/background_title.jpg"

# --- Game View Constants ---
PLAYER_INFO_BANNER_HEIGHT = 80 # Height for the top player info banner
TOP_PADDING = 20 # Padding from the top of the screen for text
LEFT_PADDING = 10 # Padding from the left of the main game area for text
RIGHT_MENU_X_START = GAME_AREA_WIDTH # X-coordinate where the right menu begins

# New: Placeholder art for locations without specific images
PLACEHOLDER_ART = "miniquest/assets/art/placeholder.jpg" # Make sure this file exists!
ART_PATH = "miniquest/assets/art/"


class MenuView(arcade.View):
    """
    Main menu view for the game, featuring a background image and horizontal buttons.
    """
    def __init__(self):
        super().__init__()
        # Load background image
        try:
            self.background_texture = arcade.load_texture(BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Error: Background image '{BACKGROUND_IMAGE}' not found.")
            print("Please make sure the image file is in the correct path or update the 'BACKGROUND_IMAGE' constant.")
            self.background_texture = None

        # Initialize button sprites
        self.new_game_button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR_TRANSLUCENT)
        self.load_game_button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR_TRANSLUCENT)
        self.quit_button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR_TRANSLUCENT)

        # Position buttons horizontally at the bottom
        total_button_width = (BUTTON_WIDTH * 3) + (2 * 20)
        start_x = (SCREEN_WIDTH - total_button_width) / 2 + BUTTON_WIDTH / 2

        self.new_game_button.center_x = start_x
        self.new_game_button.center_y = 50

        self.load_game_button.center_x = start_x + BUTTON_WIDTH + 20
        self.load_game_button.center_y = 50

        self.quit_button.center_x = start_x + (BUTTON_WIDTH * 2) + (2 * 20)
        self.quit_button.center_y = 50

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        if self.background_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.background_texture,
            )

        arcade.draw_text(
            "Miniquest",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
        )

        self.new_game_button.draw()
        self.load_game_button.draw()
        self.quit_button.draw()

        arcade.draw_text(
            "New Game", self.new_game_button.center_x, self.new_game_button.center_y,
            BUTTON_TEXT_COLOR, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            "Load Game", self.load_game_button.center_x, self.load_game_button.center_y,
            BUTTON_TEXT_COLOR, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
        )
        arcade.draw_text(
            "Quit", self.quit_button.center_x, self.quit_button.center_y,
            BUTTON_TEXT_COLOR, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
        )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.new_game_button.collides_with_point((x, y)):
            print("--- New Game button pressed! ---")
            game_world = World()
            game_world.create_character() # This will populate the log with creation messages
            game_view = GameView(game_world)
            self.window.show_view(game_view)
        elif self.load_game_button.collides_with_point((x, y)):
            print("--- Load Game button pressed! ---")
            # For now, this is identical to New Game.
            # In a real game, you'd load state from a file here.
            game_world = World()
            game_world.create_character() # Temp: still creates character for testing
            game_view = GameView(game_world)
            self.window.show_view(game_view)
        elif self.quit_button.collides_with_point((x, y)):
            print("--- Quit button pressed! Exiting game. ---")
            arcade.exit()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.new_game_button.collides_with_point((x, y)):
            self.new_game_button.color = BUTTON_HOVER_COLOR
        else:
            self.new_game_button.color = BUTTON_COLOR_TRANSLUCENT

        if self.load_game_button.collides_with_point((x, y)):
            self.load_game_button.color = BUTTON_HOVER_COLOR
        else:
            self.load_game_button.color = BUTTON_COLOR_TRANSLUCENT

        if self.quit_button.collides_with_point((x, y)):
            self.quit_button.color = BUTTON_HOVER_COLOR
        else:
            self.quit_button.color = BUTTON_COLOR_TRANSLUCENT


class GameView(arcade.View):
    """
    Main game view where gameplay takes place.
    """
    def __init__(self, world_instance: World):
        super().__init__()
        self.world = world_instance
        self.player = self.world.player

        self.game_area_background = None
        self.placeholder_texture = None # To hold the loaded placeholder texture
        self.load_placeholder_texture() # Load placeholder once

        self.load_current_area_art()

        self.current_menu_options = []
        # Initial population of options will happen in on_show_view
        # because the world needs to initialize its state before options are reliable.

        # NEW: Display mode for the main game area
        self.display_mode = "area_description" # Can be "area_description", "combat_log", "inventory", etc.
        self.log_messages_to_display = [] # List to hold messages retrieved from world.message_log


    def load_placeholder_texture(self):
        """ Loads the generic placeholder texture once. """
        try:
            self.placeholder_texture = arcade.load_texture(PLACEHOLDER_ART)
        except FileNotFoundError:
            print(f"Error: Placeholder image '{PLACEHOLDER_ART}' not found.")
            print("Please create a 'placeholder.jpg' in 'miniquest/assets/art/'.")
            self.placeholder_texture = None

    def load_current_area_art(self):
        """ Loads the art for the current area, with fallback to placeholder. """
        art_file_name = self.world.current_area.name.lower().replace(' ', '_') + ".jpg"
        # FIX: Access ART_PATH from the world instance
        art_path = f"{ART_PATH}{art_file_name}"
        try:
            self.game_area_background = arcade.load_texture(art_path)
        except FileNotFoundError:
            print(f"Warning: Area background image '{art_path}' not found for '{self.world.current_area.name}'.")
            # If specific art not found, use the pre-loaded placeholder
            self.game_area_background = self.placeholder_texture
            if self.game_area_background is None:
                print("Critical: No specific area art or placeholder art found. Using solid color fallback.")


    def update_menu_options(self, menu_type="main"):
        # We need to refresh the current area data to get accurate connections after travel
        self.world.display_current_area() # This refreshes description in world.current_area and populates message_log
        
        if menu_type == "main":
            options_text = ["1. Fight", "2. Travel", "3. Rest"]
            if self.world.current_area.name == self.world.camp:
                options_text[0] = "1. Prepare"
            self.current_menu_options = options_text
        elif menu_type == "travel":
            connections = self.world.current_area.get_connections()
            options_text = [f"{i+1}. {conn}" for i, conn in enumerate(connections)]
            options_text.append(f"{len(connections) + 1}. Stay") # Option to stay in current area during travel prompt
            self.current_menu_options = options_text


    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        # When GameView is shown, update options and load initial messages
        self.update_menu_options("main") # Set initial main menu options
        self.log_messages_to_display = self.world.get_messages() # Get welcome and character creation messages

    def on_draw(self):
        self.clear()

        # --- Draw Player Info Banner (Top) ---
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
            SCREEN_WIDTH,
            PLAYER_INFO_BANNER_HEIGHT,
            arcade.color.DARK_GRAY
        )
        # Display player stats
        player_info_y = SCREEN_HEIGHT - TOP_PADDING - (PLAYER_INFO_BANNER_HEIGHT / 2) + 20
        text_color = arcade.color.WHITE
        font_size = 12

        # Name, Level, Time
        arcade.draw_text(
            f"Name: {self.player.name} | Level: {self.player.level} | Time: {self.world.time} hrs",
            LEFT_PADDING,
            player_info_y,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="bottom",
            width=int(GAME_AREA_WIDTH - 2 * LEFT_PADDING),
            align="left"
        )
        
        # Combat Stats (Attack, Defense, Speed)
        self.player.update_stats() # Ensure stats are fresh

        # Health
        arcade.draw_text(
            f"Health: {self.player.current_health}/{self.player.max_health} Atk: {self.player.attack + self.player.attack_mod} | Def: {self.player.defense + self.player.defense_mod} | Spd: {self.player.speed + self.player.speed_mod}",
            LEFT_PADDING,
            player_info_y - 25,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="bottom",
            width=int(GAME_AREA_WIDTH - 2 * LEFT_PADDING),
            align="left"
        )
        # Combat Stats (Attack, Defense, Speed)
        # self.player.update_stats() # Ensure stats are fresh

        # arcade.draw_text(
        #     f"Atk: {self.player.attack + self.player.attack_mod} | Def: {self.player.defense + self.player.defense_mod} | Spd: {self.player.speed + self.player.speed_mod}",
        #     LEFT_PADDING,
        #     player_info_y - 50,
        #     text_color,
        #     font_size=font_size,
        #     anchor_x="left",
        #     anchor_y="center",
        #     width=int(GAME_AREA_WIDTH - 2 * LEFT_PADDING),
        #     align="left"
        # )

        # Income / Wealth
        arcade.draw_text(
            f"Wealth: {self.player.inventory.income}",
            int(LEFT_PADDING + (GAME_AREA_WIDTH / 2)),
            player_info_y - 25,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="bottom",
            width=int((GAME_AREA_WIDTH / 2) - 2 * LEFT_PADDING),
            align="left"
        )

        # --- Draw Main Game Area (Left 512x512) ---
        game_area_y_center = (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2
        
        # Draw the background image for the current area, or the placeholder, or fallback color
        if self.game_area_background:
            arcade.draw_texture_rectangle(
                GAME_AREA_WIDTH / 2,
                game_area_y_center,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.game_area_background,
            )
        else:
            # Fallback if no image (not even placeholder) found
            arcade.draw_rectangle_filled(
                GAME_AREA_WIDTH / 2,
                game_area_y_center,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_OLIVE_GREEN
            )

        # Overlay text description for the current area OR combat log
        description_x = LEFT_PADDING
        description_y = game_area_y_center + (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2 - TOP_PADDING
        description_width = GAME_AREA_WIDTH - 2 * LEFT_PADDING
        
        text_bg_height = 150 # Adjust based on content. For log, it might need to be taller.
        # Draw a semi-transparent background for the text overlay
        arcade.draw_rectangle_filled(
            GAME_AREA_WIDTH / 2,
            description_y - text_bg_height / 2,
            description_width + 20,
            text_bg_height,
            (0, 0, 0, 180) # Slightly more opaque for readability
        )

        # NEW: Conditional rendering based on display_mode
        if self.display_mode == "area_description":
            arcade.draw_text(
                f"Location: {self.world.current_area.name}\n\n{self.world.current_area.description}",
                description_x,
                description_y,
                arcade.color.LIGHT_GRAY,
                font_size=12,
                width=description_width,
                align="left",
                anchor_x="left",
                anchor_y="top"
            )
        elif self.display_mode == "combat_log":
            # Display messages from the log_messages_to_display list
            # We'll display them from bottom up for readability
            log_display_start_y = description_y - 20 # Start slightly below the top of the text box
            line_height = 16 # Approx font size + spacing
            max_lines = int(text_bg_height / line_height) # Max lines that fit in the box

            # Display the most recent messages first, to ensure they are visible
            messages_to_render = self.log_messages_to_display[-max_lines:]
            
            # Iterate through messages and draw them
            # Draw from bottom up to keep newest at the visual bottom of the log box
            for i, message in enumerate(reversed(messages_to_render)): 
                arcade.draw_text(
                    message,
                    description_x,
                    # Adjust y to draw from the bottom of the log box upwards
                    description_y - text_bg_height + (len(messages_to_render) - 1 - i) * line_height + 5, 
                    arcade.color.WHITE, # Use white for log messages
                    font_size=12,
                    width=description_width,
                    align="left",
                    anchor_x="left",
                    anchor_y="bottom" # Anchor to bottom for proper stacking
                )
            # Add a prompt to return to area description if in combat log mode
            arcade.draw_text(
                "Click outside menu to continue...",
                GAME_AREA_WIDTH / 2,
                game_area_y_center - (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2 + 10, # Position at bottom of game area
                arcade.color.YELLOW,
                font_size=10,
                anchor_x="center",
                anchor_y="bottom"
            )


        # --- Draw Right-Hand Menu ---
        arcade.draw_rectangle_filled(
            RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
            (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2, # Centered vertically below banner
            MENU_PANEL_WIDTH,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
            arcade.color.DARK_SLATE_GRAY
        )

        # Menu title
        arcade.draw_text(
            "Actions",
            RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - TOP_PADDING,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="top"
        )

        # Draw menu options
        menu_start_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - TOP_PADDING - 40
        for i, option_text in enumerate(self.current_menu_options):
            arcade.draw_text(
                option_text,
                RIGHT_MENU_X_START + 20,
                menu_start_y - (i * 30),
                arcade.color.LIGHT_YELLOW,
                font_size=16,
                anchor_x="left",
                anchor_y="top"
            )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        print(f"Mouse pressed at ({x}, {y}) in GameView")
        
        # Check if click is within the right-hand menu area
        if x > RIGHT_MENU_X_START:
            # Only process menu clicks if not in combat log review mode
            if self.display_mode == "combat_log":
                # If in combat log mode, a click on the menu *should* still activate the menu item.
                # The "Click outside menu to continue" prompt is for clicking *outside* the menu.
                pass # Continue to menu item processing below
            
            menu_start_y_clickable = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - TOP_PADDING - 40
            for i, option_text in enumerate(self.current_menu_options):
                option_top_y = menu_start_y_clickable - (i * 30)
                option_bottom_y = option_top_y - 25 

                if (RIGHT_MENU_X_START + 20 < x < RIGHT_MENU_X_START + MENU_PANEL_WIDTH - 20 and
                    option_bottom_y < y < option_top_y):
                    
                    print(f"Clicked: {option_text}")
                    
                    # Extract the actual command/destination from option_text
                    # This is the key change for travel
                    command = option_text
                    if ". " in option_text: # This handles numbered options like "1. Fight" or "2. Aethelwood"
                        command = option_text.split(". ", 1)[1] # Get "Fight" or "Aethelwood"

                    # Use world.handle_player_choice to manage state and get display mode
                    self.log_messages_to_display.clear() 
                    new_display_mode = self.world.handle_player_choice(command) # Pass the extracted command!
                    
                    # Update local state based on world's decision
                    if new_display_mode == "combat_log":
                        self.display_mode = "combat_log"
                        self.log_messages_to_display.extend(self.world.get_messages())
                    elif new_display_mode == "travel_options":
                        self.update_menu_options("travel")
                        self.display_mode = "area_description"
                        self.log_messages_to_display.extend(self.world.get_messages()) 
                    else: # "area_description" or other default
                        self.display_mode = "area_description"
                        # Ensure main menu options are set after any action that resolves
                        self.update_menu_options("main") 
                        self.load_current_area_art() # Reload art in case of travel
                        self.log_messages_to_display.extend(self.world.get_messages()) # Get new messages
                        
                    # Always redraw after a menu action
                    self.on_draw()
                    break # Exit loop after first click detected
        else: # Click was outside the menu area (e.g., in the main game art area)
            if self.display_mode == "combat_log":
                # If in combat log mode and clicked outside menu, switch back to area description
                self.display_mode = "area_description"
                self.log_messages_to_display.clear() # Clear old messages from log
                self.world.get_messages() # Clear messages from world's log as well
                self.on_draw() # Redraw to show area description
            elif self.display_mode == "area_description" and any("Stay" in opt for opt in self.current_menu_options): # Check if current options are travel options (by looking for 'Stay')
                # If we're in travel selection mode but clicked outside, assume "Stay"
                self.world.handle_player_choice("Stay") # Explicitly call "Stay"
                self.update_menu_options("main") # Revert to main menu
                self.log_messages_to_display.extend(self.world.get_messages())
                self.on_draw()


    def on_update(self, delta_time: float):
        """ Called every frame to update game logic. """
        self.player.update_stats()
        # Check for game over state
        if self.player.is_dead():
            # Ensure death messages are captured before exiting
            self.display_mode = "combat_log" 
            # Force world to append death message if it hasn't already
            if "has been defeated!" not in self.world.message_log: # Basic check to avoid re-adding
                self.world.append_message(f"{self.player.name} has been defeated!")
            self.log_messages_to_display.extend(self.world.get_messages()) # Get the final death message
            
            self.on_draw() # Draw one last frame with death message
            # For now, just exit. You'd implement a GameOverView later.
            print("Game Over!")
            arcade.exit()


def main():
    """ Main function to set up and run the game """
    # FIX: Safely get the file path.
    # sys.modules[World.__module__].__file__ might be None if the module is built-in or frozen.
    world_module_path = getattr(sys.modules.get(World.__module__), '__file__', 'N/A')
    if world_module_path != 'N/A':
        print(f"Python is loading world.py from: {world_module_path}")
        print(f"Absolute path: {os.path.abspath(world_module_path)}")
    else:
        print(f"Could not determine path for world.py module (World.__module__: {World.__module__}).")


    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()


"""
def main():
    os.chdir('miniquest/')
    world = World()
    loop = True

    while loop:
        print('Miniquest')
        print()
        print('1. New Game')
        print('2. Exit Game')
        
        i = input('Enter selection: ')
        
        if i == '1':  
            loop = True
            world.create_character()

            while loop:
                world.display_current_area()
                loop = False

        elif i == '2':
            loop = False
            sys.exit

        else:
            pass


if __name__ == "__main__":
    main()
"""