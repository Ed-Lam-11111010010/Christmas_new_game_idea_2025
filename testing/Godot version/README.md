# City Rogue - Godot 4.4.1 Version

This is the Godot port of the City Rogue game, originally developed in Python with Pygame.

## Project Structure

```
Godot version/
├── project.godot          # Main project configuration
├── icon.svg              # Project icon
├── scenes/
│   └── main.tscn         # Main game scene
├── scripts/
│   ├── consts.gd         # Game constants and enums
│   ├── game.gd           # Main game logic
│   ├── build_manager.gd  # Building placement and management
│   └── event_log_manager.gd  # Event log system
├── data/
│   └── game_data.json    # Buildings, relics, events, and milestones data
└── sfx/                  # Sound effects folder (from Python version)
```

## How to Open in Godot

1. **Open Godot 4.4.1**
2. Click "Import" on the project manager
3. Navigate to the `Godot version` folder
4. Select the `project.godot` file
5. Click "Import & Edit"

## Key Differences from Pygame Version

### Architecture Changes

1. **Rendering System**
   - Pygame used surface blitting → Godot uses `_draw()` method
   - Custom fonts → Godot's built-in font system (ThemeDB.fallback_font)
   - Manual pixel coordinates → Godot's coordinate system

2. **Input Handling**
   - Pygame event loop → Godot's `_input()` and `_process()` callbacks
   - Manual mouse button state → Godot's `InputEventMouseButton`
   - Key events → Godot's `InputEventKey`

3. **File System**
   - Python's `os.path` → Godot's `FileAccess` and `DirAccess`
   - JSON loading → Godot's `JSON.parse()`
   - Save files stored in `user://` (platform-specific user data folder)

4. **Audio**
   - Pygame mixer → Godot's AudioStreamPlayer (placeholder - needs implementation)

### GDScript vs Python

- **Class Syntax**: Python classes → GDScript `class_name` and `extends`
- **Type Hints**: Python type hints → GDScript native typing (`: int`, `: String`, etc.)
- **Dictionaries**: Python dicts → GDScript Dictionary with `.has()`, `.get()`, `.erase()`
- **Lists**: Python lists → GDScript Array with `.append()`, `.size()`, `.clear()`
- **String Formatting**: Python f-strings → GDScript `%` operator or `str()`

## What Needs to Be Completed

### 1. Audio System
The sound system is currently a placeholder. You need to:
- Add `AudioStreamPlayer` nodes for each sound effect
- Load `.wav` files from the `sfx/` folder
- Implement the `load_sounds()` and `play_sound()` functions

### 2. UI Improvements
Current UI is drawn programmatically using `_draw()`. For better performance and ease:
- Consider creating dedicated UI scenes with Control nodes
- Add proper buttons with signals
- Implement better text rendering with Label nodes

### 3. Button Click Detection
The click handling functions (handle_menu_click, handle_relic_click, etc.) have placeholders.
You need to implement proper rect collision detection or use Godot's Button nodes.

### 4. Visual Polish
- Add textures/sprites for buildings instead of colored rectangles
- Implement better grid rendering
- Add animations for building placement
- Create visual effects for events

### 5. Mobile Support (Optional)
- Add touch controls
- Adjust UI for different screen sizes
- Implement pinch-to-zoom

## Running the Game

1. Press F5 or click the "Play" button in Godot
2. The game should start at the main menu
3. Use the keyboard and mouse controls:
   - **1-9**: Select buildings
   - **Space**: End turn
   - **Escape**: Return to menu
   - **Right-click + drag**: Pan camera
   - **Mouse wheel**: Zoom in/out

## Known Issues / TODOs

- [ ] Implement audio system with AudioStreamPlayer
- [ ] Add proper button click detection
- [ ] Improve rendering performance (use TileMap for grid)
- [ ] Add visual feedback for building placement
- [ ] Implement proper popup dialogs with Control nodes
- [ ] Add particle effects for events
- [ ] Create better fonts and UI styling
- [ ] Optimize large grid rendering
- [ ] Add save/load error handling
- [ ] Test on different screen resolutions

## Tips for Further Development

1. **Use TileMap**: Consider using Godot's TileMap node for the grid instead of drawing each tile manually
2. **Autoload**: Make `Consts` an autoload singleton for easier access
3. **Signals**: Use Godot signals for event communication between nodes
4. **Resource Files**: Convert buildings data to Godot Resources for better editor integration
5. **Shaders**: Add shaders for visual effects (water animation, building highlights)

## Credits

Original Python/Pygame version by [Your Name]
Godot port created: January 2026

## Version

Godot: 4.4.1  
Game Version: 3.13
