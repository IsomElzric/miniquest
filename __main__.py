import logging
import arcade.color
from scripts.world import World
# Builder import removed as it's not directly used in __main__.py
import arcade
import os
import sys
from collections import Counter # For counting items in inventory display and grimoire topics
from scripts.inventory import EQUIPABLE_TYPES # Import for checking if item is equipable
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
TOP_PADDING = 0 # Padding from the bottom of banner for text-based views
ICON_PANEL_TOP_MARGIN = 5 # Padding from the bottom of banner for icon-based views
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
INVENTORY_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_inventory.jpg") # New background for inventory
GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png") # Assuming same as menu for now

# New constants for scrollable text areas
TEXT_AREA_LINE_HEIGHT = 22  # Pixel height for each line of text, including some padding - INCREASED
TEXT_AREA_FONT_SIZE = 12    # Font size for area descriptions - REMAINS 12
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

# --- Item Icon Display Constants ---
ITEM_ICON_DRAW_SIZE = (32, 32) # The size to draw icons on screen
ITEM_ICON_VERTICAL_SPACING = 10 # Space between item rows (icon + text)
ITEM_TEXT_OFFSET_X = ITEM_ICON_DRAW_SIZE[0] + 10 # Horizontal offset for text next to icon
ITEM_SECTION_SPACING = 20 # Vertical space between "Equipped", "Carried", "Strongbox" sections


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
        self._create_menu_buttons()

    def _create_menu_buttons(self):
        """Creates the New Game, Load Game, and Quit buttons."""
        self.menu_buttons.clear()
        button_texts = ["New Game", "Load Game", "Grimoire", "Quit"] # Added Grimoire
        
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
                print("--- Load Game button pressed! ---")
                loaded_world = World.load_game()
                if loaded_world:
                    game_view = GameView(loaded_world)
                    
                    # Prime GameView with loaded world's state
                    game_view.log_messages_to_display.clear() 
                    # Ensure the world's current area description is in the log for initial display
                    loaded_world.display_current_area() # This appends to world's log
                    game_view.log_messages_to_display.extend(loaded_world.get_messages()) 
                    
                    game_view.display_mode = "area_description"
                    game_view.update_menu_options("main")
                    game_view.load_current_area_art() 
                    game_view._prepare_scrollable_text_for_current_mode()

                    self.window.show_view(game_view)
                else:
                    print("Failed to load game or no save file found.")
                    # Optionally, display a message to the user on the MenuView itself.
                    # For now, we'll just print to console.
                    # To show a message on screen, you might add a temporary text element to MenuView
                    # or switch to a simple "message view".
                    # Example: self.show_load_error_message()
                    pass # Stay on MenuView

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

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        # Optional: Add hover effect for the new sprite buttons if desired
        # This would involve checking collision and changing texture or drawing an overlay.
        # For simplicity, hover effect is omitted here but can be added similarly to GameView's buttons.
        pass


class GrimoireView(arcade.View):
    """
    View for displaying Grimoire topics and entries.
    """
    def __init__(self, grimoire_entries_list, previous_view: arcade.View):
        super().__init__()
        self.grimoire_entries = grimoire_entries_list
        self.previous_view = previous_view # Keep reference to return to

        # Load top banner background for GrimoireView
        self.top_banner_texture = None
        try:
            self.top_banner_texture = arcade.load_texture(GAME_VIEW_BANNER_BACKGROUND_IMAGE) # Use GameView banner
        except FileNotFoundError:
            print(f"Warning: GrimoireView banner background image '{GAME_VIEW_BANNER_BACKGROUND_IMAGE}' not found.")
        self.background_texture = None # Placeholder for potential background, not used yet

        # Load menu button texture for the Back button
        self.menu_button_texture = None
        try:
            self.menu_button_texture = arcade.load_texture(MENU_BUTTON_IMAGE_PATH)
        except FileNotFoundError:
            print(f"ERROR: GrimoireView - Menu button image not found at {MENU_BUTTON_IMAGE_PATH}")

        # Load right panel background for GrimoireView
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE) # Use GameView's panel
        except FileNotFoundError:
            print(f"Warning: GrimoireView right panel background image '{GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        # UI Elements
        if self.menu_button_texture:
            self.back_button = arcade.Sprite(texture=self.menu_button_texture)
        else: # Fallback if texture not loaded
            self.back_button = arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.YELLOW_GREEN) # BRIGHTER FALLBACK FOR DIAGNOSTICS
        self.back_button.width = MENU_BUTTON_TARGET_WIDTH
        self.back_button.height = MENU_BUTTON_HEIGHT
        self.back_button.center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2 # Place in right panel
        self.back_button.center_y = MENU_BUTTON_HEIGHT * 1.5 # Near bottom of right panel
        self.back_button.properties['text'] = "Back"
        self.back_button.properties['action'] = "back"

        # State Management
        self.display_state = "list"  # "list" or "details"
        self.selected_entry_data = None # Stores the dict of the selected grimoire entry
        self._absolute_y_positions = {} # Store absolute Y positions for topics/lines
        
        self.topic_clickable_sprites = arcade.SpriteList() # For clickable topic entries in list view
        
        # Scrolling
        self.scroll_offset_y = 0.0
        self.current_scrollable_lines = [] # For topic list or topic details
        self.current_content_height = 0.0
        
        # Define the main scrollable area (below banner, left of right menu)
        self.scrollable_rect_on_screen = (
            LEFT_PADDING, # Left
            BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING, # Bottom (above where a back button might be if it were at the screen bottom)
            GAME_AREA_WIDTH - (2 * LEFT_PADDING), # Width
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - (BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING) - TOP_PADDING # Height
        )

        # Sort entries for consistent display: by category, then by title
        if self.grimoire_entries:
            self.grimoire_entries.sort(key=lambda x: (x['category'].lower(), x['title'].lower()))

        self._prepare_display() # Initial preparation

        # print(f"GrimoireView initialized. Previous view: {type(previous_view).__name__}")
        # if self.grimoire_entries:
        #     print(f"Number of grimoire entries: {len(self.grimoire_entries)}")
        # else:
        #     print("Warning: GrimoireView received no grimoire entries.")
    
    def on_hide_view(self):
        # Clean up sprites if necessary, though Arcade usually handles this
        self.topic_clickable_sprites.clear()
        return super().on_hide_view()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        # --- Draw Top Banner (like GameView/MenuView) ---
        if self.top_banner_texture:
             arcade.draw_texture_rectangle(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                self.top_banner_texture # Use GrimoireView's own banner
            )
        else:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY # Fallback color
            )

        arcade.draw_text(
            "Grimoire of Whispers",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, # Centered in banner
            arcade.color.WHITE,
            font_size=30, # Slightly smaller than main title
            anchor_x="center",
            anchor_y="center",
        )

        # --- Draw Main Content Area (Left of Menu) ---
        arcade.draw_rectangle_filled(
            GAME_AREA_WIDTH / 2,
            (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
            GAME_AREA_WIDTH,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
            (0,0,0,180) # Semi-transparent black overlay
        )

        # Draw scrollable content (topic list or details)
        # Manual clipping is used instead of set_viewport for Grimoire text.

        # Ensure scroll_offset_y is clamped before calculating drawing positions
        viewport_height = self.scrollable_rect_on_screen[3] 
        max_scroll = max(0, self.current_content_height - viewport_height)
        self.scroll_offset_y = arcade.clamp(self.scroll_offset_y, 0, max_scroll)
        
        # This is the Y-coordinate for the TOP of the first element to be drawn, after scrolling.
        current_y_for_drawing_on_screen = int(self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3] - self.scroll_offset_y)

        if self.display_state == "list":
            current_category = None
            for sprite in self.topic_clickable_sprites:
                entry_data = sprite.properties['entry_data']
                if entry_data['category'] != current_category:
                    current_category = entry_data['category']
                    category_header_height = int(TEXT_AREA_LINE_HEIGHT * 1.5)
                    # Manual clipping for category header
                    if current_y_for_drawing_on_screen > self.scrollable_rect_on_screen[1] and \
                       current_y_for_drawing_on_screen - category_header_height < self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]:
                        arcade.draw_text(
                            f"--- {current_category} ---",
                            self.scrollable_rect_on_screen[0] + 5, 
                            current_y_for_drawing_on_screen, 
                            arcade.color.GOLD,
                            font_size=TEXT_AREA_FONT_SIZE + 2,
                            bold=True,
                            anchor_y="top"
                        )
                    current_y_for_drawing_on_screen -= category_header_height 
                
                topic_line_height = int(TEXT_AREA_LINE_HEIGHT)
                # Manual clipping for topic text
                if current_y_for_drawing_on_screen > self.scrollable_rect_on_screen[1] and \
                   current_y_for_drawing_on_screen - topic_line_height < self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]:
                    arcade.draw_text(
                        f"  {entry_data['title']}", 
                        self.scrollable_rect_on_screen[0] + 10, 
                        current_y_for_drawing_on_screen, 
                        arcade.color.WHITE,
                        font_size=TEXT_AREA_FONT_SIZE,
                        anchor_y="top"
                    )                
                # Update sprite's actual screen Y for collision detection
                sprite.center_y = current_y_for_drawing_on_screen - int(TEXT_AREA_LINE_HEIGHT / 2)
                sprite.center_x = self.scrollable_rect_on_screen[0] + (self.scrollable_rect_on_screen[2] / 2) 
                sprite.width = self.scrollable_rect_on_screen[2] - 20 
                sprite.height = TEXT_AREA_LINE_HEIGHT
                # sprite.draw_hit_box(arcade.color.RED, line_thickness=1) # For debugging clicks

                current_y_for_drawing_on_screen -= topic_line_height 
        
        elif self.display_state == "details" and self.selected_entry_data: 
            # Draw Topic Title
            title_absolute_y = self._absolute_y_positions.get('title_y', self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3])
            title_draw_y = int(title_absolute_y - self.scroll_offset_y)
            title_height = int(TEXT_AREA_LINE_HEIGHT * 1.5) 
            if title_draw_y > self.scrollable_rect_on_screen[1] and \
               title_draw_y - title_height < self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]:
                arcade.draw_text(
                    f"Topic: {self.selected_entry_data['title']}",
                    self.scrollable_rect_on_screen[0], 
                    title_draw_y,
                    arcade.color.CYAN,
                    font_size=TEXT_AREA_FONT_SIZE + 4,
                    bold=True,
                    anchor_y="top"
                )
            
            current_desc_draw_y = title_draw_y - int(TEXT_AREA_LINE_HEIGHT * 1.5) 

            for line_text in self.current_scrollable_lines:
                desc_line_height = int(TEXT_AREA_LINE_HEIGHT)
                # Manual clipping for description lines
                if int(current_desc_draw_y) > self.scrollable_rect_on_screen[1] and \
                   int(current_desc_draw_y) - desc_line_height < self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]:
                    arcade.draw_text(
                        line_text,
                        self.scrollable_rect_on_screen[0], 
                        int(current_desc_draw_y), 
                        arcade.color.WHITE,
                        font_size=TEXT_AREA_FONT_SIZE,
                        anchor_y="top",
                        width=int(self.scrollable_rect_on_screen[2]) 
                    )
                current_desc_draw_y -= desc_line_height
                
        arcade.get_window().use() # Reset viewport to full screen. This is important!

        # --- Draw Right-Hand Menu Panel (for the Back button) ---
        if self.right_panel_background_texture:
            arcade.draw_texture_rectangle(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.right_panel_background_texture
            )
        else: 
            arcade.draw_rectangle_filled(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY 
            )
        self.back_button.draw()
        arcade.draw_text("Back", self.back_button.center_x, self.back_button.center_y,
                         arcade.color.WHITE, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center")
        # print(f"DEBUG: Back button drawn at center=({self.back_button.center_x}, {self.back_button.center_y}), visible={self.back_button.visible}, texture={self.back_button.texture is not None}")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.back_button.collides_with_point((x,y)):
            if self.display_state == "details":
                self.display_state = "list"
                self.selected_entry_data = None
                self.scroll_offset_y = 0.0 
                self._prepare_display()
            else: 
                self.window.show_view(self.previous_view)
            return

        if self.display_state == "list":
            clicked_topic_sprites = arcade.get_sprites_at_point((x, y), self.topic_clickable_sprites)
            if clicked_topic_sprites:
                self.selected_entry_data = clicked_topic_sprites[0].properties['entry_data']
                self.display_state = "details"
                self.scroll_offset_y = 0.0 
                self._prepare_display()
                return

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        s_rect_x, s_rect_bottom_y, s_rect_width, s_rect_height = self.scrollable_rect_on_screen
        s_rect_top_y = s_rect_bottom_y + s_rect_height

        if s_rect_x <= x <= s_rect_x + s_rect_width and \
           s_rect_bottom_y <= y <= s_rect_top_y:
            
            self.scroll_offset_y -= scroll_y * TEXT_AREA_LINE_HEIGHT # Reverted to -= for working clamping
            
            # Clamping is now done at the start of on_draw
            # viewport_height = self.scrollable_rect_on_screen[3] 
            # max_scroll = max(0, self.current_content_height - viewport_height) 
            # self.scroll_offset_y = arcade.clamp(self.scroll_offset_y, 0, max_scroll) # Clamping is now in on_draw
            print(f"Scroll Event: scroll_y_input={scroll_y}, new_offset_y_before_clamp={self.scroll_offset_y:.2f}")

    def _prepare_display(self):
        self.current_scrollable_lines.clear()
        self.topic_clickable_sprites.clear() 
        self._absolute_y_positions.clear() 

        if self.display_state == "list":
            self.current_content_height = 0
            current_category = None
            if not self.grimoire_entries:
                self.current_scrollable_lines.append("(No grimoire entries found)")
                self.current_content_height = TEXT_AREA_LINE_HEIGHT
                return

            y_cursor_for_layout = self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]

            for entry in self.grimoire_entries:
                if entry['category'] != current_category:
                    current_category = entry['category']
                    category_header_height = (TEXT_AREA_LINE_HEIGHT * 1.5)
                    self.current_content_height += category_header_height
                    y_cursor_for_layout -= category_header_height
                
                topic_line_height = TEXT_AREA_LINE_HEIGHT
                topic_sprite = arcade.SpriteSolidColor(int(self.scrollable_rect_on_screen[2] - 20), int(topic_line_height), (0,0,0,0)) 
                topic_sprite.properties['entry_data'] = entry
                topic_sprite.properties['absolute_y'] = y_cursor_for_layout 
                self.topic_clickable_sprites.append(topic_sprite)
                y_cursor_for_layout -= topic_line_height
                self.current_content_height += topic_line_height

        elif self.display_state == "details" and self.selected_entry_data:
            current_absolute_y = self.scrollable_rect_on_screen[1] + self.scrollable_rect_on_screen[3]
            self._absolute_y_positions['title_y'] = current_absolute_y
            # current_absolute_y -= (TEXT_AREA_LINE_HEIGHT * 1.5) # This was for layout, not needed for content height here

            description_value_from_entry = self.selected_entry_data.get('description')
            if description_value_from_entry is None:
                description_text = "No description available." 
            else:
                description_text = str(description_value_from_entry) 

            area_width_pixels = self.scrollable_rect_on_screen[2]
            font_size_for_metric = TEXT_AREA_FONT_SIZE
            avg_char_width = font_size_for_metric * 0.65  
            if avg_char_width <= 0: avg_char_width = 1 
            approx_chars_per_line = int(area_width_pixels / avg_char_width)
            if approx_chars_per_line <= 0: approx_chars_per_line = 1

            paragraphs = description_text.split('\n') 
            wrapped_lines = []
            for paragraph in paragraphs:
                if not paragraph.strip(): 
                    wrapped_lines.append("")
                else:
                    wrapped_lines.extend(textwrap.wrap(paragraph, width=approx_chars_per_line,
                                                       replace_whitespace=False, drop_whitespace=False,
                                                       break_long_words=True, break_on_hyphens=True))
            self.current_scrollable_lines = wrapped_lines
            
            title_height = TEXT_AREA_LINE_HEIGHT * 1.5 
            description_lines_height = len(self.current_scrollable_lines) * TEXT_AREA_LINE_HEIGHT
            self.current_content_height = title_height + description_lines_height
        else:
            self.current_content_height = 0

        # Add a small padding to the total content height to ensure the last item can be fully scrolled into view.
        self.current_content_height -= TEXT_AREA_LINE_HEIGHT * 2 
        print(f"DEBUG Grimoire Scroll: Prepared Content Height = {self.current_content_height:.2f}, Viewport Height = {self.scrollable_rect_on_screen[3]:.2f}")


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

        # Load inventory background texture
        self.inventory_background_texture = None
        try:
            self.inventory_background_texture = arcade.load_texture(INVENTORY_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: Inventory background image '{INVENTORY_BACKGROUND_IMAGE}' not found.")

        self.load_current_area_art()

        self.current_menu_options = []
        # Initial population of options will happen in on_show_view
        # because the world needs to initialize its state before options are reliable.

        # Display mode for the main game area
        self.display_mode = "welcome_screen" # Start with a welcome screen
        self.log_messages_to_display = [] # List to hold messages retrieved from world.message_log

        # For scrollable text (only for text-based views initially)
        self.scroll_offset_y = 0.0
        self.current_scrollable_lines = []
        self.current_view_content_height = 0.0 # Will store total height of current view's content
        self.scrollable_text_rect_on_screen = None

        # For "Check Bags" functionality
        self.pre_bags_view_mode = None
        self.pre_bags_menu_type = None

        # For item icons
        self.item_icon_textures = {} # Cache for loaded item icon textures
        self.default_item_icon_texture = None
        self.inventory_item_clickable_sprites = arcade.SpriteList() # For detecting clicks on icons
        self.selected_inventory_item = None # Holds the Item object selected by clicking its icon
        self.selected_item_source = None # Holds the source of the selected item (e.g., 'carried', 'strongbox')

        self._load_default_item_icon()

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
            self.game_area_background = self.placeholder_texture
            if self.game_area_background is None:
                print("Critical: No specific area art or placeholder art found. Using solid color fallback.")


    def _load_default_item_icon(self):
        """Loads the default item icon texture."""
        try:
            default_icon_path = os.path.join(ITEM_ICON_ART_PATH, "ui", "default_icon.png")
            self.default_item_icon_texture = arcade.load_texture(default_icon_path)
            print(f"Successfully loaded default item icon from: {default_icon_path}")
        except FileNotFoundError:
            print(f"ERROR: Default item icon 'default_icon.png' not found in {os.path.join(ITEM_ICON_ART_PATH, 'ui')}")
            self.default_item_icon_texture = None

    def update_menu_options(self, menu_type="main"):
        self.active_menu_type = menu_type 
        self.menu_action_buttons.clear() 

        if menu_type == "main":
            if self.world.current_area.name == self.world.camp:
                options_text = ["Prepare", "Travel", "Rest", "Save & Quit"]  
            else: 
                options_text = ["Fight", "Travel", "Check Bags", "Rest",  "Save & Quit"]

            self.current_menu_options = options_text

        elif menu_type == "travel":
            connections = self.world.available_travel_destinations 
            options_text = [f"{i+1}. {conn}" for i, conn in enumerate(connections)]
            options_text.append(f"{len(connections) + 1}. Stay") 
            self.current_menu_options = options_text
        elif menu_type == "player_combat_turn": 
            options_text = ["Attack", "Flee", "Check Bags"] 
            self.current_menu_options = options_text
        elif menu_type == "loot_decision_menu": 
            options_text = []
            if self.world.pending_loot_item:
                item_name = self.world.pending_loot_item.name
                options_text.append(f"Leave {item_name}")
                if self.world.player.inventory.can_carry_item(self.world.pending_loot_item):
                    options_text.insert(0, f"Take {item_name}") 
                else:
                    options_text.insert(0, "Drop Item to Take")
            self.current_menu_options = options_text
        elif menu_type == "welcome_menu": 
            options_text = ["Begin Game"]
            self.current_menu_options = options_text
        elif menu_type == "inventory_management": 
            # This is the "Prepare" menu when at camp
            options_text = ["Grimoire", "Back"] # Added Grimoire here
            self.current_menu_options = options_text
        elif menu_type == "view_bags_menu": 
            options_text = ["Back"]
            self.current_menu_options = options_text
        elif menu_type == "select_item_to_equip_menu":
            options_text = [f"{i+1}. {item_info['item'].name} ({item_info['item'].type}) - from {item_info['source']}" 
                            for i, item_info in enumerate(self.world.available_items_to_equip)]
            options_text.append("Back")
            self.current_menu_options = options_text
        elif menu_type == "defeat_acknowledged_menu": 
            options_text = ["Get Up"]
            self.current_menu_options = options_text
        elif menu_type == "rest_screen_menu":
            options_text = ["Get Up"]
            self.current_menu_options = options_text
        elif menu_type == "item_details_menu": 
            options_text = []
            if self.selected_inventory_item and self.selected_inventory_item.type in EQUIPABLE_TYPES:
                options_text.append("Equip")
            if self.selected_inventory_item and self.selected_item_source and \
               not self.selected_item_source.startswith("equipped_"):
                options_text.append("Drop Item") 
            options_text.append("Back to Inventory")
            self.current_menu_options = options_text
        elif menu_type == "select_item_to_drop_for_loot_menu": 
            options_text = ["Cancel Drop"]
            self.current_menu_options = options_text
        
        menu_content_area_top_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        actions_title_y = menu_content_area_top_y - TOP_PADDING
        first_button_center_y = actions_title_y - MENU_ACTIONS_TITLE_FONT_SIZE - MENU_PADDING_BELOW_TITLE - (MENU_BUTTON_HEIGHT / 2)
        button_center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2
        for i, raw_option_text in enumerate(self.current_menu_options):
            display_text = raw_option_text
            action_command = raw_option_text 
            if ". " in raw_option_text:
                parts = raw_option_text.split(". ", 1)
                if len(parts) > 1 and parts[0].isdigit():
                    prefix = raw_option_text.split(". ", 1)[0]
                    int(prefix) 
                    display_text = raw_option_text.split(". ", 1)[1]
                    action_command = display_text 

            if self.menu_button_texture:
                button_sprite = arcade.Sprite(texture=self.menu_button_texture)
                button_sprite.width = MENU_BUTTON_TARGET_WIDTH
                button_sprite.height = MENU_BUTTON_HEIGHT
            else:
                button_sprite = arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_SLATE_BLUE)
            
            button_sprite.center_x = button_center_x
            button_sprite.center_y = first_button_center_y - i * (MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING)
            button_sprite.properties['display_text'] = display_text
            button_sprite.properties['action_command'] = action_command 
            self.menu_action_buttons.append(button_sprite)

    def _prepare_scrollable_text(self, full_text_content, font_size_for_metric, area_width_pixels):
        self.current_scrollable_lines.clear()
        self.scroll_offset_y = 0.0  

        if not full_text_content:
            self.current_view_content_height = 0.0 # Ensure height is zeroed if no content
            return

        avg_char_width = font_size_for_metric * 0.65 
        if avg_char_width <= 0:
            approx_chars_per_line = 80 
        else:
            approx_chars_per_line = int(area_width_pixels / avg_char_width)
        
        if approx_chars_per_line <= 0: 
            approx_chars_per_line = 1

        paragraphs = full_text_content.split('\n')
        wrapped_lines = []
        for paragraph in paragraphs:
            if not paragraph.strip() and paragraph != "": 
                wrapped_lines.append("") 
            elif not paragraph.strip() and paragraph == "": 
                 wrapped_lines.append("")
            else:
                wrapped_lines.extend(textwrap.wrap(paragraph, width=approx_chars_per_line, 
                                                   replace_whitespace=False, drop_whitespace=False,
                                                   break_long_words=True, break_on_hyphens=True))
        self.current_scrollable_lines = wrapped_lines
        self.current_view_content_height = len(self.current_scrollable_lines) * TEXT_AREA_LINE_HEIGHT

    def _prepare_scrollable_text_for_current_mode(self):
        consistent_text_area_width = GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5 

        if self.display_mode == "welcome_screen":
            self._prepare_scrollable_text("\n".join(self.log_messages_to_display), TEXT_AREA_FONT_SIZE, consistent_text_area_width)
        elif self.display_mode == "area_description":
            self._prepare_scrollable_text("\n".join(self.log_messages_to_display), TEXT_AREA_FONT_SIZE, consistent_text_area_width)
        elif self.display_mode == "combat_log":
            self._prepare_scrollable_text("\n".join(self.log_messages_to_display), LOG_AREA_FONT_SIZE, consistent_text_area_width)
        elif self.display_mode in ["inventory_management", "view_bags", "select_item_to_equip_display", 
                                   "loot_decision_display", "select_item_to_drop_for_loot_display"] and \
             self.display_mode not in ["select_item_to_equip_display"]: # Exclude text-based equip list
            self.current_scrollable_lines.clear() 
            self.scroll_offset_y = 0.0 # Reset scroll for these views as they are not text-scrollable yet
            # Calculate height for icon views
            self.current_view_content_height = self._calculate_icon_view_content_height(self.display_mode)
            pass 
        elif self.display_mode == "item_details_display":
            self.current_scrollable_lines.clear()
            self.scroll_offset_y = 0.0
            if self.selected_inventory_item:
                details_text = f"--- {self.selected_inventory_item.name} ---\n"
                details_text += f"Type: {self.selected_inventory_item.type}\n\n"
                details_text += f"Description:\n{self.selected_inventory_item.description}"
                self._prepare_scrollable_text(details_text, TEXT_AREA_FONT_SIZE, consistent_text_area_width)
            # current_view_content_height is set by _prepare_scrollable_text
        else: # Fallback for any unhandled display modes
            self.current_scrollable_lines.clear()
            self.scroll_offset_y = 0.0
            self.current_view_content_height = 0.0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.update_menu_options("welcome_menu") 
        self.log_messages_to_display = self.world.get_messages() 
        self._prepare_scrollable_text_for_current_mode() 

    def _calculate_icon_view_content_height(self, display_mode_to_calculate):
        """
        Calculates the total potential vertical height of icon-based views.
        """
        height = 0.0
        item_row_h = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
        section_title_h = TEXT_AREA_LINE_HEIGHT + ITEM_SECTION_SPACING / 2
        empty_line_h = TEXT_AREA_LINE_HEIGHT # Height for an "(Empty)" line or similar single text line
        capacity_line_h = TEXT_AREA_LINE_HEIGHT

        if display_mode_to_calculate == "inventory_management":
            height += section_title_h # "== Equipped Items =="
            num_equipped = 0
            if self.player.inventory.equipped_items.get('Held'): num_equipped += 1
            if self.player.inventory.equipped_items.get('Body'): num_equipped += 1
            num_equipped += len(self.player.inventory.equipped_items.get('Trinkets', []))
            height += num_equipped * item_row_h if num_equipped > 0 else empty_line_h
            height += ITEM_SECTION_SPACING

            height += section_title_h # "== Carried Items (Bags) =="
            height += len(set(item.name for item in self.player.inventory.stored_items)) * item_row_h if self.player.inventory.stored_items else empty_line_h
            height += ITEM_SECTION_SPACING

            height += section_title_h # "== Strongbox (Camp) =="
            height += len(set(item.name for item in self.player.inventory.strongbox_items)) * item_row_h if self.player.inventory.strongbox_items else empty_line_h
            height += ITEM_SECTION_SPACING

        elif display_mode_to_calculate == "view_bags":
            height += section_title_h # "--- Equipment ---" title
            height += section_title_h # "== Equipped Items ==" title
            num_equipped = 0
            if self.player.inventory.equipped_items.get('Held'): num_equipped += 1
            if self.player.inventory.equipped_items.get('Body'): num_equipped += 1
            num_equipped += len(self.player.inventory.equipped_items.get('Trinkets', []))
            height += num_equipped * item_row_h if num_equipped > 0 else empty_line_h
            height += ITEM_SECTION_SPACING # Spacing after equipped section

            height += section_title_h # "--- Bag Pockets & Capacities ---" title
            for item_type_key, _ in self.player.inventory.carry_capacities.items():
                height += TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2 # Pocket title height
                items_in_this_pocket = [item for item in self.player.inventory.stored_items if item.type == item_type_key]
                height += len(set(i.name for i in items_in_this_pocket)) * item_row_h if items_in_this_pocket else empty_line_h
                height += capacity_line_h # Capacity text height
                height += ITEM_SECTION_SPACING # Spacing after each pocket section

        elif display_mode_to_calculate == "loot_decision_display":
            height += section_title_h # "--- Loot Found! ---"
            if self.world.pending_loot_item:
                height += item_row_h # Pending item
                if self.world.pending_loot_item.description:
                     desc_lines = textwrap.wrap(f"Desc: {self.world.pending_loot_item.description}", width=int((GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5) / (TEXT_AREA_FONT_SIZE * 0.6)))
                     height += len(desc_lines) * TEXT_AREA_LINE_HEIGHT
            else:
                height += empty_line_h
            height += ITEM_SECTION_SPACING
            # Add height for "Your Equipment & Pockets" section (mimicking view_bags)
            height += section_title_h # "--- Your Equipment & Pockets ---" title
            # (This part is a simplified estimation for brevity, a full loop like in view_bags would be more accurate)
            height += section_title_h + (item_row_h * 2) + ITEM_SECTION_SPACING # Approx for equipped
            for _ in self.player.inventory.carry_capacities.items(): # Pockets
                height += (TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2) + item_row_h + capacity_line_h + ITEM_SECTION_SPACING

        elif display_mode_to_calculate == "select_item_to_drop_for_loot_display":
            height += section_title_h # "--- Drop Item to Take ---" title
            height += item_row_h # Pending item display
            height += ITEM_ICON_VERTICAL_SPACING # Extra spacing
            height += TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2 # "Click Item to Drop from..." title
            if self.world.pending_loot_item:
                pending_item_type = self.world.pending_loot_item.type
                items_in_relevant_pocket = [item for item in self.player.inventory.stored_items if item.type == pending_item_type]
                height += len(set(i.name for i in items_in_relevant_pocket)) * item_row_h if items_in_relevant_pocket else empty_line_h
            else: # Should not happen if pending_loot_item is None here
                height += empty_line_h
            height += capacity_line_h # Capacity text
            height += ITEM_SECTION_SPACING

        return height + TOP_PADDING # Add a small buffer at the end

    def _get_item_icon_texture(self, item):
        if not item:
            return self.default_item_icon_texture
        cache_key = f"{item.icon_subfolder}_{item.icon_filename}"
        if cache_key in self.item_icon_textures:
            return self.item_icon_textures[cache_key]
        icon_path = "Unknown (icon data missing)" 
        if item.icon_filename and item.icon_subfolder:
            try:
                icon_path = os.path.join(ITEM_ICON_ART_PATH, item.icon_subfolder, item.icon_filename)
                texture = arcade.load_texture(icon_path)
                self.item_icon_textures[cache_key] = texture
                return texture
            except FileNotFoundError:
                print(f"Warning: Icon not found for {item.name} at {icon_path}. Using default.")
            except Exception as e: 
                print(f"Error loading icon for {item.name} at {icon_path}: {e}. Using default.")
        return self.default_item_icon_texture

    def _draw_item_section_in_panel(self, title, items_list_or_dict, current_draw_y, text_color, is_dict_of_items=False, make_clickable=False, source_override=None, view_boundaries=None):
        # Clipping for section title
        title_h = TEXT_AREA_LINE_HEIGHT + ITEM_SECTION_SPACING / 2
        if view_boundaries and current_draw_y > view_boundaries[1] and current_draw_y - title_h < view_boundaries[1] + view_boundaries[3]:
            arcade.draw_text(title, LEFT_PADDING, current_draw_y, text_color, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
        current_draw_y -= title_h # Decrement y even if not drawn to maintain layout for height calculation

        items_with_source_info = [] 
        if is_dict_of_items: 
            for slot, item_obj in items_list_or_dict.items():
                if isinstance(item_obj, list): 
                    for trinket in item_obj:
                        if trinket: items_with_source_info.append({'item': trinket, 'source': f'equipped_{slot.lower()}', 'count': 1})
                elif item_obj: 
                    items_with_source_info.append({'item': item_obj, 'source': f'equipped_{slot.lower()}', 'count': 1})
        else: 
            current_source_name = source_override 
            if current_source_name is None: 
                if items_list_or_dict is self.player.inventory.stored_items:
                    current_source_name = "carried"
                elif items_list_or_dict is self.player.inventory.strongbox_items:
                    current_source_name = "strongbox"
                else:
                    current_source_name = "unknown_list_source"
            item_name_counts = Counter(item.name for item in items_list_or_dict)
            processed_item_names = set()
            for item_obj in items_list_or_dict:
                if item_obj.name not in processed_item_names:
                    items_with_source_info.append({
                        'item': item_obj, 
                        'source': current_source_name, 
                        'count': item_name_counts[item_obj.name]
                    })
                    processed_item_names.add(item_obj.name)
        
        empty_line_h = TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING
        if not items_with_source_info:
            if view_boundaries and current_draw_y > view_boundaries[1] and current_draw_y - empty_line_h < view_boundaries[1] + view_boundaries[3]:
                arcade.draw_text("(Empty)", LEFT_PADDING + ITEM_ICON_DRAW_SIZE[0] + 10, current_draw_y, text_color, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
            current_draw_y -= empty_line_h
        else:
            for item_info in items_with_source_info:
                item = item_info['item']
                count = item_info['count']
                source = item_info['source']
                item_row_h = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)

                if make_clickable:
                    clickable_sprite = arcade.SpriteSolidColor(ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], (0,0,0,0)) 
                    clickable_sprite.center_x = LEFT_PADDING + ITEM_ICON_DRAW_SIZE[0] / 2
                    clickable_sprite.center_y = current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2 # Y is relative to scrolled current_draw_y
                    clickable_sprite.properties['item_object'] = item
                    clickable_sprite.properties['item_source'] = source
                    self.inventory_item_clickable_sprites.append(clickable_sprite)
                
                if view_boundaries and current_draw_y > view_boundaries[1] and current_draw_y - item_row_h < view_boundaries[1] + view_boundaries[3]:
                    icon_texture = self._get_item_icon_texture(item)
                    if icon_texture:
                        arcade.draw_texture_rectangle(LEFT_PADDING + ITEM_ICON_DRAW_SIZE[0] / 2, 
                                                      current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2, 
                                                      ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], 
                                                      icon_texture)
                    item_display_name = f"{item.name} ({item.type})"
                    if count > 1:
                        item_display_name += f" x{count}"
                    text_draw_y = current_draw_y - (ITEM_ICON_DRAW_SIZE[1] / 2) + (TEXT_AREA_LINE_HEIGHT / 2) - 4
                    arcade.draw_text(item_display_name, LEFT_PADDING + ITEM_TEXT_OFFSET_X, text_draw_y, 
                                      text_color, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                current_draw_y -= item_row_h
        current_draw_y -= ITEM_SECTION_SPACING
        return current_draw_y

    def on_draw(self):
        self.clear()
        # --- Top Banner Drawing (Remains the same) ---
        if self.top_banner_texture:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                self.top_banner_texture
            )
        else: 
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2,
                SCREEN_WIDTH,
                PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_GRAY
            )
        player_info_y = SCREEN_HEIGHT - TOP_PADDING - (PLAYER_INFO_BANNER_HEIGHT / 2) + 20
        text_color = arcade.color.WHITE
        font_size = 12
        name_level_str = f"Name: {self.player.name} | Level: {self.player.level}"
        arcade.draw_text(
            name_level_str,
            LEFT_PADDING,
            player_info_y,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
        )
        self.player.update_stats() 
        arcade.draw_text(
            f"HP: {self.player.current_health}/{self.player.max_health} | Atk: {self.player.attack + self.player.attack_mod} | Def: {self.player.defense + self.player.defense_mod} | Spd: {self.player.speed + self.player.speed_mod}",
            LEFT_PADDING,
            player_info_y - 25,
            text_color,
            font_size=font_size,
            anchor_x="left",
            anchor_y="center", 
            width=int(GAME_AREA_WIDTH - 2 * LEFT_PADDING),
            align="left"
        )
        time_text_color = arcade.color.RED if self.world.day_cycle.is_night() else text_color
        name_level_text_obj = arcade.Text(name_level_str, 0, 0, text_color, font_size)
        current_x_offset = LEFT_PADDING + name_level_text_obj.content_width
        spacing_between_banner_items = 20 
        wealth_text_str = f"Wealth: {self.player.inventory.income}"
        wealth_text_x_start = current_x_offset + spacing_between_banner_items
        arcade.draw_text(
            wealth_text_str,
            wealth_text_x_start,
            player_info_y, 
            text_color, 
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
        )
        wealth_text_obj_for_measure = arcade.Text(wealth_text_str, 0, 0, text_color, font_size)
        current_x_offset = wealth_text_x_start + wealth_text_obj_for_measure.content_width
        hour_text_str = f" | Hour: {self.world.day_cycle.hour}"
        hour_text_x_start = current_x_offset + spacing_between_banner_items / 2 
        arcade.draw_text(
            hour_text_str,
            hour_text_x_start,
            player_info_y,
            time_text_color, 
            font_size=font_size,
            anchor_x="left",
            anchor_y="center"
        )
        game_area_y_center = (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2
        background_to_draw = self.game_area_background 
        if self.display_mode in ["inventory_management", "view_bags", "item_details_display"]:
            if self.inventory_background_texture:
                background_to_draw = self.inventory_background_texture
            else:
                arcade.draw_rectangle_filled(
                    GAME_AREA_WIDTH / 2,
                    game_area_y_center,
                    GAME_AREA_WIDTH,
                    SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                    arcade.color.DARK_SLATE_GRAY 
                )
                background_to_draw = None 
        if background_to_draw: 
            arcade.draw_texture_rectangle(
                GAME_AREA_WIDTH / 2,
                game_area_y_center,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                background_to_draw,
            )
        elif not self.display_mode in ["inventory_management", "view_bags", "item_details_display"]: 
            arcade.draw_rectangle_filled(
                GAME_AREA_WIDTH / 2,
                game_area_y_center,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_OLIVE_GREEN 
            )
        description_x = LEFT_PADDING
        description_y = game_area_y_center + (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2 - TOP_PADDING
        description_width = GAME_AREA_WIDTH - (2 * LEFT_PADDING) - 5 
        bg_rect_center_x = GAME_AREA_WIDTH / 2
        bg_rect_width = GAME_AREA_WIDTH 
        text_box_height_for_log = 150 
        bg_rect_height = text_box_height_for_log + (2 * TEXT_AREA_LINE_HEIGHT) 
        bg_rect_center_y = description_y - (bg_rect_height / 2) # Default for text log box
        inventory_views_for_overlay = [ # This list is used to determine if the full-panel background overlay is drawn
            "inventory_management", "view_bags", 
            "loot_decision_display", "select_item_to_drop_for_loot_display",
            "item_details_display", "select_item_to_equip_display" 
        ]
        if self.display_mode in inventory_views_for_overlay: # Corrected condition
            bg_rect_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT # Height of the main game panel
            bg_rect_center_y = (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2 # Center of the main game panel
        arcade.draw_rectangle_filled( # This draws the semi-transparent background
            bg_rect_center_x,
            bg_rect_center_y, 
            bg_rect_width,
            bg_rect_height, 
            (0, 0, 0, 180) 
        )       
        _scroll_area_top_y_for_lines = description_y  
        _scroll_area_height_for_lines = text_box_height_for_log 
        _line_font_size = TEXT_AREA_FONT_SIZE
        _text_color_for_mode = arcade.color.LIGHT_GRAY 
        if self.display_mode == "welcome_screen":
            _text_color_for_mode = arcade.color.WHITE 
        elif self.display_mode == "area_description":
            location_name_text = f"Location: {self.world.current_area.name}"
            name_font_size = 14 
            spacing_after_name = 5 
            arcade.draw_text(
                location_name_text,
                description_x,
                description_y, 
                arcade.color.LIGHT_GRAY,
                font_size=name_font_size,
                width=description_width,
                align="left",
                anchor_x="left",
                anchor_y="top",
                bold=True 
            )
            _scroll_area_top_y_for_lines = description_y - (name_font_size + spacing_after_name)
            _scroll_area_height_for_lines = text_box_height_for_log - (name_font_size + spacing_after_name) 
            _line_font_size = TEXT_AREA_FONT_SIZE 
            _text_color_for_mode = arcade.color.LIGHT_GRAY 
        elif self.display_mode == "combat_log":
            _line_font_size = LOG_AREA_FONT_SIZE
            _text_color_for_mode = arcade.color.WHITE
        elif self.display_mode in ["inventory_management", "view_bags", "select_item_to_equip_display"]:
            _line_font_size = TEXT_AREA_FONT_SIZE 
            _text_color_for_mode = arcade.color.WHITE 
        
        # Define scrollable_text_rect_on_screen based on display_mode
        icon_full_panel_views = ["inventory_management", "view_bags", "loot_decision_display", "select_item_to_drop_for_loot_display"]
        if self.display_mode in icon_full_panel_views:
            self.scrollable_text_rect_on_screen = (
                0,  # left_x of the game panel
                0,  # bottom_y of the game panel (bottom of the screen)
                GAME_AREA_WIDTH,  # width of the game panel
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT # height of the game panel
            )
            # For icon views, content drawing starts from the top of the game panel area (below banner)
            _scroll_area_top_y_for_lines = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - ICON_PANEL_TOP_MARGIN 
        else: # Text-based views
            self.scrollable_text_rect_on_screen = (
                description_x,  
                _scroll_area_top_y_for_lines - _scroll_area_height_for_lines,  
                description_width,  
                _scroll_area_height_for_lines  
            )
            # _scroll_area_top_y_for_lines is already set correctly for text views from earlier logic

        # --- Set viewport for scrollable content ---
        # Rolling back viewport changes. Clipping will rely on drawing logic within bounds.
        
        # --- Text-based views drawing loop ---
        if self.display_mode in ["welcome_screen", "area_description", "combat_log", "item_details_display", "select_item_to_equip_display"]: # Ensure all text views are covered
            if self.current_scrollable_lines:
                first_visible_line_idx = int(self.scroll_offset_y / TEXT_AREA_LINE_HEIGHT)
                lines_in_view = int(self.scrollable_text_rect_on_screen[3] / TEXT_AREA_LINE_HEIGHT) if self.scrollable_text_rect_on_screen[3] > 0 else 0
                for i in range(len(self.current_scrollable_lines)):
                    if i < first_visible_line_idx:
                        continue
                    if i > first_visible_line_idx + lines_in_view + 1:  
                        break
                    line_text_content = self.current_scrollable_lines[i]
                    line_y_offset_from_content_top = i * TEXT_AREA_LINE_HEIGHT
                    draw_y_on_screen = _scroll_area_top_y_for_lines - (line_y_offset_from_content_top - self.scroll_offset_y)
                    # The old per-element clipping check can be removed due to set_viewport, but keeping it doesn't hurt.
                    # For simplicity with set_viewport, we can remove the complex condition here.
                    # We just need to ensure we don't try to draw excessively off-screen for performance.
                    if abs(draw_y_on_screen - (_scroll_area_top_y_for_lines - self.scrollable_text_rect_on_screen[3]/2)) < self.scrollable_text_rect_on_screen[3] * 1.5: # Draw if roughly near viewport
                        arcade.draw_text(
                            line_text_content,
                            description_x, 
                            draw_y_on_screen,
                            _text_color_for_mode,
                            font_size=_line_font_size,
                            width=description_width, 
                            anchor_x="left",
                            anchor_y="top"
                        )
        # --- Icon-based views drawing ---
        elif self.display_mode == "inventory_management":
            current_draw_y = _scroll_area_top_y_for_lines + self.scroll_offset_y # Changed to +
            self.inventory_item_clickable_sprites.clear() 
            current_draw_y = self._draw_item_section_in_panel("== Equipped Items ==", self.player.inventory.equipped_items, current_draw_y, _text_color_for_mode, is_dict_of_items=True, make_clickable=True, view_boundaries=self.scrollable_text_rect_on_screen)
            current_draw_y = self._draw_item_section_in_panel("== Carried Items (Bags) ==", self.player.inventory.stored_items, current_draw_y, _text_color_for_mode, make_clickable=True, view_boundaries=self.scrollable_text_rect_on_screen)
            current_draw_y = self._draw_item_section_in_panel("== Strongbox (Camp) ==", self.player.inventory.strongbox_items, current_draw_y, _text_color_for_mode, make_clickable=True, view_boundaries=self.scrollable_text_rect_on_screen)

        elif self.display_mode == "view_bags":
            current_draw_y = _scroll_area_top_y_for_lines + self.scroll_offset_y # Changed to +
            self.inventory_item_clickable_sprites.clear() 
            # Draw "--- Equipment ---" title with clipping
            title_h = TEXT_AREA_LINE_HEIGHT + ITEM_SECTION_SPACING / 2
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text("--- Equipment ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
            current_draw_y -= title_h
            current_draw_y = self._draw_item_section_in_panel("== Equipped Items ==", self.player.inventory.equipped_items, current_draw_y, _text_color_for_mode, is_dict_of_items=True, make_clickable=False, view_boundaries=self.scrollable_text_rect_on_screen)
            current_draw_y -= ITEM_SECTION_SPACING 
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text("--- Bag Pockets & Capacities ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
            current_draw_y -= title_h
            pocket_names_map = {
                'crafting': "Main Bag (Crafting)",
                'trinket': "Front Pouch (Trinkets)",
                'weapon': "Tied On the Side (Weapons)",
                'wealth': "Side Pouch (Wealth)",
                'armor': "Strapped Below (Armor)" 
            }
            for item_type_key, max_capacity in self.player.inventory.carry_capacities.items():
                pocket_display_name = pocket_names_map.get(item_type_key, f"{item_type_key.capitalize()} Pocket") 
                pocket_title_h = TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - pocket_title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(f"== {pocket_display_name} ==", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 1, bold=True, anchor_y="top")
                current_draw_y -= pocket_title_h
                items_in_this_pocket = [item for item in self.player.inventory.stored_items if item.type == item_type_key]
                empty_line_h = TEXT_AREA_LINE_HEIGHT
                if not items_in_this_pocket:
                    if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - empty_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                        arcade.draw_text("(Empty)", description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                    current_draw_y -= empty_line_h
                else:
                    item_name_counts = Counter(item.name for item in items_in_this_pocket)
                    processed_item_names = set()
                    for item_obj in items_in_this_pocket:
                        if item_obj.name not in processed_item_names:
                            item_row_h = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
                            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - item_row_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                                icon_texture = self._get_item_icon_texture(item_obj)
                                if icon_texture:
                                    arcade.draw_texture_rectangle(description_x + ITEM_ICON_DRAW_SIZE[0] / 2, current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2, ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], icon_texture)
                                display_name = f"{item_obj.name} ({item_obj.type})"
                                count = item_name_counts[item_obj.name]
                                if count > 1:
                                    display_name += f" x{count}"
                                arcade.draw_text(display_name, description_x + ITEM_TEXT_OFFSET_X, current_draw_y - (ITEM_ICON_DRAW_SIZE[1] / 2) + (TEXT_AREA_LINE_HEIGHT / 2) - 4, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                            current_draw_y -= item_row_h
                            processed_item_names.add(item_obj.name)
                capacity_text = f"Capacity: {len(items_in_this_pocket)} / {max_capacity}"
                capacity_line_h = TEXT_AREA_LINE_HEIGHT
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - capacity_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(capacity_text, description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE -1, anchor_y="top")
                current_draw_y -= (capacity_line_h + ITEM_SECTION_SPACING)

        elif self.display_mode == "loot_decision_display":
            current_draw_y = _scroll_area_top_y_for_lines + self.scroll_offset_y # Changed to +
            self.inventory_item_clickable_sprites.clear() 
            title_h = TEXT_AREA_LINE_HEIGHT + ITEM_SECTION_SPACING / 2
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text("--- Loot Found! ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
            current_draw_y -= title_h
            pending_item = self.world.pending_loot_item
            item_row_h = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
            if pending_item:
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - item_row_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    icon_texture = self._get_item_icon_texture(pending_item)
                    if icon_texture:
                        arcade.draw_texture_rectangle(description_x + ITEM_ICON_DRAW_SIZE[0] / 2, current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2, ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], icon_texture)
                    item_display_name = f"{pending_item.name} ({pending_item.type})"
                    text_draw_y = current_draw_y - (ITEM_ICON_DRAW_SIZE[1] / 2) + (TEXT_AREA_LINE_HEIGHT / 2) - 4
                    arcade.draw_text(item_display_name, description_x + ITEM_TEXT_OFFSET_X, text_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                current_draw_y -= item_row_h
                if pending_item.description:
                    desc_lines = textwrap.wrap(f"Desc: {pending_item.description}", width=int(description_width / (TEXT_AREA_FONT_SIZE * 0.6)))
                    for line in desc_lines:
                        if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - TEXT_AREA_LINE_HEIGHT < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                            arcade.draw_text(line, description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE -2, anchor_y="top")
                        current_draw_y -= TEXT_AREA_LINE_HEIGHT
            current_draw_y -= ITEM_SECTION_SPACING
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text("--- Your Equipment & Pockets ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
            current_draw_y -= title_h
            current_draw_y = self._draw_item_section_in_panel("== Equipped Items ==", self.player.inventory.equipped_items, current_draw_y, _text_color_for_mode, is_dict_of_items=True, make_clickable=False, view_boundaries=self.scrollable_text_rect_on_screen)
            pocket_names_map = {
                'crafting': "Main Bag (Crafting)",
                'trinket': "Front Pouch (Trinkets)",
                'weapon': "Tied On the Side (Weapons)",
                'wealth': "Side Pouch (Wealth)",
                'armor': "Strapped Below (Armor)"
            }
            for item_type_key, max_capacity in self.player.inventory.carry_capacities.items():
                pocket_display_name = pocket_names_map.get(item_type_key, f"{item_type_key.capitalize()} Pocket")
                pocket_title_h = TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - pocket_title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(f"== {pocket_display_name} ==", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 1, bold=True, anchor_y="top")
                current_draw_y -= pocket_title_h
                items_in_this_pocket = [item for item in self.player.inventory.stored_items if item.type == item_type_key]
                empty_line_h = TEXT_AREA_LINE_HEIGHT
                if not items_in_this_pocket:
                    if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - empty_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                        arcade.draw_text("(Empty)", description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                    current_draw_y -= empty_line_h
                else:
                    temp_y = current_draw_y
                    item_name_counts = Counter(item.name for item in items_in_this_pocket)
                    processed_item_names = set()
                    for item_obj in items_in_this_pocket:
                        if item_obj.name not in processed_item_names:
                            item_row_h_inner = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
                            if temp_y > self.scrollable_text_rect_on_screen[1] and temp_y - item_row_h_inner < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                                icon_texture = self._get_item_icon_texture(item_obj)
                                if icon_texture:
                                    arcade.draw_texture_rectangle(description_x + ITEM_ICON_DRAW_SIZE[0] / 2, temp_y - ITEM_ICON_DRAW_SIZE[1] / 2, ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], icon_texture)
                                display_name = f"{item_obj.name} ({item_obj.type})"
                                count = item_name_counts[item_obj.name]
                                if count > 1: display_name += f" x{count}"
                                arcade.draw_text(display_name, description_x + ITEM_TEXT_OFFSET_X, temp_y - (ITEM_ICON_DRAW_SIZE[1] / 2) + (TEXT_AREA_LINE_HEIGHT / 2) - 4, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                            temp_y -= item_row_h_inner
                            processed_item_names.add(item_obj.name)
                    current_draw_y = temp_y 
                capacity_text = f"Capacity: {len(items_in_this_pocket)} / {max_capacity}"
                capacity_line_h = TEXT_AREA_LINE_HEIGHT
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - capacity_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(capacity_text, description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE -1, anchor_y="top")
                current_draw_y -= (capacity_line_h + ITEM_SECTION_SPACING)

        elif self.display_mode == "select_item_to_drop_for_loot_display":
            current_draw_y = _scroll_area_top_y_for_lines + self.scroll_offset_y # Changed to +
            self.inventory_item_clickable_sprites.clear()
            pending_item = self.world.pending_loot_item
            if not pending_item:
                arcade.draw_text("Error: Loot decision cannot be processed (no item).",
                                 description_x, current_draw_y, arcade.color.RED,
                                 font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                return 
            title_h = TEXT_AREA_LINE_HEIGHT + ITEM_SECTION_SPACING / 2
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text("--- Drop Item to Take ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 2, bold=True, anchor_y="top")
            current_draw_y -= title_h
            item_row_h = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
            if pending_item:
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - item_row_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(f"New Item: {pending_item.name} ({pending_item.type})", description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                    icon_texture = self._get_item_icon_texture(pending_item)
                    if icon_texture:
                        arcade.draw_texture_rectangle(description_x + ITEM_ICON_DRAW_SIZE[0] / 2, current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2, ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], icon_texture)
            current_draw_y -= item_row_h + ITEM_ICON_VERTICAL_SPACING # Extra spacing
            pending_item_type = pending_item.type
            pocket_names_map = {
                'crafting': "Main Bag (Crafting)",
                'trinket': "Front Pouch (Trinkets)",
                'weapon': "Tied On the Side (Weapons)",
                'wealth': "Side Pouch (Wealth)",
                'armor': "Strapped Below (Armor)"
            }
            relevant_pocket_name = pocket_names_map.get(pending_item_type, f"{pending_item_type.capitalize()} Pocket")
            max_capacity = self.player.inventory.carry_capacities.get(pending_item_type, 0)
            pocket_title_h = TEXT_AREA_LINE_HEIGHT + ITEM_ICON_VERTICAL_SPACING / 2
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - pocket_title_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text(f"--- Click Item to Drop from {relevant_pocket_name} ---", description_x, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE + 1, bold=True, anchor_y="top")
            current_draw_y -= pocket_title_h
            items_in_relevant_pocket = [item for item in self.player.inventory.stored_items if item.type == pending_item_type]
            empty_line_h = TEXT_AREA_LINE_HEIGHT
            if not items_in_relevant_pocket:
                if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - empty_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                    arcade.draw_text(f"({relevant_pocket_name} is empty)", description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                current_draw_y -= empty_line_h
            else:
                item_name_counts = Counter(item.name for item in items_in_relevant_pocket)
                processed_item_names = set()
                for item_obj in items_in_relevant_pocket:
                    if item_obj.name not in processed_item_names:
                        clickable_sprite = arcade.SpriteSolidColor(ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], (0,0,0,0)) 
                        clickable_sprite.center_x = description_x + ITEM_ICON_DRAW_SIZE[0] / 2
                        clickable_sprite.center_y = current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2 # Relative to scrolled Y
                        clickable_sprite.properties['item_object'] = item_obj
                        clickable_sprite.properties['item_source'] = "carried_for_loot_drop"
                        self.inventory_item_clickable_sprites.append(clickable_sprite)
                        item_row_h_inner = (max(ITEM_ICON_DRAW_SIZE[1], TEXT_AREA_LINE_HEIGHT) + ITEM_ICON_VERTICAL_SPACING)
                        if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - item_row_h_inner < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                            icon_texture = self._get_item_icon_texture(item_obj)
                            if icon_texture:
                                arcade.draw_texture_rectangle(description_x + ITEM_ICON_DRAW_SIZE[0] / 2, current_draw_y - ITEM_ICON_DRAW_SIZE[1] / 2, ITEM_ICON_DRAW_SIZE[0], ITEM_ICON_DRAW_SIZE[1], icon_texture)
                            display_name = f"{item_obj.name} ({item_obj.type})"
                            count = item_name_counts[item_obj.name]
                            if count > 1:
                                display_name += f" x{count}"
                            arcade.draw_text(display_name, description_x + ITEM_TEXT_OFFSET_X, current_draw_y - (ITEM_ICON_DRAW_SIZE[1] / 2) + (TEXT_AREA_LINE_HEIGHT / 2) - 4, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top")
                        current_draw_y -= item_row_h_inner
                        processed_item_names.add(item_obj.name)
            capacity_text = f"Capacity: {len(items_in_relevant_pocket)} / {max_capacity}"
            capacity_line_h = TEXT_AREA_LINE_HEIGHT
            if current_draw_y > self.scrollable_text_rect_on_screen[1] and current_draw_y - capacity_line_h < self.scrollable_text_rect_on_screen[1] + self.scrollable_text_rect_on_screen[3]:
                arcade.draw_text(capacity_text, description_x + ITEM_TEXT_OFFSET_X, current_draw_y, _text_color_for_mode, font_size=TEXT_AREA_FONT_SIZE -1, anchor_y="top")
            current_draw_y -= (capacity_line_h + ITEM_SECTION_SPACING)

        # --- Right Panel Drawing (Menu Buttons - Remains the same) ---
        # Rolling back viewport reset. Arcade's default viewport should be active here.
        # Ensure the window's default viewport is active for the right panel.
        arcade.get_window().use() # This should reset to the default camera and viewport

        # Now draw the right panel and its buttons
        # --- This block was moved back from on_update to on_draw ---
        if self.right_panel_background_texture:
            arcade.draw_texture_rectangle(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.right_panel_background_texture
            )
        else: 
            arcade.draw_rectangle_filled(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2, 
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY
            )
        arcade.draw_text(
            "Actions",
            RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - TOP_PADDING,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="top"
        )
        self.menu_action_buttons.draw()
        menu_item_font_size_default = 16
        min_font_size = 6 
        for button_sprite in self.menu_action_buttons:
            display_text = button_sprite.properties.get('display_text', "")
            current_font_size = menu_item_font_size_default
            button_text_max_width = button_sprite.width - (2 * MENU_BUTTON_TEXT_PADDING)
            initial_font_size_for_button = current_font_size 
            temp_text_obj = arcade.Text(
                display_text, 0, 0, 
                MENU_BUTTON_TEXT_COLOR,
                font_size=current_font_size
            )
            text_width = temp_text_obj.content_width 
            while text_width > button_text_max_width and current_font_size > min_font_size:
                current_font_size -= 1
                temp_text_obj = arcade.Text(
                    display_text, 0, 0, MENU_BUTTON_TEXT_COLOR,
                    font_size=current_font_size
                )
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
        print(f"Mouse pressed at ({x}, {y}) in GameView")
        if x > RIGHT_MENU_X_START:
            clicked_buttons = arcade.get_sprites_at_point((x, y), self.menu_action_buttons)
            if clicked_buttons:
                clicked_button = clicked_buttons[0] 
                command = clicked_button.properties.get('action_command', "")
                print(f"Clicked button: '{command}'")
                if command == "Begin Game" and self.active_menu_type == "welcome_menu":
                    self.log_messages_to_display.clear()
                    self.world.display_current_area() 
                    self.log_messages_to_display.extend(self.world.get_messages()) 
                    self.display_mode = "area_description"
                    self.update_menu_options("main")
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                if command == "Back" and self.display_mode == "inventory_management":
                    self.display_mode = "area_description"
                    self.update_menu_options("main")
                    self.log_messages_to_display.clear()
                    self.world.display_current_area() 
                    self.log_messages_to_display.extend(self.world.get_messages())
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                elif command == "Back" and self.active_menu_type == "select_item_to_equip_menu":
                    self.display_mode = "inventory_management"
                    self.update_menu_options("inventory_management")
                    self.log_messages_to_display.clear() 
                    self._prepare_scrollable_text_for_current_mode()
                    self.world.available_items_to_equip.clear() 
                    return 
                elif command == "Back to Inventory" and self.active_menu_type == "item_details_menu":
                    self.selected_inventory_item = None 
                    self.display_mode = "inventory_management" 
                    self.update_menu_options("inventory_management")
                    self.log_messages_to_display.clear()
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                elif command == "Cancel Drop" and self.active_menu_type == "select_item_to_drop_for_loot_menu":
                    self.display_mode = "loot_decision_display"
                    self.update_menu_options("loot_decision_menu")
                    self.log_messages_to_display.clear() 
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                elif command == "Equip" and self.active_menu_type == "item_details_menu":
                    if self.selected_inventory_item and self.selected_item_source:
                        success = self.player.equip_item_from_storage(
                            self.selected_inventory_item,
                            self.selected_item_source,
                            self.world.append_message 
                        )
                        self.selected_inventory_item = None
                        self.selected_item_source = None
                        self.display_mode = "inventory_management"
                        self.update_menu_options("inventory_management")
                        self.log_messages_to_display.clear() 
                        self.log_messages_to_display.extend(self.world.get_messages()) 
                        self._prepare_scrollable_text_for_current_mode() 
                        return 
                elif command == "Drop Item" and self.active_menu_type == "item_details_menu":
                    if self.selected_inventory_item and self.selected_item_source:
                        success = self.player.inventory.drop_item(
                            self.selected_inventory_item,
                            self.selected_item_source,
                            self.world.append_message 
                        )
                        self.selected_inventory_item = None
                        self.selected_item_source = None
                        self.display_mode = "inventory_management"
                        self.update_menu_options("inventory_management")
                        self.log_messages_to_display.clear()
                        self.log_messages_to_display.extend(self.world.get_messages()) 
                        self._prepare_scrollable_text_for_current_mode()
                        return 
                
                elif command == "Save & Quit":
                    if self.world.save_game():
                        print("Game saved. Exiting.")
                        arcade.exit()
                    else:
                        # Error message already appended to world log by save_game()
                        self.log_messages_to_display.clear()
                        self.log_messages_to_display.extend(self.world.get_messages())
                        # Stay in current view, menu options remain the same
                        self._prepare_scrollable_text_for_current_mode()
                    return

                elif command == "Check Bags": 
                    self.pre_bags_view_mode = self.display_mode
                    self.pre_bags_menu_type = self.active_menu_type 
                    self.display_mode = "view_bags"
                    self.update_menu_options("view_bags_menu")
                    self.log_messages_to_display.clear()
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                elif command == "Drop Item to Take":
                    next_game_state = self.world.handle_player_choice(command)
                    self.log_messages_to_display.clear()
                    self.log_messages_to_display.extend(self.world.get_messages())
                    if next_game_state == "select_item_to_drop_for_loot":
                        self.display_mode = "select_item_to_drop_for_loot_display"
                        self.update_menu_options("select_item_to_drop_for_loot_menu")
                    else:
                        self.display_mode = "loot_decision_display"
                        self.update_menu_options("loot_decision_menu")
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                # --- Re-adding Grimoire button logic for in-game camp menu ---
                elif command == "Grimoire" and self.active_menu_type == "inventory_management":
                    print("--- Grimoire button pressed! (In-Game Camp) ---")
                    grimoire_view = GrimoireView(self.world.grimoire_entries, self)
                    self.window.show_view(grimoire_view)
                    # Not clearing log or re-preparing text, as GameView will redraw on return.
                    return
                elif command == "Back" and self.active_menu_type == "view_bags_menu": 
                    self.display_mode = self.pre_bags_view_mode if self.pre_bags_view_mode else "area_description"
                    current_menu_to_restore = self.pre_bags_menu_type if self.pre_bags_menu_type else "main"
                    self.update_menu_options(current_menu_to_restore)
                    self.log_messages_to_display.clear()
                    if self.display_mode == "area_description":
                        self.world.display_current_area() 
                        self.log_messages_to_display.extend(self.world.get_messages()) 
                    elif self.display_mode == "combat_log" and current_menu_to_restore == "player_combat_turn":
                        self.log_messages_to_display.append("--- Your Turn ---")
                        self.log_messages_to_display.append("It's your turn!")
                    self._prepare_scrollable_text_for_current_mode()
                    return 
                self.log_messages_to_display.clear()
                action_command_to_world = command
                if self.active_menu_type == "select_item_to_equip_menu" and command.isdigit(): 
                    action_command_to_world = f"Equip Index: {int(command)-1}" 
                next_game_state = self.world.handle_player_choice(action_command_to_world)
                self.log_messages_to_display.extend(self.world.get_messages())
                if next_game_state == "player_combat_turn":
                    self.display_mode = "combat_log"
                    self.update_menu_options("player_combat_turn") 
                elif next_game_state == "travel_options":
                    self.display_mode = "area_description" 
                    self.update_menu_options("travel") 
                elif next_game_state == "show_loot_options": 
                    self.display_mode = "combat_log" 
                    self.display_mode = "loot_decision_display" 
                    self.update_menu_options("loot_decision_menu") 
                elif next_game_state == "show_defeat_log_at_camp": 
                    self.display_mode = "combat_log" 
                    self.load_current_area_art() 
                    self.update_menu_options("defeat_acknowledged_menu") 
                elif next_game_state == "show_rest_screen": # New state from World after resting/exhaustion
                    self.display_mode = "combat_log" # Reuse combat_log for message display
                    self.load_current_area_art() # World has moved player to camp
                    self.update_menu_options("rest_screen_menu") # Show "Get Up" button
                elif next_game_state == "inventory_management": 
                    self.display_mode = "inventory_management"
                    self.update_menu_options("inventory_management")
                elif next_game_state == "select_item_to_equip_mode": 
                    self.display_mode = "select_item_to_equip_display"
                    self.update_menu_options("select_item_to_equip_menu")
                elif next_game_state == "select_item_to_drop_for_loot": 
                    self.display_mode = "select_item_to_drop_for_loot_display"
                    self.update_menu_options("select_item_to_drop_for_loot_menu")
                elif next_game_state == "area_description": 
                    self.display_mode = "area_description"
                    self.update_menu_options("main") 
                    self.load_current_area_art() 
                self._prepare_scrollable_text_for_current_mode() 
                return 
        else: 
            if self.display_mode == "inventory_management": 
                clicked_item_sprites = arcade.get_sprites_at_point((x,y), self.inventory_item_clickable_sprites)
                if clicked_item_sprites:
                    clicked_item_sprite = clicked_item_sprites[0]
                    self.selected_inventory_item = clicked_item_sprite.properties.get('item_object')
                    self.selected_item_source = clicked_item_sprite.properties.get('item_source') 
                    print(f"Selected item source: {self.selected_item_source}")
                    if self.selected_inventory_item:
                        print(f"Clicked on item: {self.selected_inventory_item.name}")
                        self.display_mode = "item_details_display"
                        self.update_menu_options("item_details_menu")
                        self.log_messages_to_display.clear() 
                        self._prepare_scrollable_text_for_current_mode() 
                        return 
            elif self.display_mode == "select_item_to_drop_for_loot_display":
                clicked_item_sprites = arcade.get_sprites_at_point((x,y), self.inventory_item_clickable_sprites)
                if clicked_item_sprites:
                    clicked_item_sprite = clicked_item_sprites[0]
                    item_to_drop = clicked_item_sprite.properties.get('item_object')
                    if item_to_drop:
                        print(f"Player chose to drop: {item_to_drop.name} to make space for loot.")
                        self.log_messages_to_display.clear()
                        next_game_state = self.world.handle_player_choice(f"DropForLoot: {item_to_drop.name}")
                        self.log_messages_to_display.extend(self.world.get_messages())
                        if next_game_state == "area_description":
                            self.display_mode = "area_description"
                            self.update_menu_options("main")
                        else:
                            print(f"WARNING GameView: Unexpected next_game_state '{next_game_state}' after DropForLoot. Loot sequence might not have fully completed as expected by GameView.")
                        self._prepare_scrollable_text_for_current_mode()
                        return 

    def on_update(self, delta_time: float):
        self.player.update_stats()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if self.scrollable_text_rect_on_screen:
            s_rect_x, s_rect_bottom_y, s_rect_width, s_rect_height = self.scrollable_text_rect_on_screen
            s_rect_top_y = s_rect_bottom_y + s_rect_height
            if s_rect_x <= x <= s_rect_x + s_rect_width and \
               s_rect_bottom_y <= y <= s_rect_top_y:
                # Apply scroll logic if there's content to scroll
                if self.current_view_content_height > 0:
                    # Natural scrolling: wheel down (scroll_y is negative) -> content moves up (scroll_offset_y increases)
                    # This line should be correct for natural scrolling if text views use +offset and icon views use +offset in drawing
                    self.scroll_offset_y -= scroll_y * TEXT_AREA_LINE_HEIGHT * 2
                    
                    # Use the actual height of the scrollable rectangle for clamping
                    s_rect_actual_height = self.scrollable_text_rect_on_screen[3] 
                    max_scroll = max(0, self.current_view_content_height - s_rect_actual_height)
                    
                    self.scroll_offset_y = arcade.clamp(self.scroll_offset_y, 0, max_scroll)
                    print(f"GameView Scroll Clamp: current_offset_y={self.scroll_offset_y:.2f}, max_scroll={max_scroll:.2f}, content_h={self.current_view_content_height:.2f}, viewport_h={s_rect_actual_height:.2f}")

def main():
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