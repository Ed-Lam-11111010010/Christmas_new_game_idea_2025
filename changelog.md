# 📜 City Rogue - Changelog

All notable changes to the "City Rogue" project will be documented in this file.

## [v3.3] - 2025-12-29 (Current Stable Build)
### **The "Island & Integrity" Update**
This version introduces a unified "Island" system to perfectly calculate connectivity and labor, ensuring no exploits are possible. It also hardens the milestone system against duplicate rewards.

### **🚀 New Features**
* **Unified Island System:**
    * **Island Logic:** The game now groups all connected tiles (Roads + Buildings) into "Islands".
    * **Global Labor:** Efficiency is calculated based on the total Population vs Jobs *within that specific Island*.
    * **Mixed Connectivity:** Buildings connect via roads OR by directly touching each other. As long as they are in the same "Island," they share resources.
* **Smart Road Visuals:** Roads now only turn **White** (Active) if they belong to an Island that is actually functional (has residents or jobs). Empty road networks remain dark.

### **🐛 Bug Fixes**
* **Milestone Exploit Fix:** Milestone rewards (e.g., Max AP) are now applied exactly once at the moment of unlocking. They are saved directly to the save file and never re-calculated on load, preventing double-dipping.
* **Labor Logic Fix:** Fixed issues where isolated buildings could sometimes claim 100% efficiency. Now, if an Island has 0 Population, all offices in it have 0% Efficiency.

---

## [v3.2] - 2025-12-29
### **The "Logic & Balance" Update**
This version rewrites the core connectivity logic to fix labor exploits and introduces advanced event mechanics.

### **🚀 New Features**
* **Advanced Connectivity System:**
    * **Cluster Logic:** Buildings are now grouped into "Communities". Labor is calculated based on the total population and jobs within a connected group (roads + adjacency).
    * **Direct Neighbors:** Buildings directly touching a House now count as connected, even without a road.
* **New Events:**
    * **Gridlock:** Temporary penalty (-1 Max Action Point).
    * **Mandatory OT:** Trade-off event (-5 Happiness, +1 Max Action Point).
* **Enhanced Logs:** Round summaries now appear in Cyan for better visibility, detailing exact income and energy changes.

### **🐛 Bug Fixes**
* **Infinite Labor Fix:** Fixed a bug where isolated office clusters would generate 100% efficiency with 0 population.
* **Milestone Fix:** Fixed an issue where milestones could be triggered multiple times in a single run.
* **Road Visuals:** Roads now correctly light up (White) only when connected to an active building or network.

---

## [v3.1] - 2025-12-29
### **The "Visuals & Milestones" Update**
* **Visual Feedback:** Roads now visually indicate their state.
    * **White (Active):** Connected to a functioning building or network.
    * **Dark Gray (Inactive):** Road to nowhere.
* **New Milestone:** **Metropolis** (Reach Population > 50). Rewards +1 Max Action Point permanently.

## [v3.0] - 2025-12-28
### **The "Achievement" Update**
* **Milestone System:** Added a persistent achievement system that tracks across runs.
    * **Wealthy City:** Reach >$500 Income to unlock +1 Max Action Point permanently.
* **Labor Logic Update:** Buildings no longer strictly require roads if they are directly adjacent to a House.
* **New Events:** Added "Red Tape" (AP Penalty) and "Streamlined" (AP Bonus).

## [v2.9] - 2025-12-28
### **The "Action Economy" Update**
* **Action Points (AP):** Players now have a limited number of actions (Stars) per turn.
    * Buildings cost **1 AP**.
    * Roads/Bridges cost **0 AP** (Free actions, money only).
* **Clustering Rule:** Connectivity rules relaxed. Buildings can now connect to the network via *other buildings*, allowing for 2x2 or 3x3 city blocks.

## [v2.8] - 2025-12-28
### **The "Data Driven" Update**
* **External Data:** All game data (Buildings, Relics, Events) moved to `game_data.json`.
    * Allows for easy modding and balance tweaks without touching code.
* **Leaderboard Reset:** Score file updated to `v2` to support the new economy balance.
* **Detailed Logs:** Added specific warnings for "Labor Shortage" and detailed event descriptions in the log.

---

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