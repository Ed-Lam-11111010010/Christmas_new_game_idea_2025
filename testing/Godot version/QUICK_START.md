# City Rogue - Godot Quick Start Guide

## 🎮 Getting Started

### Step 1: Open the Project
1. Launch **Godot 4.4.1**
2. Click **"Import"** in the Project Manager
3. Browse to: `d:\Docs\GitHub\Christmas_new_game_idea_2025\testing\Godot version\`
4. Select `project.godot`
5. Click **"Import & Edit"**

### Step 2: First Run
1. Press **F5** or click the ▶️ **Play** button
2. The game should start at the main menu
3. If you see errors, check the **Output** panel at the bottom

## 🎯 Current Status

### ✅ What Works
- **Game Data**: All buildings, relics, events loaded from JSON
- **Core Logic**: Building placement, upgrades, demolition
- **Turn System**: Round progression, income calculation
- **Stats**: Population, happiness, energy tracking
- **Save/Load**: Game state persistence
- **Neighbor Synergies**: Combo bonuses for adjacent buildings
- **Events**: Random events every 5 rounds
- **Milestones**: Achievement system

### ⚠️ What Needs Work
- **Audio**: Sound effects are placeholders (no actual audio playback)
- **UI Buttons**: Click detection is basic, consider using Godot Control nodes
- **Graphics**: Currently colored rectangles, could use sprites/textures
- **Animations**: No visual effects yet
- **Polish**: Needs better fonts, layouts, and visual feedback

## 🕹️ Controls

### Keyboard
- **1-9**: Select building types
  - 1: House
  - 2: Office
  - 3: Power Plant
  - 4: Park
  - 5: Shop
  - 6: Garden
  - 7: Factory
  - 8: Road
  - 9: Bridge
- **Space**: End turn
- **Escape**: Return to menu / Pause

### Mouse
- **Left Click**: 
  - On empty tile: Place selected building
  - On building: Open building menu (upgrade/sell)
- **Right Click + Drag**: Pan camera
- **Mouse Wheel**: Zoom in/out

## 🔧 Next Steps for Development

### Priority 1: Audio System
```gdscript
# Add to the scene tree:
# - AudioStreamPlayer for each sound effect
# Then update play_sound() function:

func play_sound(sound_name: String):
    match sound_name:
        "build":
            $BuildSound.play()
        "money":
            $MoneySound.play()
        # ... etc
```

### Priority 2: Better UI with Control Nodes
Create a new scene `ui.tscn`:
```
CanvasLayer
├── Panel (Sidebar)
│   ├── VBoxContainer
│   │   ├── Label (Stats)
│   │   ├── GridContainer (Building buttons)
│   │   └── Button (Next Turn)
├── Panel (Event Popup)
└── RichTextLabel (Event Log)
```

### Priority 3: Visual Improvements
1. Replace colored rectangles with sprites
2. Add particle effects for building placement
3. Animate water tiles
4. Add building construction animation

## 📁 File Structure Quick Reference

```
Godot version/
├── project.godot                 # Main project config
├── scenes/
│   └── main.tscn                 # Main game scene
├── scripts/
│   ├── consts.gd                 # Constants (Grid size, colors, etc.)
│   ├── game.gd                   # Main game logic (900+ lines)
│   ├── build_manager.gd          # Building placement system
│   └── event_log_manager.gd      # Event logging
├── data/
│   └── game_data.json            # All game content data
└── README.md                     # Full documentation
```

## 🐛 Troubleshooting

### "Cannot open file" errors
- Make sure you imported the project (don't just open Godot in the folder)
- Check that `game_data.json` exists in `data/` folder

### Black screen
- Check Output panel for errors
- Verify `main.tscn` is set as main scene in Project Settings

### Game doesn't respond to input
- Make sure the game window has focus
- Check that `_input()` function isn't disabled

### Save files not working
- Godot saves to platform-specific folders:
  - **Windows**: `%APPDATA%\Godot\app_userdata\City Rogue\`
  - **Linux**: `~/.local/share/godot/app_userdata/City Rogue/`
  - **macOS**: `~/Library/Application Support/Godot/app_userdata/City Rogue/`

## 🎨 Customization Tips

### Change Colors
Edit `scripts/consts.gd`:
```gdscript
const GREEN: Color = Color(0.2, 0.9, 0.2)  # Brighter green
const UI_BG: Color = Color(0.05, 0.05, 0.07)  # Darker background
```

### Adjust Game Balance
Edit `data/game_data.json`:
```json
{
  "buildings": {
    "1": {
      "name": "House",
      "cost": 50,        // Change cost
      "pop": 5,          // Change population
      "happy": -2        // Change happiness impact
    }
  }
}
```

### Add New Buildings
1. Add entry to `data/game_data.json`
2. Use a unique ID number
3. Restart the game to load changes

## 📚 Learning Resources

- **Godot Docs**: https://docs.godotengine.org/en/stable/
- **GDScript Reference**: https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/index.html
- **2D Tutorial**: https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html

## 💡 Pro Tips

1. **Use the Remote Debugger**: Run the game with F5, and you can see variables in real-time
2. **Print Debugging**: Use `print()` statements to debug - output shows in the Output panel
3. **Scene Testing**: Right-click any scene and "Set as Main Scene" to test it independently
4. **Git Integration**: Godot has built-in Git support (Project → Version Control)
5. **Export Templates**: Download export templates to build standalone executables

## 🚀 Next Features to Implement

- [ ] Sound effects with AudioStreamPlayer nodes
- [ ] Better UI with Control nodes and signals
- [ ] Building sprites/textures
- [ ] Particle effects for events
- [ ] Animation for building placement
- [ ] Settings menu (volume, resolution)
- [ ] Tutorial/help screen
- [ ] Different map generation algorithms
- [ ] Multiplayer support (ambitious!)

---

**Need Help?** Check the MIGRATION_GUIDE.md for detailed Python→GDScript conversions!

**Ready to Code?** Open `scripts/game.gd` and start customizing! 🎮
