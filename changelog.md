# 📜 City Rogue - Changelog

All notable changes to the "City Rogue" project will be documented in this file.

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