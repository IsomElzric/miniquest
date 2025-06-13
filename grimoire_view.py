import logging
import arcade
import textwrap # For wrapping text into lines

# Import constants
from constants import *
# Note: World and other views are not directly instantiated here, so not imported.

logging.getLogger('arcade').setLevel(logging.INFO)


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
