# name_entry_view.py
import arcade
import arcade.color
from arcade.gui import UIManager, UIInputText, UIAnchorWidget # UIAnchorWidget currently unused but kept for potential future use

from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_INFO_BANNER_HEIGHT, TOP_PADDING,
                       TOP_BANNER_BACKGROUND_IMAGE, MENU_BUTTON_IMAGE_PATH,
                       MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, MENU_BUTTON_VERTICAL_SPACING, INPUT_BOX_BACKGROUND_PADDING, # Added PADDING
                       MENU_BUTTON_TEXT_PADDING, BUTTON_FONT_SIZE, INPUT_BOX_BACKGROUND_IMAGE_PATH, # Added INPUT_BOX_BACKGROUND_IMAGE_PATH
                       INVENTORY_BACKGROUND_IMAGE, MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE, # For panel backgrounds
                       LEFT_PADDING, MENU_PANEL_WIDTH, RIGHT_MENU_X_START, CC_NAME_INPUT_WIDTH, CC_NAME_INPUT_HEIGHT,
                       GAME_AREA_WIDTH) # Added GAME_AREA_WIDTH
from game_view import GameView
from scripts.world import World
# For type hinting to resolve circular imports.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from character_creation_view import CharacterCreationView

class NameEntryView(arcade.View):
    def __init__(self, previous_view: 'CharacterCreationView', selected_background_data: dict):
        super().__init__()
        self.previous_view = previous_view
        self.selected_background_data = selected_background_data

        self.manager = UIManager()
        self.name_input_box = None
        self.ui_elements = arcade.SpriteList()
        self.input_box_background_sprite = None # For custom textured background

        self.top_banner_texture = None
        try:
            self.top_banner_texture = arcade.load_texture(TOP_BANNER_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: Top banner background image '{TOP_BANNER_BACKGROUND_IMAGE}' not found for NameEntryView.")

        self.menu_button_texture = None
        try:
            self.menu_button_texture = arcade.load_texture(MENU_BUTTON_IMAGE_PATH)
        except FileNotFoundError:
            print(f"ERROR: Menu button image not found at {MENU_BUTTON_IMAGE_PATH} for NameEntryView")

        # Load background for the main input area (left panel)
        self.main_area_background_texture = None
        try:
            self.main_area_background_texture = arcade.load_texture(INVENTORY_BACKGROUND_IMAGE) # Using inventory bg as a general panel
        except FileNotFoundError:
            print(f"Warning: NameEntryView main area background image '{INVENTORY_BACKGROUND_IMAGE}' not found.")

        # Load background for the right menu panel
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: NameEntryView right panel background image '{MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        # Load background for the input box itself
        self.input_box_background_texture = None
        try:
            self.input_box_background_texture = arcade.load_texture(INPUT_BOX_BACKGROUND_IMAGE_PATH)
        except FileNotFoundError:
            print(f"Warning: NameEntryView input box background image '{INPUT_BOX_BACKGROUND_IMAGE_PATH}' not found.")

        self._setup_ui()

    def _setup_ui(self):
        self.manager.clear()
        self.ui_elements.clear()

        # Name Input Box
        input_box_center_x = GAME_AREA_WIDTH / 2
        input_box_center_y = (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2 # Vertically centered in game area

        input_width = CC_NAME_INPUT_WIDTH * 1.5
        input_height = CC_NAME_INPUT_HEIGHT
        input_x = input_box_center_x - input_width / 2
        input_y = input_box_center_y - input_height / 2

        # Create the background sprite for the input box
        if self.input_box_background_texture:
            self.input_box_background_sprite = arcade.Sprite(texture=self.input_box_background_texture)
            self.input_box_background_sprite.width = input_width + (4 * INPUT_BOX_BACKGROUND_PADDING) # Add padding to width
            self.input_box_background_sprite.height = input_height + (2 * INPUT_BOX_BACKGROUND_PADDING) # Add padding to height
            self.input_box_background_sprite.center_x = input_box_center_x
            self.input_box_background_sprite.center_y = input_box_center_y

        # Define a style for the input box to make its own background transparent
        input_style_params = {
            "font_color": arcade.color.BLACK,
            "bg_color": (0,0,0,0), # Transparent background
            "border_width": 0,     # No border (or a thin one if you want it over the texture)
            # Note: 'font_name' and 'font_size' for the typed text are direct parameters
            # 'caret_color', 'selection_font_color', 'selection_bg_color' are other style options
        }

        self.name_input_box = UIInputText(
            x=input_x,
            y=input_y,
            width=input_width,
            height=input_height,
            font_size=20, # Font size for the text you type
            text="Adventurer", # Default text
            text_color=arcade.color.BLACK, # Color for the text you type,
            max_length=15, # Limit input to 15 characters
            **input_style_params # Pass style parameters
        )
        self.manager.add(self.name_input_box)

        # --- Buttons moved to the right panel ---
        button_panel_center_x = RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2

        # Back Button (Bottom-most in the right panel)
        back_button_sprite = arcade.Sprite(texture=self.menu_button_texture) if self.menu_button_texture else arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_RED)
        back_button_sprite.width = MENU_BUTTON_TARGET_WIDTH
        back_button_sprite.height = MENU_BUTTON_HEIGHT
        back_button_sprite.center_x = button_panel_center_x
        back_button_sprite.center_y = MENU_BUTTON_HEIGHT * 1.5 # Position near bottom
        back_button_sprite.properties['text'] = "Back"
        back_button_sprite.properties['action'] = "back_to_character_creation"
        self.ui_elements.append(back_button_sprite)

        # Confirm Button
        confirm_button_sprite = arcade.Sprite(texture=self.menu_button_texture) if self.menu_button_texture else arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_GREEN)
        confirm_button_sprite.width = MENU_BUTTON_TARGET_WIDTH
        confirm_button_sprite.height = MENU_BUTTON_HEIGHT
        confirm_button_sprite.center_x = button_panel_center_x
        confirm_button_sprite.center_y = back_button_sprite.center_y + MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING # Above back button
        confirm_button_sprite.properties['text'] = "Confirm Name"
        confirm_button_sprite.properties['action'] = "confirm_name"
        self.ui_elements.append(confirm_button_sprite)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.manager.enable()
        if self.name_input_box:
            self.manager.focused_widget = self.name_input_box # type: ignore

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        # --- Top Banner ---
        if self.top_banner_texture:
            arcade.draw_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, SCREEN_WIDTH, PLAYER_INFO_BANNER_HEIGHT, self.top_banner_texture)
        else:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, SCREEN_WIDTH, PLAYER_INFO_BANNER_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_text("Enter Your Name", SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # arcade.draw_rectangle_filled(
        # --- Main Content Area Background (Left of Menu) ---
        if self.main_area_background_texture:
            arcade.draw_texture_rectangle(
                GAME_AREA_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.main_area_background_texture
            )
        else: # Fallback
            arcade.draw_rectangle_filled(
                GAME_AREA_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                GAME_AREA_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_GRAY # Fallback color for main area
            )
        # Dark overlay for main content area to help input box stand out
        arcade.draw_rectangle_filled(
            GAME_AREA_WIDTH / 2,
            (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
            GAME_AREA_WIDTH,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
            (20,20,20,200) 
        )

        # Draw the custom background for the input box (if it exists)
        if self.input_box_background_sprite:
            self.input_box_background_sprite.draw()
        # --- Right-Hand Menu Panel Background ---
        if self.right_panel_background_texture:
            arcade.draw_texture_rectangle(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.right_panel_background_texture
            )
        else: # Fallback
            arcade.draw_rectangle_filled(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY
            )

        # --- UI Elements ---
        self.manager.draw() 
        self.ui_elements.draw()

        for button in self.ui_elements:
            arcade.draw_text(button.properties['text'], button.center_x, button.center_y,
                             arcade.color.WHITE, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
                             width=int(button.width - 2 * MENU_BUTTON_TEXT_PADDING))

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        clicked_buttons = arcade.get_sprites_at_point((x, y), self.ui_elements)
        if clicked_buttons:
            action = clicked_buttons[0].properties['action']
            if action == "confirm_name":
                character_name = self.name_input_box.text.strip() if self.name_input_box and self.name_input_box.text.strip() else "Adventurer"
                print(f"--- Character '{character_name}' with background '{self.selected_background_data.get('name', 'Unknown')}' confirmed! ---")
                
                game_world = World() 
                game_world.create_character(name=character_name, background_data=self.selected_background_data)
                
                game_view = GameView(game_world)
                self.window.show_view(game_view)

            elif action == "back_to_character_creation":
                self.window.show_view(self.previous_view)
        
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        self.manager.on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER: # type: ignore
            if self.name_input_box and self.manager.focused_widget is self.name_input_box: # type: ignore
                character_name = self.name_input_box.text.strip() if self.name_input_box.text.strip() else "Adventurer"
                print(f"--- Character '{character_name}' (from Enter) with background '{self.selected_background_data.get('name', 'Unknown')}' confirmed! ---")
                game_world = World()
                game_world.create_character(name=character_name, background_data=self.selected_background_data)
                game_view = GameView(game_world)
                self.window.show_view(game_view)
        elif symbol == arcade.key.ESCAPE: # type: ignore
            self.window.show_view(self.previous_view)

    def on_key_release(self, symbol: int, modifiers: int):
        self.manager.on_key_release(symbol, modifiers)