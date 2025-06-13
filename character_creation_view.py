import logging
import arcade
# os, sys, and Counter are not used in this file.
# arcade.gui is used, specifically UIManager, UIInputText, UIAnchorWidget.
from arcade.gui import UIManager, UIInputText, UIAnchorWidget 
import textwrap # For wrapping text into lines

# Import constants and other views/modules
from constants import * 
from game_view import GameView
from scripts.world import World

# For type hinting to resolve circular imports.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from menu_view import MenuView # This import is only for type checking

logging.getLogger('arcade').setLevel(logging.INFO)


class CharacterCreationView(arcade.View):
    def __init__(self, previous_view: 'MenuView'): # Use string literal for type hint
        super().__init__()
        self.previous_view = previous_view
        self.background_options = list(BACKGROUNDS_DATA.keys())
        self.selected_background_key = None
        self.selected_background_details = ""

        self.manager = UIManager()
        self.manager.enable()
        self.name_input_box = None

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

        self.ui_elements = arcade.SpriteList()
        self._setup_ui() # Now call _setup_ui AFTER textures are initialized

    def _setup_ui(self):
        self.ui_elements.clear()
        self.manager.clear() # Clear existing UI manager elements

        # Name Input Box (Above background selection buttons, or in the description panel)
        # --- Temporarily removing name input box ---
        # name_input_style = {
        #     "font_color": arcade.color.BLACK,      # Color of the default text "Adventurer" if not focused
        #     "bg_color": arcade.color.YELLOW_ORANGE, # A very visible background color
        #     "border_color": arcade.color.RED_DEVIL,   # A very visible border color
        #     "border_width": 2,
        # }
        # Note: The actual editable text color and font_size are set by UIInputText's own parameters.

        # self.name_input_box = UIInputText( # Corrected usage if UIInputText is directly imported
        #     width=CC_NAME_INPUT_WIDTH, 
        #     height=CC_NAME_INPUT_HEIGHT, # Use the full defined height
        #     font_size=18, # Font size for the text you type
        #     text="Adventurer", # Default text
        #     text_color=arcade.color.BLACK, # Color for the text you type
        #     style=name_input_style # Apply the custom style
        # )


        # Anchor the UIInputText directly
        # name_input_anchor = UIAnchorWidget(
        #     child=self.name_input_box, # Anchor the input box directly
        #     anchor_x="center_x",  # Align child's center_x to the anchor's x.
        #     anchor_y="top",       # Align child's top to the anchor's y.
        #     # Position the anchor widget itself.
        #     x=LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH / 2,  # Centered in the left button panel area
        #     y=SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET  # This will be the child's top.
        # )
        # self.manager.add(name_input_anchor)

        # Background selection buttons (left panel)
        start_y_for_buttons = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET - 30 # Adjusted Y, no longer depends on name input height
        for i, bg_name in enumerate(self.background_options):
            button = arcade.SpriteSolidColor(CC_BACKGROUND_BUTTON_WIDTH, CC_BACKGROUND_BUTTON_HEIGHT, arcade.color.DARK_SLATE_GRAY)
            if self.menu_button_texture:
                button = arcade.Sprite(texture=self.menu_button_texture)
                button.width = CC_BACKGROUND_BUTTON_WIDTH
                button.height = CC_BACKGROUND_BUTTON_HEIGHT

            button.center_x = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH / 2
            button.center_y = start_y_for_buttons - (CC_BACKGROUND_BUTTON_HEIGHT / 2) - (i * (CC_BACKGROUND_BUTTON_HEIGHT + CC_BACKGROUND_BUTTON_SPACING))
            button.properties['text'] = bg_name
            button.properties['action'] = f"select_bg_{bg_name}"
            self.ui_elements.append(button)

        # Confirm button (bottom right of description area)
        confirm_button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, arcade.color.DARK_GREEN if self.selected_background_key else arcade.color.DARK_RED)
        if self.menu_button_texture:
            confirm_button = arcade.Sprite(texture=self.menu_button_texture)
            confirm_button.width = BUTTON_WIDTH
            confirm_button.height = BUTTON_HEIGHT
        
        confirm_button.center_x = SCREEN_WIDTH - MENU_PANEL_WIDTH / 2 # Center in the right panel area
        confirm_button.center_y = BUTTON_HEIGHT * 2.5 # Position it a bit higher than Back
        confirm_button.properties['text'] = "Confirm"
        confirm_button.properties['action'] = "confirm_selection"
        self.ui_elements.append(confirm_button)

        # Back button (bottom right, below confirm)
        back_button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, arcade.color.DARK_RED)
        if self.menu_button_texture:
            back_button = arcade.Sprite(texture=self.menu_button_texture)
            back_button.width = BUTTON_WIDTH
            back_button.height = BUTTON_HEIGHT

        back_button.center_x = SCREEN_WIDTH - MENU_PANEL_WIDTH / 2 # Center in the right panel area
        back_button.center_y = BUTTON_HEIGHT * 1.5
        back_button.properties['text'] = "Back"
        back_button.properties['action'] = "back_to_menu"
        self.ui_elements.append(back_button)

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
        arcade.draw_rectangle_filled(
            (LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH + LEFT_PADDING) / 2,
            (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
            CC_BACKGROUND_BUTTON_WIDTH + LEFT_PADDING * 2,
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
            (0,0,0,100) # Semi-transparent black
        )

        # Draw Description Panel (Right)
        arcade.draw_rectangle_filled(
            CC_DESC_AREA_X + CC_DESC_AREA_WIDTH / 2,
            (SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT) / 2,
            CC_DESC_AREA_WIDTH + LEFT_PADDING, # Full width for this panel
            SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT,
            (20,20,20,150) # Darker semi-transparent black
        )

        self.ui_elements.draw()
        self.manager.draw() # Draw the UI Manager (for the input text box)

        # Draw text on buttons
        for button in self.ui_elements:
            text_color = arcade.color.WHITE
            if button.properties['action'] == "confirm_selection" and not self.selected_background_key:
                text_color = arcade.color.GRAY # Dim text if confirm is not active
            
            arcade.draw_text(button.properties['text'], button.center_x, button.center_y,
                             text_color, font_size=BUTTON_FONT_SIZE, anchor_x="center", anchor_y="center",
                             width=int(button.width - 2 * MENU_BUTTON_TEXT_PADDING))

        # Draw selected background description and stats
        if self.selected_background_key:
            # Adjust starting Y for description to be below the name input box
            # Description panel starts at its own Y offset, independent of name input now
            desc_y = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET

            arcade.draw_text(f"Background: {self.selected_background_key}",
                             CC_DESC_AREA_X, desc_y, arcade.color.GOLD, font_size=18, bold=True, anchor_y="top",
                             width=CC_DESC_AREA_WIDTH)
            desc_y -= 30
            
            # Wrap and draw description
            # Adjusted width calculation for text wrapping to be more robust
            char_width_estimate = TEXT_AREA_FONT_SIZE * 0.6 # A common estimate for average char width
            wrap_width_chars = int(CC_DESC_AREA_WIDTH / char_width_estimate) if char_width_estimate > 0 else 50

            wrapped_description = textwrap.wrap(BACKGROUNDS_DATA[self.selected_background_key]["description"], width=wrap_width_chars)
            for line in wrapped_description:
                arcade.draw_text(line, CC_DESC_AREA_X, desc_y, arcade.color.WHITE, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top", width=CC_DESC_AREA_WIDTH)
                desc_y -= TEXT_AREA_LINE_HEIGHT
            
            desc_y -= TEXT_AREA_LINE_HEIGHT # Extra space
            wrapped_details = textwrap.wrap(BACKGROUNDS_DATA[self.selected_background_key]["details"], width=wrap_width_chars)
            for line in wrapped_details:
                arcade.draw_text(line, CC_DESC_AREA_X, desc_y, arcade.color.LIGHT_GRAY, font_size=TEXT_AREA_FONT_SIZE, anchor_y="top", width=CC_DESC_AREA_WIDTH)
                desc_y -= TEXT_AREA_LINE_HEIGHT

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        clicked = arcade.get_sprites_at_point((x, y), self.ui_elements)
        if clicked:
            action = clicked[0].properties['action']
            if action.startswith("select_bg_"):
                self.selected_background_key = action.replace("select_bg_", "")
                if self.selected_background_key in BACKGROUNDS_DATA: # Ensure key exists
                    self.selected_background_details = BACKGROUNDS_DATA[self.selected_background_key]["details"]
                self._setup_ui() # Refresh UI to update confirm button color
            elif action == "confirm_selection":
                if self.selected_background_key:
                    character_name = "Adventurer" # Default name since input box is removed
                    print(f"--- Character '{character_name}' with background '{self.selected_background_key}' confirmed! ---")
                    game_world = World()
                    chosen_stats = BACKGROUNDS_DATA[self.selected_background_key]["stats"]
                    game_world.create_character(name=character_name, background_stats=chosen_stats)
                    game_view = GameView(game_world)
                    self.window.show_view(game_view)
                else:
                    print("No background selected.") # Should not happen if button is disabled visually
            elif action == "back_to_menu":
                self.manager.disable() # Disable UI manager when leaving view
                self.window.show_view(self.previous_view)

    def on_hide_view(self):
        self.manager.disable() # Important to disable UIManager