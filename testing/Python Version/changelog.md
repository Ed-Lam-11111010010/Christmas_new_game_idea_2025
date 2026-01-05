# 📜 City Rogue - Changelog

All notable changes to the "City Rogue" project will be documented in this file.

## [v3.13] - 2026-01-02
### **The "Modular Architecture & Data-Driven Synergies" Update**
This update restructures the codebase into specialized modules for better maintainability and makes neighbor synergies fully data-driven.

### **🏗️ Code Architecture**
* **New Module: `event_log_manager.py`**
    * Extracted all event logging functionality into a dedicated `EventLogManager` class
    * Handles log scrolling, visibility, and save/load operations
    * Clean API: `log()`, `handle_scroll()`, `get_visible_logs()`, `clear()`, `load_logs()`
* **New Module: `build_manager.py`**
    * Extracted all building operations into a dedicated `BuildManager` class
    * Manages placement, upgrades, demolition, and neighbor bonus calculations
    * Centralized building logic: `can_place_building()`, `build()`, `upgrade_building()`, `demolish_building()`
* **Refactored `city_rogue.py`:**
    * Main game file now delegates to specialized managers
    * Cleaner, more maintainable code structure
    * Reduced code duplication

### **🎮 Data-Driven Neighbor Synergies**
* **New JSON Section in `game_data.json`: `neighbor_synergies`**
    * All neighbor synergy rules are now defined in JSON format
    * Each synergy has: `id`, `name`, `desc`, `building_ids`, `neighbor_ids`, `bonus`
    * Easy to add new synergies without touching code
* **Synergies are now configurable:**
    ```json
    {
      "id": "shop_residential",
      "name": "Shop + Residential Synergy",
      "desc": "Shops and Malls gain +15 income near Houses/Apartments",
      "building_ids": [6, 11],
      "neighbor_ids": [1, 5],
      "bonus": {"money": 15}
    }
    ```
* **Modding Support:** Players/modders can easily customize or add new synergies by editing the JSON file

### **🔧 Technical Improvements**
* **Separation of Concerns:** Each system (logging, building, rendering) is now isolated
* **Testability:** Managers can be tested independently
* **Extensibility:** Much easier to add new features without touching core game logic
* **Maintainability:** Bug fixes are now easier to locate and implement
* **Code Reusability:** Managers can potentially be reused in other projects

### **📝 Documentation**
* Added comprehensive `REFACTORING_SUMMARY.md` documenting all architectural changes
* Detailed explanation of how to add new neighbor synergies via JSON

---

## [v3.12] - 2026-01-01
### **The "Neighbor Synergy & Balance" Update**
This update introduces persistent neighbor bonuses, park upgrades for better happiness balance, and improved economic systems.

### **🎮 Gameplay Improvements**
* **Persistent Neighbor Bonuses:** Neighbor effects now persist after building upgrades! When you upgrade a building (e.g., House → Apartment, Shop → Mall), all neighbor bonuses are preserved and stack with new bonuses.
* **New Neighbor Combinations:**
    * 🏢 **Office + Shop/Mall:** +10💰 income bonus
    * 🏭 **Factory + Power Plant:** +20💰 income bonus (industrial synergy!)
    * 🌳 **Park + House/Apartment:** +5😊 happiness bonus
* **Park Upgrades:** Added upgrade paths to help balance happiness:
    * 🌳 **Park → 🌲 Enhanced Park** ($120): Provides 18 happiness + 1 job
    * 🌻 **Garden → 🌺 Botanical Garden** ($80): Provides 10 happiness + 1 job + $5 income

### **💰 Economic Balance**
* **Improved Selling System:** Selling buildings now correctly returns 50% of total invested value (base cost + all upgrade costs in the chain).
* **Building Values:** Upgraded buildings now properly track their full investment cost for more accurate refunds.

### **🎨 UI Enhancements**
* **Repositioned Leaderboard:** Moved the ranking board lower on the menu screen to align with the start game buttons for better visual balance.
* **Enhanced Preview:** Building placement preview now shows all applicable neighbor bonuses before you build.

### **🔧 Technical Changes**
* **Neighbor Bonus Tracking System:** Implemented persistent storage for neighbor effects across save/load and upgrades.
* **Cost Calculation:** Added comprehensive total cost tracking that follows upgrade chains.

---

## [v3.9.1] - 2025-12-29 (End of Night Build)
### **The "Refactor & Polish" Update**
This update focuses on code stability, input precision, and user interface logic.

### **🔧 Code Structure**
* **Refactoring:** Moved all constants, file paths, and color definitions to a separate file (`consts.py`) to declutter the main logic.
* **Input Handling:** Fixed a critical bug where buildings would "auto-place" when clicking UI elements. Map clicks are now strictly separated from UI interactions.

### **✨ UI & Controls**
* **Selection Bar Cleanup:** Removed upgrade-only buildings (Apartments, Malls) from the construction sidebar. These can now only be accessed by upgrading Houses and Shops.
* **Key Bindings:**
    * **Keys 1-7:** Select Buildings (House, Office, Power, Park, Shop, Garden, Factory).
    * **Keys 8-9:** Select Infrastructure (Bridge, Road).
* **Audio Feedback:** Pressing number keys now plays the selection sound effect.

### **🐛 Bug Fixes**
* **Relic Logic:** Fixed the "City Planner" relic to ensure the starting layout (Roads + Houses) is recognized as fully connected immediately upon game start.
* **ID Alignment:** Aligned internal Building IDs with `game_data.json` to prevent selection errors.

---

## [v3.5 - v3.8] - 2025-12-29
### **The "Content & Feedback" Update**

### **🚀 New Features**
* **New Buildings:**
    * **Garden (🌻):** Small 1x1 tile that boosts happiness.
    * **Factory (🏭):** High income, high pollution 2x2 building.
* **New Milestone:** **Utopia** (Reach >90 Happiness).
* **Persistent Settings:** Volume settings are now saved to `city_rogue_settings.json` and persist between runs.

### **📊 Enhanced Feedback**
* **Info Box Overhaul:** The bottom-right panel now displays detailed breakdown:
    * Cost & AP / Pop & Jobs / Energy & Happiness impacts.
* **Smart Logs:**
    * **Round Summary:** Now displays the **Change (Delta)** in stats (e.g., `Pop +5`, `Happy -2`) instead of just raw totals.
    * **Incidents:** Restored critical warnings for "Citizens Unhappy" and "Power Shortage".
* **Popups:** Added modal popups for Events and Milestones to ensure players don't miss important triggers.

### **⚖ Balance**
* **Event System:** Events are now removed from the pool after triggering (no repeats per run). Added positive events like "Subsidies" and "Grand Festival".

---

## [v3.3] - 2025-12-29
### **The "Island & Integrity" Update**
This version introduces a unified "Island" system to perfectly calculate connectivity and labor, ensuring no exploits are possible.

### **🚀 New Features**
* **Unified Island System:**
    * **Island Logic:** The game now groups all connected tiles (Roads + Buildings) into "Islands".
    * **Global Labor:** Efficiency is calculated based on the total Population vs Jobs *within that specific Island*.
* **Smart Road Visuals:** Roads now only turn **White** (Active) if they belong to an Island that is actually functional.

---

## [v3.2] - 2025-12-29
### **The "Logic & Balance" Update**
Rewrote core connectivity logic and added new events like "Gridlock" and "Mandatory OT".

## [v2.8 - v3.1] - 2025-12-28
### **The "Economy" Update**
* **Data Driven:** Migrated all game data to `game_data.json`.
* **Action Points (AP):** Introduced AP economy (Buildings cost 1 AP, Roads are free).
* **Milestones:** Added persistent achievements that grant permanent +Max AP.

## [v2.7] - 2025-12-27
### **The "Scale & Polish" Update**
* **Infinite-Style Map:** 30x30 Grid with Zoom and Pan controls.
* **Infrastructure:** Added **Bridges** and required Road connectivity.
* **UI Polish:** Restored Info Panel, fixed popup buttons, and centered icons.

## [v1.8] - 2025-12-26
### **The "Roads & Rivers" Update**
* **Roads:** Added buildable roads.
* **Rivers:** Added random river generation.
* **Audio:** Added sound effects.

## [v1.7] - 2025-12-25
### **The "Persistence" Update**
* **Save/Load:** JSON-based save system.
* **Roguelike:** Permadeath (save deletion on loss).
* **High Scores:** Local leaderboard.

## [v1.0 - v1.3] - 2025-12-24
### **The "Synergy" Update**
* **Adjacency Bonuses:** Added combo effects (Shop+House, Office+Park).
* **Relics:** Added 3 selectable starting relics.

## [v0.1] - 2025-12-20
### **Prototype**
* Basic 10x10 grid, 3 building types, and turn-based loop.