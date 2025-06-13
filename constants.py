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
MENU_BUTTON_TEXT_PADDING = 10
MENU_ACTIONS_TITLE_FONT_SIZE = 24
MENU_PADDING_BELOW_TITLE = 15

# Text Area Constants
TEXT_AREA_LINE_HEIGHT = 22
TEXT_AREA_FONT_SIZE = 12
LOG_AREA_FONT_SIZE = 12

# Item Icon Display Constants
ITEM_ICON_DRAW_SIZE = (32, 32)
ITEM_ICON_VERTICAL_SPACING = 10
ITEM_TEXT_OFFSET_X = ITEM_ICON_DRAW_SIZE[0] + 10
ITEM_SECTION_SPACING = 20

# Character Creation View Constants
CC_BACKGROUND_BUTTON_WIDTH = MENU_PANEL_WIDTH - 40
CC_BACKGROUND_BUTTON_HEIGHT = 60
CC_BACKGROUND_BUTTON_SPACING = 15
CC_DESC_AREA_X = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH + 30
CC_DESC_AREA_Y_START_OFFSET = 50
CC_DESC_AREA_WIDTH = GAME_AREA_WIDTH - CC_DESC_AREA_X - LEFT_PADDING
CC_NAME_INPUT_WIDTH = CC_BACKGROUND_BUTTON_WIDTH - 20
CC_NAME_INPUT_HEIGHT = 40
CC_DESC_AREA_HEIGHT = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET - BUTTON_HEIGHT - 20

# --- Data ---
BACKGROUNDS_DATA = {
    "Warrior": {
        "description": "A hardened warrior, accustomed to the brutal realities of combat. Favors direct confrontation and resilience.",
        "stats": {"attack": 5, "defense": 4, "speed": 2},
        "details": "Starting Stats:\n  Attack: 5\n  Defense: 4\n  Speed: 2\n\nA life of conflict has honed your offensive and defensive capabilities, though agility is not your forte."
    },
    "Rogue": {
        "description": "A nimble rogue, thriving in shadows and striking when least expected. Values speed and precision over raw power.",
        "stats": {"attack": 4, "defense": 2, "speed": 5},
        "details": "Starting Stats:\n  Attack: 4\n  Defense: 2\n  Speed: 5\n\nQuick reflexes and a keen eye for weakness allow you to outmaneuver foes and strike with deadly accuracy."
    },
    "Scholar": {
        "description": "A studious scholar, whose knowledge of the old world might offer an edge. Relies on intellect more than brawn.",
        "stats": {"attack": 3, "defense": 3, "speed": 3},
        "details": "Starting Stats:\n  Attack: 3\n  Defense: 3\n  Speed: 3\n\nWhile not a natural fighter, your understanding of lore and tactics provides a balanced approach to survival."
    },
    "Survivor": {
        "description": "A resilient survivor, hardened by adversity and possessing an unyielding will to live. Endurance is your greatest asset.",
        "stats": {"attack": 3, "defense": 5, "speed": 2},
        "details": "Starting Stats:\n  Attack: 3\n  Defense: 5\n  Speed: 2\n\nYou've weathered countless storms and learned to endure. Your toughness allows you to withstand more punishment."
    }
}

# --- Constants ---
GAME_AREA_WIDTH = 512  # The fixed width for game art
MENU_PANEL_WIDTH = 240  # Width for the right-hand menu
SCREEN_WIDTH = GAME_AREA_WIDTH + MENU_PANEL_WIDTH  # Total screen width
SCREEN_HEIGHT = 600  # Adjusted height to accommodate banner and buttons better
SCREEN_TITLE = "Miniquest"

# Button properties (for the main menu)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_COLOR_TRANSLUCENT = (arcade.color.DARK_BLUE[0], arcade.color.DARK_BLUE[1], arcade.color.DARK_BLUE[2], 120)
BUTTON_HOVER_COLOR = arcade.color.BLUE  # Not currently used for sprite buttons
BUTTON_TEXT_COLOR = arcade.color.WHITE
BUTTON_FONT_SIZE = 18

# --- Game View Constants ---
PLAYER_INFO_BANNER_HEIGHT = 80  # Height for the top player info banner
TOP_PADDING = 0  # Padding from the bottom of banner for text-based views
ICON_PANEL_TOP_MARGIN = 5  # Padding from the bottom of banner for icon-based views
LEFT_PADDING = 10  # Padding from the left of the main game area for text
RIGHT_MENU_X_START = GAME_AREA_WIDTH  # X-coordinate where the right menu begins

# Determine the absolute path to the 'miniquest' package directory (where __main__.py resides)
PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PACKAGE_ROOT_DIR, 'assets')
ART_BASE_PATH = os.path.join(ASSETS_DIR, "art")  # Base path for all art

# New structured art paths
UI_ART_PATH = os.path.join(ART_BASE_PATH, "ui")
LOCATION_ART_PATH = os.path.join(ART_BASE_PATH, "location")
ITEM_ICON_ART_PATH = os.path.join(ART_BASE_PATH, "item_icons")  # For future use when displaying icons

BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_title.jpg")
PLACEHOLDER_ART = os.path.join(LOCATION_ART_PATH, "placeholder.jpg")

TOP_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_menu.png")
GAME_VIEW_BANNER_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_banner_game.png")
MENU_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png")
INVENTORY_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_inventory.jpg")
GAME_VIEW_RIGHT_PANEL_BACKGROUND_IMAGE = os.path.join(UI_ART_PATH, "background_panel_menu.png")

# New constants for scrollable text areas
TEXT_AREA_LINE_HEIGHT = 22  # Pixel height for each line of text, including some padding - INCREASED
TEXT_AREA_FONT_SIZE = 12  # Font size for area descriptions - REMAINS 12
LOG_AREA_FONT_SIZE = 12  # Font size for combat/event logs

# New constants for menu buttons with images
MENU_BUTTON_IMAGE_PATH = os.path.join(UI_ART_PATH, "menu_button.png")
MENU_BUTTON_TARGET_WIDTH = MENU_PANEL_WIDTH - 30  # Target width: Panel width minus 15px padding on each side
MENU_BUTTON_HEIGHT = 40  # Further reduced height to make them less "dramatic"
MENU_BUTTON_TEXT_COLOR = arcade.color.WHITE
MENU_BUTTON_VERTICAL_SPACING = 8  # Significantly increased space between buttons
MENU_BUTTON_TEXT_PADDING = 10  # Padding for text inside the button (e.g., 5px on each side for centering)
MENU_ACTIONS_TITLE_FONT_SIZE = 24  # Font size of the "Actions" title
MENU_PADDING_BELOW_TITLE = 15  # Padding between the "Actions" title and the first button

# --- Item Icon Display Constants ---
ITEM_ICON_DRAW_SIZE = (32, 32)  # The size to draw icons on screen
ITEM_ICON_VERTICAL_SPACING = 10  # Space between item rows (icon + text)
ITEM_TEXT_OFFSET_X = ITEM_ICON_DRAW_SIZE[0] + 10  # Horizontal offset for text next to icon
ITEM_SECTION_SPACING = 20  # Vertical space between "Equipped", "Carried", "Strongbox" sections

# Character Creation View Constants
CC_BACKGROUND_BUTTON_WIDTH = MENU_PANEL_WIDTH - 40  # Slightly narrower than menu buttons
CC_BACKGROUND_BUTTON_HEIGHT = 60
CC_BACKGROUND_BUTTON_SPACING = 15
CC_DESC_AREA_X = LEFT_PADDING + CC_BACKGROUND_BUTTON_WIDTH + 30  # To the right of background buttons
CC_DESC_AREA_Y_START_OFFSET = 50  # From top of content area
CC_DESC_AREA_WIDTH = GAME_AREA_WIDTH - CC_DESC_AREA_X - LEFT_PADDING
CC_NAME_INPUT_WIDTH = CC_BACKGROUND_BUTTON_WIDTH - 20  # Adjusted width for left panel
CC_NAME_INPUT_HEIGHT = 40
CC_DESC_AREA_HEIGHT = SCREEN_HEIGHT - PLAYER_INFO_BANNER_HEIGHT - CC_DESC_AREA_Y_START_OFFSET - BUTTON_HEIGHT - 20  # Space for confirm/back

BACKGROUNDS_DATA = {
    "Warrior": {
        "description": "A hardened warrior, accustomed to the brutal realities of combat. Favors direct confrontation and resilience.",
        "stats": {"attack": 5, "defense": 4, "speed": 2},
        "details": "Starting Stats:\n  Attack: 5\n  Defense: 4\n  Speed: 2\n\nA life of conflict has honed your offensive and defensive capabilities, though agility is not your forte."
    },
    "Rogue": {
        "description": "A nimble rogue, thriving in shadows and striking when least expected. Values speed and precision over raw power.",
        "stats": {"attack": 4, "defense": 2, "speed": 5},
        "details": "Starting Stats:\n  Attack: 4\n  Defense: 2\n  Speed: 5\n\nQuick reflexes and a keen eye for weakness allow you to outmaneuver foes and strike with deadly accuracy."
    },
    "Scholar": {
        "description": "A studious scholar, whose knowledge of the old world might offer an edge. Relies on intellect more than brawn.",
        "stats": {"attack": 3, "defense": 3, "speed": 3},
        "details": "Starting Stats:\n  Attack: 3\n  Defense: 3\n  Speed: 3\n\nWhile not a natural fighter, your understanding of lore and tactics provides a balanced approach to survival."
    },
    "Survivor": {
        "description": "A resilient survivor, hardened by adversity and possessing an unyielding will to live. Endurance is your greatest asset.",
        "stats": {"attack": 3, "defense": 5, "speed": 2},
        "details": "Starting Stats:\n  Attack: 3\n  Defense: 5\n  Speed: 2\n\nYou've weathered countless storms and learned to endure. Your toughness allows you to withstand more punishment."
    }
}