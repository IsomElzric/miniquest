import logging
import arcade
import arcade.color # Explicitly import arcade.color
# os, sys, Counter, arcade.gui, and textwrap are not directly used in this file.
# Path constants are handled by constants.py
# UI elements are not directly created here using arcade.gui

# Import constants and other views/modules
from constants import (BACKGROUND_IMAGE, TOP_BANNER_BACKGROUND_IMAGE, MENU_BUTTON_IMAGE_PATH,
                       MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE, ASSETS_DIR, SCREEN_HEIGHT, PLAYER_INFO_BANNER_HEIGHT,
                       GAME_AREA_WIDTH, RIGHT_MENU_X_START, MENU_PANEL_WIDTH, TOP_PADDING,
                       MENU_BUTTON_HEIGHT, MENU_BUTTON_VERTICAL_SPACING, MENU_BUTTON_TARGET_WIDTH, # Keep existing
                       MENU_BUTTON_TEXT_COLOR, MENU_BUTTON_TEXT_PADDING, SCREEN_WIDTH, # Keep existing
                       MENU_ACTIONS_TITLE_FONT_SIZE, MENU_PADDING_BELOW_TITLE # Add these two
                       # arcade.color is used directly for some fallbacks/title, not from constants module
                      )
from character_creation_view import CharacterCreationView
from grimoire_view import GrimoireView
import os # For scanning save files directory
from game_view import GameView
from scripts.world import World

logging.getLogger('arcade').setLevel(logging.INFO)


class MenuView(arcade.View):
    """
    Main menu view for the game, featuring a background image and horizontal buttons.
    """
    def __init__(self):
        super().__init__()
        # Load background image
        self.background_texture = None # Initialize
        try:
            self.background_texture = arcade.load_texture(BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Error: Background image '{BACKGROUND_IMAGE}' not found.")
            print("Please make sure the image file is in the correct path or update the 'BACKGROUND_IMAGE' constant.")

        # Load top banner background
        self.top_banner_texture = None
        try:
            self.top_banner_texture = arcade.load_texture(TOP_BANNER_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: Top banner background image '{TOP_BANNER_BACKGROUND_IMAGE}' not found for MenuView.")

        # Load menu button texture (consistent with GameView)
        self.menu_button_texture = None # Initialize
        try:
            self.menu_button_texture = arcade.load_texture(MENU_BUTTON_IMAGE_PATH)
        except FileNotFoundError:
            print(f"ERROR: Menu button image not found at {MENU_BUTTON_IMAGE_PATH}")
        
        # Load right panel background for MenuView
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: MenuView right panel background image '{MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        self.menu_buttons = arcade.SpriteList()
        self.menu_state = "main" # "main" or "load_game_selection"
        self.available_save_files = [] # To store tuples of (display_name, filename.json)
        self._create_menu_buttons()

    def _create_menu_buttons(self):
        """Creates the New Game, Load Game, and Quit buttons."""
        self.menu_buttons.clear()
        button_properties = [] # List of dicts: {'text': "Display Text", 'action': "action_command"}

        if self.menu_state == "main":
            button_properties = [
                {'text': "New Game", 'action': "new_game"},
                {'text': "Load Game", 'action': "show_load_options"},
                {'text': "Grimoire", 'action': "grimoire"},
                {'text': "Quit", 'action': "quit"}
            ]
        elif self.menu_state == "load_game_selection":
            for display_name, filename in self.available_save_files:
                button_properties.append({'text': display_name, 'action': f"load_selected_{filename}"})
            button_properties.append({'text': "Back", 'action': "back_to_main_menu"})
        
        menu_content_area_top_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        title_area_height = MENU_ACTIONS_TITLE_FONT_SIZE + MENU_PADDING_BELOW_TITLE # Approx height for a title if we had one
        
        # Start buttons lower in the MenuView, perhaps centered vertically in the panel
        available_button_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - (2 * TOP_PADDING) # Total height for buttons
        total_buttons_height = len(button_properties) * MENU_BUTTON_HEIGHT + (len(button_properties) -1) * MENU_BUTTON_VERTICAL_SPACING
        first_button_center_y = menu_content_area_top_y - TOP_PADDING - (available_button_height - total_buttons_height) / 2 - MENU_BUTTON_HEIGHT / 2

        button_center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2

        for i, prop in enumerate(button_properties):
            button_sprite = arcade.Sprite(texture=self.menu_button_texture) if self.menu_button_texture else arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            button_sprite.width = MENU_BUTTON_TARGET_WIDTH
            button_sprite.height = MENU_BUTTON_HEIGHT
            button_sprite.center_x = button_center_x
            button_sprite.center_y = first_button_center_y - i * (MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING)
            button_sprite.properties['text'] = prop['text']
            button_sprite.properties['action'] = prop['action']
            self.menu_buttons.append(button_sprite)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        if self.background_texture:
            # Draw background image in the left "game art" panel
            arcade.draw_texture_rectangle(
                GAME_AREA_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2, # Center below banner
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,      # Full height below banner
                self.background_texture,
            )
        else: # Fallback if no background
            arcade.draw_rectangle_filled(
                GAME_AREA_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_GRAY
            )

        # --- Draw Top Banner (like GameView) ---
        if self.top_banner_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                self.top_banner_texture
            )
        else: # Fallback color if texture not loaded
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY 
            )
        arcade.draw_text(
            "Miniquest",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, # Centered in banner
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
        )

        # --- Draw Right-Hand Menu Panel ---
        if self.right_panel_background_texture:
            arcade.draw_texture_rectangle(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.right_panel_background_texture
            )
        else: # Fallback color
            arcade.draw_rectangle_filled(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2, 
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY 
            )

        # Draw menu buttons and their text
        self.menu_buttons.draw()

        menu_item_font_size_default = 16 # Same as GameView
        min_font_size = 6 # Same as GameView

        for button_sprite in self.menu_buttons:
            display_text = button_sprite.properties.get('text', "")
            current_font_size = menu_item_font_size_default
            button_text_max_width = button_sprite.width - (2 * MENU_BUTTON_TEXT_PADDING)

            temp_text_obj = arcade.Text(display_text, 0, 0, MENU_BUTTON_TEXT_COLOR, font_size=current_font_size)
            text_width = temp_text_obj.content_width
            
            while text_width > button_text_max_width and current_font_size > min_font_size:
                current_font_size -= 1
                temp_text_obj = arcade.Text(display_text, 0, 0, MENU_BUTTON_TEXT_COLOR, font_size=current_font_size)
                text_width = temp_text_obj.content_width

            arcade.draw_text(
                display_text,
                button_sprite.center_x,
                button_sprite.center_y,
                MENU_BUTTON_TEXT_COLOR,
                font_size=current_font_size,
                anchor_x="center",
                anchor_y="center",
                width=int(button_text_max_width)
            )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        clicked_buttons = arcade.get_sprites_at_point((x,y), self.menu_buttons)
        if clicked_buttons:
            action = clicked_buttons[0].properties.get('action')
            if action == "new_game":
                print("--- New Game button pressed! ---")
                cc_view = CharacterCreationView(self)
                self.window.show_view(cc_view)
            elif action == "show_load_options":
                print("--- Load Game (show options) button pressed! ---")
                self._scan_for_save_files()
                if not self.available_save_files:
                    print("No save files found.")
                    # Optionally, you could add a temporary message to the screen here
                    # or just rely on the console print for now.
                    # To keep it simple, we'll just refresh the main menu.
                    self.menu_state = "main" 
                else:
                    self.menu_state = "load_game_selection"
                self._create_menu_buttons() # Rebuild buttons based on new state
            
            # Check if action is a string before calling string methods
            elif isinstance(action, str) and action.startswith("load_selected_"):
                filename_to_load = action.replace("load_selected_", "") # Now safe
                print(f"--- Attempting to load save file: {filename_to_load} ---")
                loaded_world = World.load_game(filename_to_load) # Pass the specific filename
                if loaded_world: # If load_game returns a World instance
                    game_view = GameView(loaded_world) # Create GameView with the loaded world

                    # Prime GameView with loaded world's state
                    game_view.log_messages_to_display.clear() 

                    loaded_world.display_current_area() # This appends to world's log
                    game_view.log_messages_to_display.extend(loaded_world.get_messages()) 
                    
                    game_view.display_mode = "area_description"
                    game_view.update_menu_options("main")
                    game_view.load_current_area_art() 
                    game_view._prepare_scrollable_text_for_current_mode()

                    self.window.show_view(game_view)
                else:
                    print(f"Failed to load game: {filename_to_load}")
                    # Potentially show an error message to the user on screen
                    # For now, just return to the load game selection or main menu
                    self.menu_state = "load_game_selection" # Or "main"
                    self._create_menu_buttons()

            elif action == "back_to_main_menu":
                self.menu_state = "main"
                self.available_save_files.clear()
                self._create_menu_buttons()

            elif action == "grimoire":
                print("--- Grimoire button pressed! (Main Menu) ---")
                # Instantiate Builder to load grimoire entries
                # Pass a simple lambda for message_log as MenuView doesn't have a world.append_message
                builder = World().builder # Temporarily create a world to access its builder
                # A bit inefficient, but World handles builder init.
                # Alternatively, instantiate Builder directly if its init is simple.
                grimoire_entries = builder.build_grimoire_entries()
                grimoire_view = GrimoireView(grimoire_entries, self)
                self.window.show_view(grimoire_view)
            elif action == "quit":
                print("--- Quit button pressed! Exiting game. ---")
                arcade.exit()

    def _scan_for_save_files(self):
        """Scans the save directory for .json files and populates available_save_files."""
        self.available_save_files.clear()
        save_dir = os.path.join(ASSETS_DIR, 'save_files') # Use ASSETS_DIR from constants
        if not os.path.exists(save_dir):
            print(f"Save directory not found: {save_dir}")
            return

        for filename in os.listdir(save_dir):
            if filename.endswith(".json"):
                # Display name is filename without .json, spaces for underscores, capitalized
                display_name = os.path.splitext(filename)[0].replace("_", " ").capitalize()
                self.available_save_files.append((display_name, filename))
        self.available_save_files.sort() # Sort by display name

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Optional: Add hover effect for the new sprite buttons if desired
        # This would involve checking collision and changing texture or drawing an overlay.
        # For simplicity, hover effect is omitted here but can be added similarly to GameView's buttons.
        pass