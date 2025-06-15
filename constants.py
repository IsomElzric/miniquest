# constants.py
import arcade.color
import os

# --- Screen & Layout Constants ---
GAME_AREA_WIDTH = 512  # The fixed width for game art
MENU_PANEL_WIDTH = 240  # Width for the right-hand menu
SCREEN_WIDTH = GAME_AREA_WIDTH + MENU_PANEL_WIDTH  # Total screen width
SCREEN_HEIGHT = 600  # Adjusted height to accommodate banner and buttons better
SCREEN_TITLE = "Miniquest"

PLAYER_INFO_BANNER_HEIGHT = 80  # Height for the top player info banner
TOP_PADDING = 0  # Padding from the bottom of banner for text-based views
ICON_PANEL_TOP_MARGIN = 5 # Padding from the bottom of banner for icon-based views
LEFT_PADDING = 10  # Padding from the left of the main game area for text
RIGHT_MENU_X_START = GAME_AREA_WIDTH  # X-coordinate where the right menu begins

# --- Path Constants ---
# Determine the absolute path to the 'miniquest' package directory (where __main__.py and constants.py reside)
# os.path.dirname(__file__) is '.../miniquest' (this is the package root)
PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PACKAGE_ROOT_DIR, 'assets')
ART_BASE_PATH = os.path.join(ASSETS_DIR, "art")  # Base path for all art

UI_ART_PATH = os.path.join(ART_BASE_PATH, "ui")
LOCATION_ART_PATH = os.path.join(ART_BASE_PATH, "location")
ITEM_ICON_ART_PATH = os.path.join(ART_BASE_PATH, "item_icons")
ENEMY_ASSET_PATH = os.path.join(ASSETS_DIR, 'enemies') # Path for enemy definition files (used by builder)
ITEM_ASSET_PATH = os.path.join(ASSETS_DIR, 'items') # Path for item definition files (used by builder)
GRIMOIRE_ASSET_PATH = os.path.join(ASSETS_DIR, 'grimoire_entries') # Path for grimoire entry files (used by builder)
LOCATION_ASSET_PATH = os.path.join(ASSETS_DIR, 'locations') # Path for location definition files (used by builder)

# --- Image File Paths ---
BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_title.jpg")
PLACEHOLDER_ART = os.path.join(LOCATION_ART_PATH, "placeholder.jpg")

TOP_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_menu.png")
GAME_VIEW_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_game.png")
MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png")
INVENTORY_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_inventory.jpg")
GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png") # Assuming same as menu for now
MENU_BUTTON_IMAGE_PATH = os.path.join(UI_ART_PATH, "menu_button.png")
CC_LEFT_PANEL_BUTTON_AREA_BG_IMAGE = os.path.join(UI_ART_PATH, "cc_left_panel_button_area_bg.png") # New
CHARACTER_ART_PATH = os.path.join(ART_BASE_PATH, "character_backgrounds") # New
INPUT_BOX_BACKGROUND_IMAGE_PATH = os.path.join(UI_ART_PATH, "input_box_background.png") # New for input box
INPUT_BOX_BACKGROUND_PADDING = 25 # Pixels to add to each side of the input box for its background sprite
DEFAULT_CHARACTER_ART_IMAGE = os.path.join(CHARACTER_ART_PATH, "default_char_art.png") # New default art

# --- UI Element Constants ---
# General Button properties (for the main menu, can be adapted)
BUTTON_WIDTH = 150 # Generic button width, can be overridden
BUTTON_HEIGHT = 50 # Generic button height, can be overridden
BUTTON_COLOR_TRANSLUCENT = (arcade.color.DARK_BLUE[0], arcade.color.DARK_BLUE[1], arcade.color.DARK_BLUE[2], 120)
BUTTON_HOVER_COLOR = arcade.color.BLUE
BUTTON_TEXT_COLOR = arcade.color.WHITE
BUTTON_FONT_SIZE = 18 # Generic button font size

# Menu Buttons (Sprite-based, for side panels)
MENU_BUTTON_TARGET_WIDTH = MENU_PANEL_WIDTH - 30
MENU_BUTTON_HEIGHT = 40 # Specific height for these buttons
MENU_BUTTON_VERTICAL_SPACING = 8
MENU_BUTTON_TEXT_COLOR = arcade.color.WHITE # Added this line, can be same as BUTTON_TEXT_COLOR or different
MENU_BUTTON_TEXT_PADDING = 10
MENU_ACTIONS_TITLE_FONT_SIZE = 24
MENU_PADDING_BELOW_TITLE = 15

# Text Area Constants
TEXT_AREA_LINE_HEIGHT = 22
TEXT_AREA_FONT_SIZE = 12
LOG_AREA_FONT_SIZE = 12
LOG_AREA_TEXT_BOX_HEIGHT = 150 # Set default height for Log messages in crafting

# Item Icon Display Constants
ITEM_ICON_DRAW_SIZE = (32, 32)
ITEM_ICON_VERTICAL_SPACING = 10
ITEM_TEXT_OFFSET_X = ITEM_ICON_DRAW_SIZE[0] + 10
ITEM_SECTION_SPACING = 20

# Character Creation View Constants
CC_BACKGROUND_BUTTON_WIDTH = MENU_PANEL_WIDTH - 80 # Revert to 160px width (240 - 80)
CC_BACKGROUND_BUTTON_HEIGHT = 40
CC_BACKGROUND_BUTTON_SPACING = 15
CC_DESC_AREA_X = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH # Remove the +30 spacing
CC_DESC_AREA_Y_START_OFFSET = 50
CC_DESC_AREA_WIDTH = GAME_AREA_WIDTH - CC_DESC_AREA_X - LEFT_PADDING # This will expand as CC_DESC_AREA_X shifts left
CC_NAME_INPUT_WIDTH = CC_BACKGROUND_BUTTON_WIDTH - 20 # Name input width will also reduce
CC_NAME_INPUT_HEIGHT = 40
CC_DESC_AREA_HEIGHT = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET - BUTTON_HEIGHT - 20
CC_DESC_TEXT_PADDING = 10 # Padding inside the description text area

# Character Creation View - Character Art Area
CC_CHAR_ART_Y_START_OFFSET = 10 # Reduced: Space below buttons before art starts
CC_CHAR_ART_BOTTOM_PADDING = 10 # Reduced: Space from bottom of panel to bottom of art
CC_CHAR_ART_WIDTH = CC_BACKGROUND_BUTTON_WIDTH # Art width same as buttons