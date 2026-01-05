import pygame
import os

# --- Get script directory for reliable file paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Configuration ---
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 640
GRID_SIZE = 30
TILE_SIZE = 40
MAX_ROUNDS = 20

# --- File Paths ---
SAVE_FILE = os.path.join(SCRIPT_DIR, "city_rogue_save.json")
SCORE_FILE = os.path.join(SCRIPT_DIR, "city_rogue_scores.json")
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "city_rogue_settings.json")
DATA_FILE = os.path.join(SCRIPT_DIR, "game_data.json")
SFX_DIR = os.path.join(SCRIPT_DIR, "sfx")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
UI_BG = (30, 30, 35)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (220, 220, 50)
PINK = (220, 100, 180)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 200)
ORANGE = (220, 140, 30)
GOLD = (255, 215, 0)
RIVER_BLUE = (60, 100, 200)
ROAD_ACTIVE = (220, 220, 220)
ROAD_INACTIVE = (80, 80, 80)
BRIDGE_COL = (139, 69, 19)

# --- States ---
STATE_MENU = 0
STATE_RELIC = 1
STATE_GAME = 2
STATE_SETTINGS = 3
STATE_GAMEOVER = 4