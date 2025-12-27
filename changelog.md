📜 City Rogue - Changelog
All notable changes to the "City Rogue" project will be documented in this file.

[v2.7] - 2025-12-27 (Current Stable Build)
The "Scale & Polish" Update
This version marks the transition from a simple grid game to a scalable city builder with a large scrolling map, complex economy, and polished UI.

🚀 New Features
Infinite-Style Map:

30x30 Grid: Map size tripled (900 tiles total).

Camera Controls: Added Right-Click Drag to pan and Scroll Wheel to zoom (0.5x - 2.0x).

River Generation: Random rivers now flow through the map, acting as natural barriers.

Infrastructure & Economy:

Road Connectivity: Buildings now require a valid road connection to function. Disconnected buildings show a "⚠ No Road" warning.

Bridges (🌉): New building ($30) that can be built on water to connect islands.

Local Economy: Workers only commute to jobs within their connected road network.

Building Overhaul:

2x2 Buildings: Houses, Offices, Shops, Power Plants, and Parks now occupy a 2x2 tile space.

Roads & Bridges: Remain 1x1 for detailed layout control.

✨ UI & UX Improvements
Restored Info Panel: Bottom-right panel displays building stats, costs, and active Event effects.

Predictive Tooltips: Hovering over the map calculates and displays specific adjacency bonuses (e.g., "Combo: +15💰") or warnings before building.

Pass Turn Button: Added a dedicated, safe-to-click button in the sidebar.

Game Over Screen: Added a proper Victory/Bankruptcy screen with "Play Again" and "Main Menu" options.

Icon Alignment: Building icons are now perfectly centered within their footprint (1x1 or 2x2).

🐛 Bug Fixes
Rendering: Fixed 2x2 buildings disappearing when scrolling or overlapping with terrain (implemented Two-Pass Rendering).

Input: Fixed "Upgrade/Sell" popup buttons not being clickable.

Input: Prioritized the "Pass Turn" button to prevent accidental map clicks.

Stability: Fixed crashes related to TILE_SIZE variables and camera initialization.

[v1.8] - 2025-12-26
The "Roads & Rivers" Update
New Building: Road (🛣️) ($10). Essential for connecting buildings.

Rivers: Added basic random river generation (impassable terrain).

Sound Effects: Added support for SFX (build.wav, money.wav, select.wav).

[v1.7] - 2025-12-25
The "Persistence" Update
Save/Load System: Game now auto-saves after every turn. Added "Load Game" to Main Menu.

Roguelike Elements: Save files are deleted upon death (Bankruptcy) or Victory.

High Scores: Added a local leaderboard tracking the top 5 runs.

Visuals: Replaced text labels with Emojis (💰, ⚡, 👥, 😊) for better readability.

[v1.3] - 2025-12-24
The "Synergy" Update
Adjacency Bonuses:

House ↔ Park: +5 Happiness.

Shop ↔ House: +$15 Income per adjacent House.

Office ↔ Park: +20% Income.

NIMBY Mechanic: Houses lose happiness if placed near Power Plants.

Bidirectional Logic: Tooltips now show both incoming effects (what neighbors do to you) and outgoing effects (what you do to neighbors).

[v1.1] - 2025-12-24
The "Relic" Update
New Building: Shop (🏪). Low base income but high combo potential.

Relic System: Players choose 1 of 3 "Mayoral Artifacts" at the start of a run (e.g., The Industrialist).

[v0.9] - 2025-12-23
The "Efficiency" Update
Labor System: Buildings now require a workforce. Efficiency = Pop / Jobs.

Understaffing: Buildings operate at reduced capacity if there aren't enough workers.

Feedback: Added verbose event logs for blackouts, unrest, and bonuses.

[v0.1 - v0.5] - 2025-12-20 to 2025-12-22
The Prototype Phase
Core Loop: Established the 10x10 grid, turn-based system, and basic resources (Money, Energy).

Buildings: Implemented House, Office, Power Plant.

Events: Added random events every 5 rounds (Inflation, Plague, Tech Boom).

UI: Basic sidebar and grid rendering.