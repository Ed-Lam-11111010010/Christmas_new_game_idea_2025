# Changelog - City Rogue (Godot Edition)

All notable changes to the Godot version of City Rogue will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.13.1] - 2026-01-05

### 🎉 Initial Godot Port Release
Complete conversion of City Rogue from Python/Pygame to Godot 4.4.1

### ✨ Added
- **Core Game Systems**
  - Full grid-based city building gameplay (20x12 grid)
  - 9 building types: House, Office, Power Plant, Park, Shop, Garden, Factory, Road, Bridge
  - Resource management (Money, Energy, Population, Happiness)
  - Turn-based gameplay with 20 rounds to reach victory
  - Building upgrade system (3 levels per building)
  - Demolish/sell buildings for 50% refund

- **Game Mechanics**
  - Neighbor synergy bonuses (e.g., House + Park = happiness boost)
  - Connectivity requirements (buildings must connect to roads)
  - Dynamic income calculation based on building combinations
  - Population capacity and worker allocation system
  - Energy generation and consumption tracking
  - Happiness calculation with warning system

- **Events & Progression**
  - 4 unique relics with different bonuses (Money/Energy/Happiness/Random)
  - Random events system (weather, inspections, festivals)
  - Milestone achievements (population, building count, happiness targets)
  - High score tracking with persistent save file

- **UI/UX Features**
  - Main menu with New Game, Load Game, Settings, Quit
  - Relic selection screen with 4 distinct choices
  - In-game HUD showing all resources and turn count
  - Building selection sidebar with icons
  - Building popup for upgrade/sell actions
  - Event log system showing last 8 messages
  - Settings menu with difficulty, volume, and resolution controls
  - Game over screen with score summary and restart option

- **Visual Features**
  - Grid-based rendering with zoom and pan controls
  - Building size preview (1x1 or 2x2) with white highlight frame
  - Color-coded buildings by type
  - Emoji-based building icons with proper centering
  - Unified rendering for multi-tile buildings (2x2 shown as single block)
  - 3D depth effects with gradients and shadows
  - Black background for empty land tiles
  - Version number display (v3.13.1 on menu, v3.13 in-game)

- **Camera Controls**
  - Right-click drag to pan camera
  - Mouse wheel zoom (0.5x - 2.0x range)
  - Smooth camera movements
  - Auto-centering on game start

- **Save System**
  - Complete game state persistence
  - Saves: grid, resources, turn count, relic, difficulty
  - Auto-loads settings and high scores
  - Safe file handling with error messages

- **Documentation**
  - Comprehensive README with feature overview
  - Quick Start Guide with controls and troubleshooting
  - Migration Guide (Pygame → Godot conversion reference)
  - Artwork Guide for adding sprites and visual assets
  - Implementation Checklist for future development
  - Conversion Summary with technical details
  - Index for easy documentation navigation

### 🔧 Technical Implementation
- **Architecture**
  - Modular GDScript structure with separate manager classes
  - `game.gd` - Main game logic (~1450 lines)
  - `consts.gd` - Constants, enums, and color definitions
  - `build_manager.gd` - Building placement and validation
  - `event_log_manager.gd` - Message logging system
  - Type-safe GDScript with proper annotations

- **Data Management**
  - JSON-based game data (`game_data.json`)
  - All buildings, events, relics, and milestones externalized
  - Easy modding and balancing without code changes

- **Performance**
  - Efficient draw culling (only visible tiles rendered)
  - Optimized building overlap detection
  - Smart redraw system (queue_redraw() only when needed)

### 🐛 Fixed
- **Load Game Issues**
  - Added file existence check before loading
  - Prevents crashes from missing save files
  - Shows error message: "No save file found!"

- **UI Precision**
  - Fixed Y-axis displacement in building selection buttons
  - Corrected click detection from ~280px to exact 230px
  - Integer division fix for proper row calculation

- **Building Rendering**
  - Fixed emoji positioning (shifted from 0.3 to 0.4 on X-axis)
  - Centered emojis properly on 2x2 buildings
  - Single emoji per building instead of repeating on every tile

- **Settings Navigation**
  - Added ESC key handler to exit settings screen
  - Returns to main menu when ESC pressed
  - Consistent with other screen navigation

- **Building Management**
  - Implemented building popup system (was missing)
  - Upgrade button with cost display and affordability check
  - Sell button showing 50% refund value
  - Close button (X) for popup dismissal
  - Smart popup positioning (stays on screen)

- **Selection Preview**
  - White frame now matches building size (1x1 or 2x2)
  - Dynamic sizing based on selected building type
  - Accurate visual feedback for placement

### 📋 Game Balance
- **Difficulty Modes**
  - Normal: Start with $600
  - Hard: Start with $400
  
- **Building Costs**
  - House: $100, Office: $150, Power: $200, Park: $50
  - Shop: $120, Garden: $30, Factory: $180
  - Road: $20, Bridge: $40

- **Resource Generation**
  - Houses: +2 population per level
  - Offices: +$30 income if staffed
  - Power: +5 energy per level
  - Factories: +$50 income but -2 happiness

- **Victory Conditions**
  - Survive 20 rounds
  - Maintain positive resources
  - Score based on money, population, happiness, buildings

### 🎮 Controls
- **Keyboard**
  - `1-9` - Select building type
  - `Space` - End turn
  - `ESC` - Return to menu / Close popup

- **Mouse**
  - `Left Click` - Place building / Select button / Open popup
  - `Right Click + Drag` - Pan camera
  - `Mouse Wheel` - Zoom in/out

### 📦 Project Structure
```
testing/Godot version/
├── project.godot          # Godot 4.4.1 project file
├── scenes/
│   └── main.tscn          # Main game scene
├── scripts/
│   ├── game.gd            # Core game logic
│   ├── consts.gd          # Constants and enums
│   ├── build_manager.gd   # Building system
│   └── event_log_manager.gd # Event logging
├── data/
│   └── game_data.json     # All game data
└── docs/
    ├── README.md
    ├── CHANGELOG.md
    ├── QUICK_START.md
    ├── MIGRATION_GUIDE.md
    ├── ARTWORK_GUIDE.md
    ├── IMPLEMENTATION_CHECKLIST.md
    ├── CONVERSION_SUMMARY.md
    └── INDEX.md
```

### 🚀 Known Limitations
- Audio system has placeholders (no sound yet)
- Uses emoji icons instead of sprites (ready for artwork)
- UI uses basic drawing (can be upgraded to Control nodes)
- No animations or particle effects yet
- Settings are functional but basic

### 📝 Notes
- 100% gameplay parity with Python version
- All core mechanics tested and working
- Save/load system verified
- Ready for sprite artwork integration
- Foundation for future Godot-specific enhancements

---

## [Planned] - Future Versions

### 🎯 Roadmap
- [ ] Audio system implementation (music, SFX)
- [ ] Sprite-based artwork (isometric buildings)
- [ ] Animation system (building construction, effects)
- [ ] Particle effects (smoke, sparkles, weather)
- [ ] Advanced UI with Control nodes
- [ ] Tutorial system for new players
- [ ] More building types and relics
- [ ] Multiplayer support (future consideration)

---

## Version History

- **v3.13.1** (2026-01-05) - Initial Godot port with all bug fixes
- **v3.13.0** (2025-12-XX) - Python/Pygame original version

---

**Conversion Credits:**
- Original Python Version: [Your Name]
- Godot Port: GitHub Copilot (Claude Sonnet 4.5)
- Platform: Godot Engine 4.4.1
- License: [Your License]

**For more information:**
- See [README.md](README.md) for complete documentation
- See [QUICK_START.md](QUICK_START.md) for getting started
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for technical details