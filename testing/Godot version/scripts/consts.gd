extends Node
## Global constants for City Rogue game

# Grid and Display Configuration
const GRID_SIZE: int = 30
const TILE_SIZE: int = 40
const MAX_ROUNDS: int = 20

# File Paths
const SAVE_FILE: String = "user://city_rogue_save.json"
const SCORE_FILE: String = "user://city_rogue_scores.json"
const SETTINGS_FILE: String = "user://city_rogue_settings.json"
const DATA_FILE: String = "res://data/game_data.json"

# Colors
const WHITE: Color = Color(1.0, 1.0, 1.0)
const BLACK: Color = Color(0.0, 0.0, 0.0)
const GRAY: Color = Color(0.78, 0.78, 0.78)
const DARK_GRAY: Color = Color(0.16, 0.16, 0.16)
const UI_BG: Color = Color(0.12, 0.12, 0.14)
const RED: Color = Color(0.86, 0.2, 0.2)
const GREEN: Color = Color(0.2, 0.78, 0.2)
const BLUE: Color = Color(0.2, 0.39, 0.86)
const YELLOW: Color = Color(0.86, 0.86, 0.2)
const PINK: Color = Color(0.86, 0.39, 0.71)
const PURPLE: Color = Color(0.59, 0.2, 0.78)
const CYAN: Color = Color(0.2, 0.78, 0.78)
const ORANGE: Color = Color(0.86, 0.55, 0.12)
const GOLD: Color = Color(1.0, 0.84, 0.0)
const RIVER_BLUE: Color = Color(0.24, 0.39, 0.78)
const ROAD_ACTIVE: Color = Color(0.86, 0.86, 0.86)
const ROAD_INACTIVE: Color = Color(0.31, 0.31, 0.31)
const BRIDGE_COL: Color = Color(0.55, 0.27, 0.07)

# Game States
enum GameState {
	MENU,
	RELIC,
	GAME,
	SETTINGS,
	GAMEOVER
}
