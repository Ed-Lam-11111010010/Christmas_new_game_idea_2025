# Implementation Checklist

Use this checklist to track completion of the Godot port.

## ✅ Core Conversion (COMPLETE)

- [x] Project structure created
- [x] Constants converted (consts.gd)
- [x] Main game logic converted (game.gd)
- [x] BuildManager converted (build_manager.gd)
- [x] EventLogManager converted (event_log_manager.gd)
- [x] Game data JSON copied
- [x] Main scene created (main.tscn)
- [x] Save/load system implemented
- [x] Input handling implemented
- [x] Camera system (pan/zoom) implemented
- [x] All game states (menu, relic, game, settings, gameover)

## 🔊 Audio Implementation (TODO)

### Setup
- [ ] Create `AudioStreamPlayer` nodes in main scene:
  - [ ] BuildSound
  - [ ] MoneySound
  - [ ] SelectSound
  - [ ] ErrorSound

### Audio Files
- [ ] Copy .wav files from Python version's `sfx/` folder to Godot's `sfx/` folder
- [ ] Assign audio streams to AudioStreamPlayer nodes in editor

### Code Updates
- [ ] Implement `load_sounds()` function in game.gd:
  ```gdscript
  func load_sounds():
      $BuildSound.stream = load("res://sfx/build.wav")
      $MoneySound.stream = load("res://sfx/money.wav")
      $SelectSound.stream = load("res://sfx/select.wav")
      $ErrorSound.stream = load("res://sfx/error.wav")
  ```

- [ ] Implement `play_sound()` function in game.gd:
  ```gdscript
  func play_sound(sound_name: String):
      match sound_name:
          "build": $BuildSound.play()
          "money": $MoneySound.play()
          "select": $SelectSound.play()
          "error": $ErrorSound.play()
  ```

- [ ] Set volume levels:
  ```gdscript
  func update_volume():
      $BuildSound.volume_db = linear_to_db(volume)
      $MoneySound.volume_db = linear_to_db(volume)
      $SelectSound.volume_db = linear_to_db(volume)
      $ErrorSound.volume_db = linear_to_db(volume)
  ```

## 🎨 UI Improvements (TODO)

### Menu Screen
- [ ] Create proper Button nodes for menu options
- [ ] Connect button signals to functions
- [ ] Add hover effects

### Relic Screen
- [ ] Create Button/Panel nodes for relic selection
- [ ] Add hover previews
- [ ] Connect signals

### Game UI
- [ ] Create sidebar UI scene (ui_sidebar.tscn)
  - [ ] Stats panel
  - [ ] Building selection grid
  - [ ] Next turn button
  - [ ] Event log panel

- [ ] Create popup dialog scene (ui_popup.tscn)
  - [ ] Building info popup
  - [ ] Upgrade/sell buttons
  - [ ] Event popup

- [ ] Connect UI signals to game logic

### Settings Screen
- [ ] Create proper UI controls:
  - [ ] Difficulty OptionButton
  - [ ] Resolution OptionButton
  - [ ] Volume HSlider
  - [ ] Back Button

## 🎮 Button Click Detection (TODO)

Currently using basic rect collision. Should implement proper UI:

### Menu Buttons
- [ ] Replace rect collision with Button nodes
- [ ] Connect signals:
  ```gdscript
  func _on_new_game_pressed():
      reset_game_data()
      state = Consts.GameState.RELIC
  
  func _on_load_game_pressed():
      load_game_from_file()
  
  func _on_settings_pressed():
      state = Consts.GameState.SETTINGS
  
  func _on_quit_pressed():
      get_tree().quit()
  ```

### Relic Selection
- [ ] Create Button nodes for each relic
- [ ] Add dynamic button creation based on relics array
- [ ] Connect to selection logic

### Settings Buttons
- [ ] Implement proper controls
- [ ] Add signal connections
- [ ] Update settings in real-time

## 🖼️ Visual Enhancements (TODO)

### Graphics
- [ ] Create/import building sprites
- [ ] Replace colored rectangles with sprites
- [ ] Add terrain textures
- [ ] Design UI theme

### Fonts
- [ ] Import custom fonts
- [ ] Create Theme resource
- [ ] Apply to all text

### Animations
- [ ] Building placement animation (scale/fade in)
- [ ] Demolition animation (fade out/particles)
- [ ] Money change animation (floating text)
- [ ] Turn transition animation

### Particles
- [ ] Building construction particles
- [ ] Event notification particles
- [ ] Money gain/loss particles
- [ ] Upgrade effect particles

### Shaders
- [ ] Water animation shader for rivers
- [ ] Building highlight shader
- [ ] Grid glow shader for valid placement

## 🔧 Code Improvements (TODO)

### Performance
- [ ] Replace `_draw()` grid with TileMap node
  - Create tileset
  - Convert grid array to tilemap
  - Update placement logic

- [ ] Cache frequently used values
- [ ] Optimize building iteration loops

### Architecture
- [ ] Make Consts an autoload singleton
- [ ] Separate UI into dedicated scenes
- [ ] Use signals for event communication

### Error Handling
- [ ] Add try/catch for file operations
- [ ] Handle missing save files gracefully
- [ ] Validate JSON data on load

## 📱 Platform Support (TODO)

### Desktop
- [ ] Test on Windows
- [ ] Test on Linux
- [ ] Test on macOS

### Mobile (Optional)
- [ ] Add touch controls
- [ ] Implement virtual buttons
- [ ] Add pinch-to-zoom
- [ ] Optimize for mobile screens

### Export
- [ ] Configure export presets
- [ ] Test exported builds
- [ ] Create installers

## 🧪 Testing Checklist

### Core Gameplay
- [ ] New game starts correctly
- [ ] Building placement works
- [ ] Buildings can be upgraded
- [ ] Buildings can be demolished
- [ ] Resources calculate correctly
- [ ] Turn progression works
- [ ] Events trigger properly
- [ ] Milestones unlock correctly
- [ ] Win/loss conditions work

### Save/Load
- [ ] Game saves on turn end
- [ ] Game loads correctly
- [ ] All state is preserved
- [ ] High scores save/load
- [ ] Settings save/load

### UI
- [ ] All buttons respond
- [ ] All screens display correctly
- [ ] Camera controls work
- [ ] Zoom works
- [ ] Popups display correctly

### Edge Cases
- [ ] Can't place building off-grid
- [ ] Can't place building on water (except bridge)
- [ ] Can't afford expensive buildings
- [ ] Out of action points
- [ ] Game over at round 20
- [ ] Game over at $0

## 📚 Documentation (TODO)

- [ ] Add inline code comments
- [ ] Create GDScript documentation comments
- [ ] Update README with screenshots
- [ ] Create video tutorial
- [ ] Write developer guide

## 🚀 Release Preparation (TODO)

- [ ] Version number in project settings
- [ ] Create changelog
- [ ] Add license file
- [ ] Create itch.io page
- [ ] Prepare promotional materials
- [ ] Test on fresh Godot install
- [ ] Create export templates
- [ ] Build final executables

## 🎯 Priority Order

1. **Audio** - Quick win, adds a lot to feel
2. **Button Click Detection** - Essential for usability
3. **Visual Polish** - Makes it look professional
4. **Code Refactoring** - Long-term maintainability
5. **Platform Support** - Expand audience
6. **Extra Features** - Nice to have

---

## Current Status Summary

**Completed**: 15/15 Core Conversion Tasks (100%)  
**Remaining**: 60+ Enhancement Tasks

**Next Immediate Steps**:
1. Copy sound files to sfx/ folder
2. Add AudioStreamPlayer nodes
3. Implement sound playback
4. Test the game!

**Estimated Time to Production-Ready**:
- With audio only: 1-2 hours
- With UI improvements: 4-8 hours  
- With full polish: 20-40 hours

---

**Last Updated**: January 3, 2026  
**Current Phase**: Core Complete, Enhancement Needed
