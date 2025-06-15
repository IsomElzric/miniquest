import logging
import arcade
import os
import arcade.color # Explicitly import arcade.color
from arcade.gui import UIManager # UIInputText, UIAnchorWidget 
import textwrap # For wrapping text into lines

# Import constants and other views/modules
from constants import (TOP_BANNER_BACKGROUND_IMAGE, MENU_BUTTON_IMAGE_PATH, PLAYER_INFO_BANNER_HEIGHT,
                       LEFT_PADDING, CC_BACKGROUND_BUTTON_WIDTH, CC_BACKGROUND_BUTTON_HEIGHT, SCREEN_HEIGHT, INVENTORY_BACKGROUND_IMAGE, TOP_PADDING, # CC_BACKGROUND_BUTTON_HEIGHT is same as MENU_BUTTON_HEIGHT
                       CC_DESC_AREA_Y_START_OFFSET, SCREEN_WIDTH, MENU_PANEL_WIDTH, RIGHT_MENU_X_START, GAME_AREA_WIDTH, MENU_BUTTON_VERTICAL_SPACING, CC_DESC_TEXT_PADDING, CHARACTER_ART_PATH, DEFAULT_CHARACTER_ART_IMAGE,
                       MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, # Import standard button dimensions
                       MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE, CC_LEFT_PANEL_BUTTON_AREA_BG_IMAGE, # Added for the right panel
                       CC_CHAR_ART_Y_START_OFFSET, CC_CHAR_ART_BOTTOM_PADDING, CC_CHAR_ART_WIDTH, # Character art constants
                       BUTTON_FONT_SIZE, MENU_BUTTON_TEXT_PADDING, CC_DESC_AREA_X, CC_DESC_AREA_WIDTH, # Removed 'arcade' from this import
                       TEXT_AREA_FONT_SIZE, TEXT_AREA_LINE_HEIGHT, CC_BACKGROUND_BUTTON_SPACING)

from typing import TYPE_CHECKING # Keep TYPE_CHECKING for MenuView hint
if TYPE_CHECKING: # MenuView is only for type hinting
    from menu_view import MenuView # This import is only for type checking
from scripts.builder import Builder # Import Builder
from name_entry_view import NameEntryView # Import the new view

logging.getLogger('arcade').setLevel(logging.INFO)


class CharacterCreationView(arcade.View):
    def __init__(self, previous_view: 'MenuView'): # Use string literal for type hint
        super().__init__()
        self.previous_view = previous_view

        # Instantiate Builder to load background data
        self.builder = Builder(message_log=lambda msg: print(f"CCView_Builder: {msg}")) # Simple logger for builder
        self.backgrounds_data = self.builder.build_backgrounds() # Load from JSONs
        self.background_options = list(self.backgrounds_data.keys())

        self.selected_background_key = None 

        self.manager = UIManager()
        self.manager.enable()

        # Scrolling for description panel
        self.desc_scroll_offset_y = 0.0
        self.desc_content_total_height = 0.0
        self.desc_area_view_rect = None # Will be defined in on_draw or _setup_ui

        # Load top banner background (same as MenuView)
        self.top_banner_texture = None
        try:
            self.top_banner_texture = arcade.load_texture(TOP_BANNER_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: Top banner background image '{TOP_BANNER_BACKGROUND_IMAGE}' not found for CharacterCreationView.")

        # Load menu button texture (consistent with GameView/MenuView)
        self.menu_button_texture = None
        try:
            self.menu_button_texture = arcade.load_texture(MENU_BUTTON_IMAGE_PATH)
        except FileNotFoundError:
            print(f"ERROR: Menu button image not found at {MENU_BUTTON_IMAGE_PATH} for CharacterCreationView")

        # Load right panel background (consistent with MenuView/GameView)
        self.right_panel_background_texture = None
        try:
            self.right_panel_background_texture = arcade.load_texture(MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: CharacterCreationView right panel background image '{MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE}' not found.")

        # Load description panel background (inventory background)
        self.description_panel_texture = None
        try:
            self.description_panel_texture = arcade.load_texture(INVENTORY_BACKGROUND_IMAGE)
        except FileNotFoundError:
            print(f"Warning: CharacterCreationView description panel background image '{INVENTORY_BACKGROUND_IMAGE}' not found.")

        # Load static background for the left panel's button area
        self.left_panel_button_area_texture = None
        try:
            self.left_panel_button_area_texture = arcade.load_texture(CC_LEFT_PANEL_BUTTON_AREA_BG_IMAGE)
        except FileNotFoundError:
            print(f"Warning: CharacterCreationView left panel button area background '{CC_LEFT_PANEL_BUTTON_AREA_BG_IMAGE}' not found.")
        self.selected_character_art_texture = None # To hold the art of the selected character

        # Load default character art
        self.default_character_art_texture = None
        try:
            self.default_character_art_texture = arcade.load_texture(DEFAULT_CHARACTER_ART_IMAGE)
        except FileNotFoundError:
            print(f"Warning: CharacterCreationView default character art '{DEFAULT_CHARACTER_ART_IMAGE}' not found.")

        self.ui_elements = arcade.SpriteList()
        self._setup_ui() # Now call _setup_ui AFTER textures are initialized

    def _setup_ui(self):
        self.ui_elements.clear()
        self.manager.clear() # Clear existing UI manager elements

        # Background selection buttons (left panel)
        # Move buttons to the top of the panel
        start_y_for_buttons = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - TOP_PADDING - (CC_BACKGROUND_BUTTON_HEIGHT / 2) - 30 # Start high
        for i, bg_name in enumerate(self.background_options):
            button = arcade.SpriteSolidColor(CC_BACKGROUND_BUTTON_WIDTH, CC_BACKGROUND_BUTTON_HEIGHT, arcade.color.DARK_SLATE_GRAY)
            if self.menu_button_texture:
                button = arcade.Sprite(texture=self.menu_button_texture)
                button.width = CC_BACKGROUND_BUTTON_WIDTH
                button.height = CC_BACKGROUND_BUTTON_HEIGHT

            # Center the button within the full width of the left panel area
            button.center_x = (LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH) / 2
            button.center_y = start_y_for_buttons - (CC_BACKGROUND_BUTTON_HEIGHT / 2) - (i * (CC_BACKGROUND_BUTTON_HEIGHT + CC_BACKGROUND_BUTTON_SPACING))
            button.properties['text'] = bg_name
            button.properties['action'] = f"select_bg_{bg_name}"
            self.ui_elements.append(button)

        # Back button (bottom right, lowest button in the panel)
        back_button = arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_RED)
        if self.menu_button_texture:
            back_button = arcade.Sprite(texture=self.menu_button_texture)
            back_button.width = MENU_BUTTON_TARGET_WIDTH
            back_button.height = MENU_BUTTON_HEIGHT
            
        back_button.center_x = SCREEN_WIDTH - MENU_PANEL_WIDTH / 2 # Center in the right panel area
        back_button.center_y = MENU_BUTTON_HEIGHT * 1.5 # Use MENU_BUTTON_HEIGHT for positioning
        back_button.properties['text'] = "Back"
        back_button.properties['action'] = "back_to_menu"
        self.ui_elements.append(back_button)

        # Confirm button (bottom right of description area)
        confirm_button = arcade.SpriteSolidColor(MENU_BUTTON_TARGET_WIDTH, MENU_BUTTON_HEIGHT, arcade.color.DARK_GREEN if self.selected_background_key else arcade.color.DARK_RED)
        if self.menu_button_texture:
            confirm_button = arcade.Sprite(texture=self.menu_button_texture)
            confirm_button.width = MENU_BUTTON_TARGET_WIDTH
            confirm_button.height = MENU_BUTTON_HEIGHT
        confirm_button.center_x = SCREEN_WIDTH - MENU_PANEL_WIDTH / 2 # Center in the right panel area
        confirm_button.center_y = back_button.center_y + MENU_BUTTON_HEIGHT + MENU_BUTTON_VERTICAL_SPACING # Position above Back button with spacing
        confirm_button.properties['text'] = "Confirm"
        confirm_button.properties['action'] = "confirm_selection"
        self.ui_elements.append(confirm_button)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.manager.enable()
        self._setup_ui() # Re-setup UI in case selected_background_key changed visibility of confirm

    def on_draw(self):
        self.clear()

        # Draw Top Banner
        if self.top_banner_texture:
            arcade.draw_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, SCREEN_WIDTH, PLAYER_INFO_BANNER_HEIGHT, self.top_banner_texture)
        else:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, SCREEN_WIDTH, PLAYER_INFO_BANNER_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_text("Choose Your Background", SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT / 2, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Draw Background Options Panel (Left) - just a darker rect for now
        left_panel_content_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        left_panel_center_y = left_panel_content_height / 2
        left_panel_width = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH
        left_panel_center_x = left_panel_width / 2

        # Draw the selected character's art or the default art FIRST
        if self.selected_character_art_texture:
            self._draw_selected_character_art()
        elif self.default_character_art_texture: # If no character selected, draw default
            self._draw_default_character_art()

        # Draw the static background for the button area if available
        if self.left_panel_button_area_texture:
            arcade.draw_texture_rectangle(
                center_x=left_panel_center_x,
                center_y=left_panel_center_y, # Assuming it covers the whole panel height for now
                width=left_panel_width,
                height=left_panel_content_height,
                texture=self.left_panel_button_area_texture
            )
        else: # Fallback
            arcade.draw_rectangle_filled(left_panel_center_x, left_panel_center_y, left_panel_width, left_panel_content_height, (0,0,0,100))

        # Draw Description Panel (Right)
        # This panel covers the area from CC_DESC_AREA_X to GAME_AREA_WIDTH
        desc_panel_actual_width = GAME_AREA_WIDTH - CC_DESC_AREA_X
        desc_panel_center_x = CC_DESC_AREA_X + desc_panel_actual_width / 2
        desc_panel_center_y = (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2
        desc_panel_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT

        # Draw the specific background for the description panel first
        if self.description_panel_texture:
            arcade.draw_texture_rectangle(
                center_x=desc_panel_center_x,
                center_y=desc_panel_center_y,
                width=desc_panel_actual_width,
                height=desc_panel_height,
                texture=self.description_panel_texture
            )

        # Then, draw the translucent dark overlay on top of the description panel's background
        arcade.draw_rectangle_filled(
            center_x=desc_panel_center_x,
            center_y=desc_panel_center_y,
            width=desc_panel_actual_width,
            height=desc_panel_height,
            color=(20, 20, 20, 150)  # The semi-transparent black overlay
        )
        # --- Draw Right-Hand Menu Panel Background ---
        if self.right_panel_background_texture:
            arcade.draw_texture_rectangle(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                self.right_panel_background_texture
            )
        else: # Fallback color if texture not loaded
            arcade.draw_rectangle_filled(
                RIGHT_MENU_X_START + MENU_PANEL_WIDTH / 2,
                (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
                MENU_PANEL_WIDTH,
                SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
                arcade.color.DARK_SLATE_GRAY # Consistent fallback
            )

        # Draw selected background description and stats (Moved from _draw_character_art_texture)
        if self.selected_background_key:
            # Define the viewport for the description area
            desc_panel_top_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET # Top of the description content area
            desc_panel_bottom_y = MENU_BUTTON_HEIGHT * 3.5 # Use MENU_BUTTON_HEIGHT. Approx bottom, above confirm/back buttons
            desc_panel_height = desc_panel_top_y - desc_panel_bottom_y
            self.desc_area_view_rect = (CC_DESC_AREA_X, desc_panel_bottom_y, CC_DESC_AREA_WIDTH, desc_panel_height)

            # Calculate drawing coordinates and width for text, applying internal padding
            text_draw_x = CC_DESC_AREA_X + CC_DESC_TEXT_PADDING
            text_draw_width = CC_DESC_AREA_WIDTH - (2 * CC_DESC_TEXT_PADDING)

            # Wrap and draw description
            wrap_width_chars = int(text_draw_width / (TEXT_AREA_FONT_SIZE * 0.6)) if (TEXT_AREA_FONT_SIZE * 0.6) > 0 else 50

            selected_bg_data = self.backgrounds_data[self.selected_background_key]
            stat_summary_lines = []
            stats = selected_bg_data.get("stats", {})
            stat_summary_lines.append("Initial Stats:")
            stat_summary_lines.append(f"  Attack: {stats.get('attack', 'N/A')}")
            stat_summary_lines.append(f"  Defense: {stats.get('defense', 'N/A')}")
            stat_summary_lines.append(f"  Speed: {stats.get('speed', 'N/A')}")
            
            temp_total_height = 30 
            for line in stat_summary_lines:
                temp_total_height += TEXT_AREA_LINE_HEIGHT
            temp_total_height += TEXT_AREA_LINE_HEIGHT
            
            description_text = self.backgrounds_data[self.selected_background_key].get("description", "No description.")
            wrapped_description = textwrap.wrap(description_text, width=wrap_width_chars)
            for line in wrapped_description:
                temp_total_height += TEXT_AREA_LINE_HEIGHT
            self.desc_content_total_height = temp_total_height

            max_scroll = max(0, self.desc_content_total_height - self.desc_area_view_rect[3])
            self.desc_scroll_offset_y = arcade.clamp(self.desc_scroll_offset_y, 0, max_scroll)
            
            title_start_y = desc_panel_top_y + self.desc_scroll_offset_y # CORRECTED: Subtracted scroll offset
            title_block_height = 30

            if self.desc_scroll_offset_y < (1.5 * TEXT_AREA_LINE_HEIGHT):
                arcade.draw_text(f"Background: {self.selected_background_key}",
                                 text_draw_x, title_start_y, arcade.color.GOLD, font_size=18, bold=True, anchor_y="top",
                                 width=text_draw_width)
            
            current_draw_y = title_start_y - title_block_height

            for line_num, line in enumerate(stat_summary_lines):
                line_top_y = current_draw_y
                line_bottom_y = current_draw_y - TEXT_AREA_LINE_HEIGHT
                if line_bottom_y < self.desc_area_view_rect[1] + self.desc_area_view_rect[3] and line_top_y > self.desc_area_view_rect[1]:
                    arcade.draw_text(line, text_draw_x, current_draw_y, arcade.color.LIGHT_GRAY, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top", width=text_draw_width)
                current_draw_y -= TEXT_AREA_LINE_HEIGHT
            
            current_draw_y -= TEXT_AREA_LINE_HEIGHT

            for line_num, line in enumerate(wrapped_description):
                line_top_y = current_draw_y
                line_bottom_y = current_draw_y - TEXT_AREA_LINE_HEIGHT
                if line_bottom_y < self.desc_area_view_rect[1] + self.desc_area_view_rect[3] and line_top_y > self.desc_area_view_rect[1]:
                    arcade.draw_text(line, text_draw_x, current_draw_y, arcade.color.WHITE, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top", width=text_draw_width)
                current_draw_y -= TEXT_AREA_LINE_HEIGHT

        # Draw UI elements (buttons) and manager (if any UIElements are added to it)
        self.ui_elements.draw()
        self.manager.draw() 

        # Draw text on buttons
        for button in self.ui_elements:
            text_color = arcade.color.WHITE
            if button.properties['action'] == "confirm_selection" and not self.selected_background_key:
                text_color = arcade.color.GRAY # Dim text if confirm is not active
            
            arcade.draw_text(button.properties['text'], button.center_x, button.center_y,
                             text_color, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
                             width=int(button.width - 2 * MENU_BUTTON_TEXT_PADDING))

    def _draw_selected_character_art(self):
        self._draw_character_art_texture(self.selected_character_art_texture)

    def _draw_default_character_art(self):
        self._draw_character_art_texture(self.default_character_art_texture)

    def _draw_character_art_texture(self, texture_to_draw):
        if not texture_to_draw:
            return

        panel_width = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH
        panel_height = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT
        panel_center_x = panel_width / 2
        panel_center_y = panel_height / 2

        if panel_height > 0 and panel_width > 0:
            arcade.draw_texture_rectangle(
                center_x=panel_center_x,
                center_y=panel_center_y,
                width=panel_width,
                height=panel_height,
                texture=texture_to_draw
            )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        clicked = arcade.get_sprites_at_point((x, y), self.ui_elements)
        if clicked:
            action = clicked[0].properties['action']
            if action.startswith("select_bg_"):
                self.selected_background_key = action.replace("select_bg_", "")
                self.desc_scroll_offset_y = 0 # Reset scroll on new selection
                # Load character artoptional: for debugging
                art_filename = self.selected_background_key.lower().replace(" ", "_") + ".png"
                art_path = os.path.join(CHARACTER_ART_PATH, art_filename)
                try:
                    self.selected_character_art_texture = arcade.load_texture(art_path)
                    # print(f"Loaded character art: {art_path}")
                except FileNotFoundError:
                    self.selected_character_art_texture = None # Or a placeholder
                    # print(f"Character art not found: {art_path}")
                
                self._setup_ui() # Refresh UI to update confirm button color
            elif action == "confirm_selection":
                if self.selected_background_key:
                    chosen_background_data = self.backgrounds_data[self.selected_background_key] # Get the full data dict
                    print(f"--- Background '{self.selected_background_key}' selected, proceeding to name entry. ---")
                    name_entry_v = NameEntryView(self, chosen_background_data)
                    self.window.show_view(name_entry_v)
                else:
                    print("No background selected.") # Should not happen if button is disabled visually
            elif action == "back_to_menu":
                self.manager.disable() # Disable UI manager when leaving view
                self.window.show_view(self.previous_view)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if self.desc_area_view_rect and self.selected_background_key:
            rect_x, rect_y, rect_width, rect_height = self.desc_area_view_rect
            # Check if mouse is over the description panel
            if rect_x <= x <= rect_x + rect_width and \
               rect_y <= y <= rect_y + rect_height:
                
                self.desc_scroll_offset_y -= scroll_y * TEXT_AREA_LINE_HEIGHT * 1.5 # scroll_speed_multiplier

    def on_hide_view(self):
        self.manager.disable() # Important to disable UIManager