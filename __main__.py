import logging
import arcade.color
from scripts.world import World
# Builder import removed as it's not directly used in __main__.py
import arcade
import os
import sys
from collections import Counter # For counting items in inventory display
import textwrap # For wrapping text into lines

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

# --- Game View Constants ---
PLAYER_INFO_BANNER_HEIGHT = 80 # Height for the top player info banner
TOP_PADDING = 20 # Padding from the top of the screen for text
LEFT_PADDING = 10 # Padding from the left of the main game area for text
RIGHT_MENU_X_START = GAME_AREA_WIDTH # X-coordinate where the right menu begins

# Determine the absolute path to the 'miniquest' package directory (where __main__.py resides)
PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PACKAGE_ROOT_DIR, 'assets')
ART_BASE_PATH = os.path.join(ASSETS_DIR, "art") # Base path for all art
 
# New structured art paths
UI_ART_PATH = os.path.join(ART_BASE_PATH, "ui")
LOCATION_ART_PATH = os.path.join(ART_BASE_PATH, "location")
ITEM_ICON_ART_PATH = os.path.join(ART_BASE_PATH, "item_icons") # For future use when displaying icons

BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_title.jpg")
PLACEHOLDER_ART = os.path.join(LOCATION_ART_PATH, "placeholder.jpg") # Make sure this file exists in the new location folder!
 
TOP_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_menu.png")
GAME_VIEW_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_game.png")
MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png")
GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png") # Assuming same as menu for now

# New constants for scrollable text areas
TEXT_AREA_LINE_HEIGHT = 18  # Pixel height for each line of text, including some padding
TEXT_AREA_FONT_SIZE = 12    # Font size for area descriptions
LOG_AREA_FONT_SIZE = 12       # Font size for combat/event logs

# New constants for menu buttons with images
MENU_BUTTON_IMAGE_PATH = os.path.join(UI_ART_PATH, "menu_button.png")
MENU_BUTTON_TARGET_WIDTH = MENU_PANEL_WIDTH - 30 # Target width: Panel width minus 15px padding on each side
MENU_BUTTON_HEIGHT = 40 # Further reduced height to make them less "dramatic"
MENU_BUTTON_TEXT_COLOR = arcade.color.WHITE
MENU_BUTTON_VERTICAL_SPACING = 8 # Significantly increased space between buttons
MENU_BUTTON_TEXT_PADDING = 10 # Padding for text inside the button (e.g., 5px on each side for centering)
MENU_ACTIONS_TITLE_FONT_SIZE = 24 # Font size of the "Actions" title
MENU_PADDING_BELOW_TITLE = 15 # Padding between the "Actions" title and the first button


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
            print(f"ERROR: Menu button image not found at {MENU_BUTTON_IMAGE_PATH} for MenuView")
        
        # Load right panel background for MenuView
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: MenuView right panel background image '{MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        self.menu_buttons = arcade.SpriteList()
        self._create_menu_buttons()

    def _create_menu_buttons(self):
        """Creates the New Game, Load Game, and Quit buttons."""
        self.menu_buttons.clear()
        button_texts = ["New Game", "Load Game", "Quit"]
        
        menu_content_area_top_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        title_area_height = MENU_ACTIONS_TITLE_FONT_SIZE + MENU_PADDING_BELOW_TITLE # Approx height for a title if we had one
        
        # Start buttons lower in the MenuView, perhaps centered vertically in the panel
        available_button_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - (2 * TOP_PADDING) # Total height for buttons
        total_buttons_height = len(button_texts) * MENU_BUTTON_HEIGHT + (len(button_texts) -1) * MENU_BUTTON_VERTICAL_SPACING
        first_button_center_y = menu_content_area_top_y - TOP_PADDING - (available_button_height - total_buttons_height) / 2 - MENU_BUTTON_HEIGHT / 2

        button_center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2

        for i, text in enumerate(button_texts):
            button_sprite = arcade.Sprite(texture=self.menu_button_texture) if self.menu_button_texture else arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            button_sprite.width = MENU_BUTTON_TARGET_WIDTH
            button_sprite.height = MENU_BUTTON_HEIGHT
            button_sprite.center_x = button_center_x
            button_sprite.center_y = first_button_center_y - i * (MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING)
            button_sprite.properties['text'] = text
            button_sprite.properties['action'] = text.lower().replace(" ", "_") # e.g., "new_game"
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
                game_world = World()
                game_world.create_character() 
                game_view = GameView(game_world)
                self.window.show_view(game_view)
            elif action == "load_game":
                print("--- Load Game button pressed! (Not implemented) ---")
                # Placeholder: For now, acts like New Game
                game_world = World()
                game_world.create_character()
                game_view = GameView(game_world)
                self.window.show_view(game_view)
            elif action == "quit":
                print("--- Quit button pressed! Exiting game. ---")
                arcade.exit()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Optional: Add hover effect for the new sprite buttons if desired
        # This would involve checking collision and changing texture or drawing an overlay.
        # For simplicity, hover effect is omitted here but can be added similarly to GameView's buttons.
        pass


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

        # Display mode for the main game area
        self.display_mode = "area_description" # Can be "area_description", "combat_log", "inventory", etc.
        self.log_messages_to_display = [] # List to hold messages retrieved from world.message_log

        # For scrollable text
        self.scroll_offset_y = 0.0  # How many pixels the text content has been scrolled up
        self.current_scrollable_lines = [] # Stores the pre-wrapped lines for the current view
        self.scrollable_text_rect_on_screen = None # To store screen coords of the text box for scroll detection

        # For "Check Bags" functionality
        self.pre_bags_view_mode = None
        self.pre_bags_menu_type = None
        self.active_menu_type = "main" # Track the current menu type

        # Load top banner background
        self.top_banner_texture = None
        try:
            self.top_banner_texture = arcade.load_texture(GAME_VIEW_BANNER_BACKGROUND_IMAGE) # Use GameView specific banner
        except FileNotFoundError:
            print(f"Warning: GameView banner background image '{GAME_VIEW_BANNER_BACKGROUND_IMAGE}' not found.")

        # Load right panel background for GameView
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: GameView right panel background image '{GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        # For menu buttons with images
        try:
            self.menu_button_texture = arcade.load_texture(MENU_BUTTON_IMAGE_PATH)
        except FileNotFoundError:
            print(f"ERROR: Menu button image not found at {MENU_BUTTON_IMAGE_PATH}")
            self.menu_button_texture = None # Fallback if image is missing
        self.menu_action_buttons = arcade.SpriteList()

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
        art_path = os.path.join(LOCATION_ART_PATH, art_file_name) # Use the new LOCATION_ART_PATH
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
        # self.world.display_current_area() # This is now handled more explicitly when actions resolve
        self.active_menu_type = menu_type # Store the active menu type

        self.menu_action_buttons.clear() # Clear old buttons

        if menu_type == "main":
            options_text = ["Fight", "Travel", "Rest"] # Start with base options
            if self.world.current_area.name == self.world.camp:
                options_text[0] = "1. Prepare" # Replace "Fight" with "Prepare" at camp
            else: # Only add "Check Bags" if not at camp
                options_text.insert(2, "Check Bags") # Insert before "Rest"
            self.current_menu_options = options_text
        elif menu_type == "travel":
            connections = self.world.available_travel_destinations # Use cached destinations
            options_text = [f"{i+1}. {conn}" for i, conn in enumerate(connections)]
            options_text.append(f"{len(connections) + 1}. Stay") # Option to stay in current area during travel prompt
            self.current_menu_options = options_text
        elif menu_type == "player_combat_turn": # For player's combat actions
            options_text = ["Attack", "Flee", "Check Bags"] # Add Check Bags option
            self.current_menu_options = options_text
        elif menu_type == "loot_decision": # For post-combat loot
            # Check if player can carry the pending loot item
            if self.world.pending_loot_item and self.world.player.inventory.can_carry_item(self.world.pending_loot_item):
                options_text = ["Take Item", "Leave"]
            else:
                # If cannot carry, or no pending item (should not happen if in this state)
                options_text = ["Drop Loot", "Leave"] # "Drop Loot" means discard the new item
            # No "Check Bags" here as it might complicate the loot decision flow,
            # and inventory is already shown.
            self.current_menu_options = options_text
        # elif menu_type == "player_defeated_flee_only": # This menu type is replaced
            # options_text = ["Flee Battle"] 
            # self.current_menu_options = options_text
        elif menu_type == "inventory_management": # New menu for inventory
            options_text = ["Equip Item", "View Items", "View Equipped", "Back"] # Added "Equip Item"
            self.current_menu_options = options_text
        elif menu_type == "view_bags_menu": # Menu for when viewing bags
            options_text = ["Back"]
            self.current_menu_options = options_text
        elif menu_type == "select_item_to_equip_menu":
            options_text = [f"{i+1}. {item_info['item'].name} ({item_info['item'].type}) - from {item_info['source']}" 
                            for i, item_info in enumerate(self.world.available_items_to_equip)]
            options_text.append("Back")
            self.current_menu_options = options_text
        elif menu_type == "defeat_acknowledged_menu": # New menu after defeat messages are shown at camp
            options_text = ["Get Up"]
            self.current_menu_options = options_text
        
        # Create button sprites
        # Calculate the Y position for the top of the menu content area (below player banner)
        menu_content_area_top_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        # Y position for the "Actions" title (anchored top)
        actions_title_y = menu_content_area_top_y - TOP_PADDING
        # Calculate where the first button's center should be
        first_button_center_y = actions_title_y - MENU_ACTIONS_TITLE_FONT_SIZE - MENU_PADDING_BELOW_TITLE - (MENU_BUTTON_HEIGHT / 2)
        button_center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2
        for i, raw_option_text in enumerate(self.current_menu_options):
            display_text = raw_option_text
            action_command = raw_option_text # Default action command
            if ". " in raw_option_text:
                # Check if the part before ". " is a number, to avoid stripping "Check Bags" etc.
                parts = raw_option_text.split(". ", 1)
                if len(parts) > 1 and parts[0].isdigit():
                # try:
                    prefix = raw_option_text.split(". ", 1)[0]
                    int(prefix) 
                    display_text = raw_option_text.split(". ", 1)[1]
                    action_command = display_text # Use the stripped text for command if numbered

            if self.menu_button_texture:
                button_sprite = arcade.Sprite(texture=self.menu_button_texture)
                # Directly set the target width and height. Arcade will adjust scale.
                button_sprite.width = MENU_BUTTON_TARGET_WIDTH
                button_sprite.height = MENU_BUTTON_HEIGHT
            else:
                # Fallback to a solid color sprite with the target dimensions
                button_sprite = arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            
            button_sprite.center_x = button_center_x
            button_sprite.center_y = first_button_center_y - i * (MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING)
            button_sprite.properties['display_text'] = display_text
            button_sprite.properties['action_command'] = action_command # Store the command for click handling
            self.menu_action_buttons.append(button_sprite)

    def _prepare_scrollable_text(self, full_text_content, font_size_for_metric, area_width_pixels):
        """
        Prepares full_text_content into self.current_scrollable_lines,
        wrapped to fit area_width_pixels.
        """
        self.current_scrollable_lines.clear()
        self.scroll_offset_y = 0.0  # Reset scroll when content changes

        if not full_text_content:
            return

        # Estimate characters per line for textwrap. This is an approximation.
        # Using a slightly larger factor (e.g., 0.60 to 0.65) makes textwrap more conservative.
        avg_char_width = font_size_for_metric * 0.65 # Increased factor
        if avg_char_width <= 0:
            approx_chars_per_line = 80 # Default fallback
        else:
            approx_chars_per_line = int(area_width_pixels / avg_char_width)
        
        if approx_chars_per_line <= 0: # Ensure positive width for textwrap
            approx_chars_per_line = 1

        paragraphs = full_text_content.split('\n')
        wrapped_lines = []
        for paragraph in paragraphs:
            if not paragraph.strip() and paragraph != "": # Preserve lines that are empty
                wrapped_lines.append("") # Add an empty line
            elif not paragraph.strip() and paragraph == "": # Preserve lines that are empty
                 wrapped_lines.append("")
            else:
                wrapped_lines.extend(textwrap.wrap(paragraph, width=approx_chars_per_line, 
                                                   replace_whitespace=False, drop_whitespace=False,
                                                   break_long_words=True, break_on_hyphens=True))
        self.current_scrollable_lines = wrapped_lines
        # Removed the problematic block that was overriding inventory text here.

    def _prepare_scrollable_text_for_current_mode(self):
        # Calculate the consistent, buffered width for the text area
        # This must match the 'description_width' used in on_draw's rendering logic
        consistent_text_area_width = GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5 # Buffer of 5 pixels

        if self.display_mode == "area_description":
            self._prepare_scrollable_text(self.world.current_area.description, TEXT_AREA_FONT_SIZE, consistent_text_area_width)
        elif self.display_mode == "combat_log":
            self._prepare_scrollable_text("\n".join(self.log_messages_to_display), LOG_AREA_FONT_SIZE, consistent_text_area_width)
        
        elif self.display_mode == "inventory_management":
            inventory_text = "--- Camp Preparations ---\n\n"

            inventory_text += "== Equipped Items ==\n"
            if self.player.inventory.equipped_items['Held']:
                inventory_text += f"Held: {self.player.inventory.equipped_items['Held'].name}\n"
            else:
                inventory_text += "Held: (None)\n"
            if self.player.inventory.equipped_items['Body']:
                inventory_text += f"Body: {self.player.inventory.equipped_items['Body'].name}\n"
            else:
                inventory_text += "Body: (None)\n"
            if self.player.inventory.equipped_items['Trinkets']:
                trinket_names = [t.name for t in self.player.inventory.equipped_items['Trinkets']]
                inventory_text += f"Trinkets: {', '.join(trinket_names) if trinket_names else '(None)'}\n"
            else:
                inventory_text += "Trinkets: (None)\n"
            inventory_text += "\n"

            inventory_text += "== Carried Items (In Bags) ==\n"
            if not self.player.inventory.stored_items:
                inventory_text += "(Bags are empty)\n"
            else:
                item_counts = Counter(item.name for item in self.player.inventory.stored_items)
                for name, count in item_counts.items():
                    sample_item = next(item for item in self.player.inventory.stored_items if item.name == name)
                    inventory_text += f" - {name} ({sample_item.type})"
                    if count > 1:
                        inventory_text += f" x{count}"
                    inventory_text += "\n"
            inventory_text += "\n"

            inventory_text += "== Strongbox Items (At Camp) ==\n"
            if not self.player.inventory.strongbox_items:
                inventory_text += "(Strongbox is empty)\n"
            else:
                strongbox_item_counts = Counter(item.name for item in self.player.inventory.strongbox_items)
                for name, count in strongbox_item_counts.items():
                    sample_item = next(item for item in self.player.inventory.strongbox_items if item.name == name)
                    inventory_text += f" - {name} ({sample_item.type})"
                    if count > 1:
                        inventory_text += f" x{count}"
                    inventory_text += "\n"
            
            self._prepare_scrollable_text(inventory_text, TEXT_AREA_FONT_SIZE, consistent_text_area_width)

        elif self.display_mode == "view_bags":
            bags_text = "--- Your Bags ---\n\n"
            bags_text += "== Equipped Items ==\n"
            if self.player.inventory.equipped_items['Held']: bags_text += f"Held: {self.player.inventory.equipped_items['Held'].name}\n"
            else: bags_text += "Held: (None)\n"
            if self.player.inventory.equipped_items['Body']: bags_text += f"Body: {self.player.inventory.equipped_items['Body'].name}\n"
            else: bags_text += "Body: (None)\n"
            if self.player.inventory.equipped_items['Trinkets']:
                trinket_names = [t.name for t in self.player.inventory.equipped_items['Trinkets']]
                bags_text += f"Trinkets: {', '.join(trinket_names) if trinket_names else '(None)'}\n"
            else: bags_text += "Trinkets: (None)\n"
            bags_text += "\n"
            bags_text += "== Carried Items (In Bags) ==\n"
            if not self.player.inventory.stored_items: bags_text += "(Bags are empty)\n"
            else:
                item_counts = Counter(item.name for item in self.player.inventory.stored_items)
                for name, count in item_counts.items():
                    sample_item = next(item for item in self.player.inventory.stored_items if item.name == name)
                    bags_text += f" - {name} ({sample_item.type})"
                    if count > 1: bags_text += f" x{count}"
                    bags_text += "\n"
            self._prepare_scrollable_text(bags_text, TEXT_AREA_FONT_SIZE, consistent_text_area_width)
        
        elif self.display_mode == "select_item_to_equip_display":
            equip_selection_text = "--- Select Item to Equip ---\n\n"
            if not self.world.available_items_to_equip:
                equip_selection_text += "(No equipable items found in bags or strongbox.)"
            else:
                for i, item_info in enumerate(self.world.available_items_to_equip):
                    item = item_info["item"]
                    source = item_info["source"]
                    equip_selection_text += f"{i+1}. {item.name} ({item.type}) - from {source}\n"
                    # Optionally add item stats here if desired
                    if item.description:
                         equip_selection_text += f"   Desc: {item.description}\n"
                    equip_selection_text += "\n"

            self._prepare_scrollable_text(equip_selection_text, TEXT_AREA_FONT_SIZE, consistent_text_area_width)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        # When GameView is shown, update options and load initial messages
        self.update_menu_options("main") # Set initial main menu options
        self.log_messages_to_display = self.world.get_messages() # Get welcome and character creation messages
        self._prepare_scrollable_text_for_current_mode() # Prepare initial text

    def on_draw(self):
        self.clear()

        # --- Draw Player Info Banner (Top) ---
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
                arcade.color.DARK_GRAY
            )
        # Display player stats
        player_info_y = SCREEN_HEIGHT - TOP_PADDING - (PLAYER_INFO_BANNER_HEIGHT / 2) + 20
        text_color = arcade.color.WHITE
        font_size = 12

        # Name, Level - First item on the top line
        name_level_str = f"Name: {self.player.name} | Level: {self.player.level}"
        arcade.draw_text(
            name_level_str,
            LEFT_PADDING,
            player_info_y,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
            # Removed width constraint to let it take natural width; we'll position subsequent items based on this
        )
        
        # Combat Stats (Attack, Defense, Speed)
        self.player.update_stats() # Ensure stats are fresh

        # Health
        arcade.draw_text(
            f"HP: {self.player.current_health}/{self.player.max_health} | Atk: {self.player.attack + self.player.attack_mod} | Def: {self.player.defense + self.player.defense_mod} | Spd: {self.player.speed + self.player.speed_mod}",
            LEFT_PADDING,
            player_info_y - 25,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="center", # Adjusted for better vertical alignment
            width=int(GAME_AREA_WIDTH - 2 * LEFT_PADDING),
            align="left"
        )

        # Determine time color for the "Hour" display
        time_text_color = arcade.color.RED if self.world.day_cycle.is_night() else text_color

        # --- Position Wealth and Hour dynamically after Name/Level ---
        # Measure the width of the "Name | Level" text
        name_level_text_obj = arcade.Text(name_level_str, 0, 0, text_color, font_size)
        current_x_offset = LEFT_PADDING + name_level_text_obj.content_width
        spacing_between_banner_items = 20 # Adjust as needed

        # Wealth - Positioned after Name/Level
        wealth_text_str = f"Wealth: {self.player.inventory.income}"
        wealth_text_x_start = current_x_offset + spacing_between_banner_items
        arcade.draw_text(
            wealth_text_str,
            wealth_text_x_start,
            player_info_y, # Align with Name/Level line
            text_color, # Wealth is always the default text_color
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
        )

        # Measure Wealth text to position Hour text next
        wealth_text_obj_for_measure = arcade.Text(wealth_text_str, 0, 0, text_color, font_size)
        current_x_offset = wealth_text_x_start + wealth_text_obj_for_measure.content_width

        # Hour - Positioned after Wealth, drawn separately to control its color
        hour_text_str = f" | Hour: {self.world.day_cycle.hour}"
        hour_text_x_start = current_x_offset + spacing_between_banner_items / 2 # A bit less spacing for the separator
        
        arcade.draw_text(
            hour_text_str,
            hour_text_x_start,
            player_info_y,
            time_text_color, # Hour uses the conditional color
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
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
        # Original: description_width = GAME_AREA_WIDTH - 2 * LEFT_PADDING
        description_width = GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5 # Add a small buffer (e.g., 5 pixels)
        text_bg_height = 150 # Adjust based on content. For log, it might need to be taller.
        
        # Calculate the actual height and center Y for the background rectangle
        # to ensure it covers text that might draw slightly below the nominal text_bg_height
        effective_background_height = text_bg_height + (2 * TEXT_AREA_LINE_HEIGHT) # Extend by two line heights
        effective_background_center_y = description_y - (effective_background_height / 2)

        # Draw a semi-transparent background for the text overlay
        arcade.draw_rectangle_filled(
            GAME_AREA_WIDTH / 2,
            effective_background_center_y, # Use new center_y
            description_width + 20,
            effective_background_height, # Use new height
            (0, 0, 0, 180) # Slightly more opaque for readability
        )       

        # --- Determine parameters for scrollable text based on display_mode ---
        _scroll_area_top_y_for_lines = description_y  # Default: top of the text box
        _scroll_area_height_for_lines = text_bg_height # Default: full height of text box
        _line_font_size = TEXT_AREA_FONT_SIZE
        _line_color = arcade.color.LIGHT_GRAY # Default color

        if self.display_mode == "area_description":
            # --- Location Name ---
            location_name_text = f"Location: {self.world.current_area.name}"
            name_font_size = 14 # Stays as is, not part of scrollable TEXT_AREA_FONT_SIZE
            spacing_after_name = 5 

            arcade.draw_text(
                location_name_text,
                description_x,
                description_y, # Anchored to the top of the text box
                arcade.color.LIGHT_GRAY,
                font_size=name_font_size,
                width=description_width,
                align="left",
                anchor_x="left",
                anchor_y="top",
                bold=True # Make the location name stand out
            )

            _scroll_area_top_y_for_lines = description_y - (name_font_size + spacing_after_name)
            _scroll_area_height_for_lines = text_bg_height - (name_font_size + spacing_after_name)
            _line_font_size = TEXT_AREA_FONT_SIZE
            _line_color = arcade.color.LIGHT_GRAY
        elif self.display_mode == "combat_log":
            _line_font_size = LOG_AREA_FONT_SIZE
            _line_color = arcade.color.WHITE
        elif self.display_mode == "inventory_management" or self.display_mode == "view_bags":
            _line_font_size = TEXT_AREA_FONT_SIZE 
            _line_color = arcade.color.WHITE # Brighter for inventory text

        # Update self.scrollable_text_rect_on_screen for the current mode (used by on_mouse_scroll)
        self.scrollable_text_rect_on_screen = (
            description_x,  # left_x
            _scroll_area_top_y_for_lines - _scroll_area_height_for_lines,  # bottom_y
            description_width,  # width
            _scroll_area_height_for_lines  # height
        )
        # For debugging the scroll area bounds:
        # arcade.draw_lrbt_rectangle_outline(*self.scrollable_text_rect_on_screen, arcade.color.GREEN, 1)

        # --- Common Scrollable Text Drawing Logic ---
        if self.current_scrollable_lines:
            first_visible_line_idx = int(self.scroll_offset_y / TEXT_AREA_LINE_HEIGHT)
            lines_in_view = int(_scroll_area_height_for_lines / TEXT_AREA_LINE_HEIGHT)

            for i in range(len(self.current_scrollable_lines)):
                if i < first_visible_line_idx:
                    continue
                if i > first_visible_line_idx + lines_in_view + 1:  # +1 for partially visible line
                    break
                
                line_text_content = self.current_scrollable_lines[i]
                line_y_offset_from_content_top = i * TEXT_AREA_LINE_HEIGHT
                draw_y_on_screen = _scroll_area_top_y_for_lines - (line_y_offset_from_content_top - self.scroll_offset_y)

                # Basic clipping: only draw if the line's top is within drawable vertical space
                if draw_y_on_screen <= _scroll_area_top_y_for_lines and \
                   draw_y_on_screen >= _scroll_area_top_y_for_lines - _scroll_area_height_for_lines - TEXT_AREA_LINE_HEIGHT:
                    arcade.draw_text(
                        line_text_content,
                        description_x, # Use description_x as the consistent left starting point
                        draw_y_on_screen,
                        _line_color,
                        font_size=_line_font_size,
                        width=description_width, # Use description_width for consistency
                        anchor_x="left",
                        anchor_y="top"
                    )

        # --- Draw Right-Hand Menu ---
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

        # Draw menu buttons and their text
        self.menu_action_buttons.draw()

        menu_item_font_size_default = 16
        min_font_size = 6 # Further reduced minimum font size

        for button_sprite in self.menu_action_buttons:
            display_text = button_sprite.properties.get('display_text', "")
            current_font_size = menu_item_font_size_default
            
            # Max width for text on this button
            button_text_max_width = button_sprite.width - (2 * MENU_BUTTON_TEXT_PADDING)
            initial_font_size_for_button = current_font_size # For debugging
            
            # Measure text width using arcade.measure_text()
            # Revert to using arcade.Text for measurement if arcade.measure_text is not available
            temp_text_obj = arcade.Text(
                display_text, 0, 0, # x, y not relevant for measurement
                MENU_BUTTON_TEXT_COLOR,
                font_size=current_font_size
            )
            text_width = temp_text_obj.content_width # Use content_width for more reliable measurement
            
            while text_width > button_text_max_width and current_font_size > min_font_size:
                current_font_size -= 1
                # Recalculate width with the new font size
                temp_text_obj = arcade.Text(
                    display_text, 0, 0, MENU_BUTTON_TEXT_COLOR,
                    font_size=current_font_size
                )
                text_width = temp_text_obj.content_width # Use content_width here as well

            arcade.draw_text(
                display_text, # Use the processed text without numbers
                button_sprite.center_x,
                button_sprite.center_y,
                MENU_BUTTON_TEXT_COLOR,
                font_size=current_font_size, # Use dynamically adjusted font size
                anchor_x="center", # Center text on the button
                anchor_y="center", # Center text on the button
                width=int(button_text_max_width) # Also provide width to draw_text for potential internal wrapping
            )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        print(f"Mouse pressed at ({x}, {y}) in GameView")
        
        # Check if click is within the right-hand menu area
        if x > RIGHT_MENU_X_START:
            # Check for clicks on the new button sprites
            clicked_buttons = arcade.get_sprites_at_point((x, y), self.menu_action_buttons)
            if clicked_buttons:
                clicked_button = clicked_buttons[0] # Get the first button clicked (should only be one)
                command = clicked_button.properties.get('action_command', "")
                
                print(f"Clicked button: '{command}'")

                # --- Handle locally managed view changes first ---
                if command == "Back" and self.display_mode == "inventory_management":
                    self.display_mode = "area_description"
                    self.update_menu_options("main")
                    self.log_messages_to_display.clear()
                    self.world.display_current_area() # Get area description
                    self.log_messages_to_display.extend(self.world.get_messages())
                    self._prepare_scrollable_text_for_current_mode()
                    return # Handled locally
                
                elif command == "Back" and self.active_menu_type == "select_item_to_equip_menu":
                    # Go back to the main inventory management view
                    self.display_mode = "inventory_management"
                    self.update_menu_options("inventory_management")
                    self.log_messages_to_display.clear() # Clear selection prompt
                    # Messages for inventory_management are usually just the inventory listing itself
                    self._prepare_scrollable_text_for_current_mode()
                    self.world.available_items_to_equip.clear() # Clear the list in world
                    return # Handled locally

                elif command == "Check Bags":
                    self.pre_bags_view_mode = self.display_mode
                    self.pre_bags_menu_type = self.active_menu_type # Use stored active_menu_type
                    
                    self.display_mode = "view_bags"
                    self.update_menu_options("view_bags_menu")
                    
                    self.log_messages_to_display.clear()
                    self._prepare_scrollable_text_for_current_mode()
                    return # Handled locally

                elif command == "Back" and self.active_menu_type == "view_bags_menu": # Specifically "Back" from bags view
                    self.display_mode = self.pre_bags_view_mode if self.pre_bags_view_mode else "area_description"
                    current_menu_to_restore = self.pre_bags_menu_type if self.pre_bags_menu_type else "main"
                    self.update_menu_options(current_menu_to_restore)
                    
                    self.log_messages_to_display.clear()
                    if self.display_mode == "area_description":
                        # If returning to area description, fetch any pending messages from world
                        # (e.g., if "Check Bags" was used during travel prompt)
                        self.log_messages_to_display.extend(self.world.get_messages()) 
                    elif self.display_mode == "combat_log" and current_menu_to_restore == "player_combat_turn":
                        # If returning to player's combat turn, re-add turn prompt
                        self.log_messages_to_display.append("--- Your Turn ---")
                        self.log_messages_to_display.append("It's your turn!")
                    
                    self._prepare_scrollable_text_for_current_mode()
                    return # Handled locally

                # --- If not a local view change, proceed with world interaction ---
                self.log_messages_to_display.clear()
                
                # Construct command for equipping if in selection mode
                action_command_to_world = command
                if self.active_menu_type == "select_item_to_equip_menu" and command.isdigit(): # Assuming button text is just the number
                    action_command_to_world = f"Equip Index: {int(command)-1}" # Convert 1-based to 0-based index
                
                next_game_state = self.world.handle_player_choice(action_command_to_world)
                self.log_messages_to_display.extend(self.world.get_messages())
                
                # Update local state based on world's decision
                if next_game_state == "player_combat_turn":
                    self.display_mode = "combat_log"
                    self.update_menu_options("player_combat_turn") # Show Attack/Flee buttons
                elif next_game_state == "travel_options":
                    self.display_mode = "area_description" # Stay in description to show travel prompt
                    self.update_menu_options("travel") # This will rebuild buttons for travel
                elif next_game_state == "loot_decision":
                    self.display_mode = "combat_log" # Show loot messages in the log area
                    self.update_menu_options("loot_decision") # Show Take/Leave buttons
                    # Prepare text to show current inventory relevant to loot decision
                    loot_info_text = "--- Loot Found! ---\n"
                    if self.world.pending_loot_item:
                        loot_info_text += f"You found: {self.world.pending_loot_item.name} ({self.world.pending_loot_item.type})\n\n"
                        loot_info_text += "Your carried items:\n"
                        if self.world.player.inventory.stored_items:
                            for item in self.world.player.inventory.stored_items:
                                loot_info_text += f" - {item.name} ({item.type})\n"
                        else:
                            loot_info_text += "(None carried)\n"
                    self._prepare_scrollable_text(loot_info_text, LOG_AREA_FONT_SIZE, GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5)
                # elif next_game_state == "player_defeated_must_flee": # This state is removed
                    # self.display_mode = "combat_log" # Show defeat messages
                    # self.update_menu_options("player_defeated_flee_only") # Show only "Flee Battle"
                elif next_game_state == "show_defeat_log_at_camp": # New state after player is defeated
                    self.display_mode = "combat_log" # Show defeat messages
                    self.load_current_area_art() # World has moved player to camp, update art
                    self.update_menu_options("defeat_acknowledged_menu") # Show "Continue" button
                elif next_game_state == "inventory_management": # Player chose "Prepare"
                    self.display_mode = "inventory_management"
                    self.update_menu_options("inventory_management")
                elif next_game_state == "select_item_to_equip_mode": # World wants us to show item selection
                    self.display_mode = "select_item_to_equip_display"
                    self.update_menu_options("select_item_to_equip_menu")
                    # Log messages (like "Select an item...") are already added by world
                elif next_game_state == "area_description": # Combat ended, or general action
                    self.display_mode = "area_description"
                    self.update_menu_options("main") # Rebuild main action buttons
                    self.load_current_area_art() # Reload art in case of travel

                self._prepare_scrollable_text_for_current_mode() # Prepare text for the new state
                # No need to explicitly call self.on_draw(), the game loop handles it.
                return # Exit after processing a button click

        else: # Click was outside the menu area (e.g., in the main game art area)
            # Clicks outside the right-hand menu should not trigger game state changes.
            # The player must use the buttons in the menu to proceed.
            pass
    def on_update(self, delta_time: float):
        """ Called every frame to update game logic. """
        self.player.update_stats()
        # The player death and retreat logic is now handled through the
        # "player_defeated_must_flee" and "returned_to_camp_after_defeat" states
        # triggered by world.handle_player_choice and processed in on_mouse_press.
        # So, the direct check for self.player.is_dead() here is no longer needed
        # to initiate the retreat sequence.

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """ Handle mouse scroll events for the text area. """
        if self.scrollable_text_rect_on_screen:
            s_rect_x, s_rect_bottom_y, s_rect_width, s_rect_height = self.scrollable_text_rect_on_screen
            s_rect_top_y = s_rect_bottom_y + s_rect_height

            # Check if mouse is over the scrollable text area
            if s_rect_x <= x <= s_rect_x + s_rect_width and \
               s_rect_bottom_y <= y <= s_rect_top_y:
                
                # scroll_y is +1 for wheel up (scroll content up), -1 for wheel down (scroll content down)
                self.scroll_offset_y -= scroll_y * TEXT_AREA_LINE_HEIGHT * 2 # Multiply for faster scroll

                # Clamp scroll_offset_y
                total_content_height = len(self.current_scrollable_lines) * TEXT_AREA_LINE_HEIGHT
                
                max_scroll = max(0, total_content_height - s_rect_height)
                if total_content_height <= s_rect_height: # If content fits, no scroll needed
                    self.scroll_offset_y = 0
                else:
                    self.scroll_offset_y = arcade.clamp(self.scroll_offset_y, 0, max_scroll)


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