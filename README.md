# Cyber City Survival 🌆⚡

A **Roguelike City Management Game** set in a futuristic, high-tech metropolis. Build and manage your cyber city while dealing with random events, resource management, and the challenges of maintaining a technological marvel!

## 🎮 Game Overview

Cyber City Survival combines the strategic depth of city management with the unpredictability of roguelike mechanics. As the mayor of a futuristic city, you must:

- **Build** high-tech structures and infrastructure
- **Manage** resources like money, power, water, and food
- **Survive** random events that can make or break your city
- **Grow** your population and advance your technology level
- **Balance** citizen happiness, health, and economic prosperity

## 🎯 Win/Lose Conditions

### Victory Conditions
- Reach **1,000 population** AND **Tech Level 10**

### Defeat Conditions
- Population drops to **0** (city abandoned)
- Money drops below **-$1,000** (bankruptcy)

## 🏗️ Building Types

Your city features various high-tech buildings:

| Building | Cost | Effects |
|----------|------|---------|
| **Residential Tower** | $100 | +50 population capacity |
| **Commercial Complex** | $150 | +20 money/turn |
| **Tech Factory** | $200 | +15 production, +5 pollution |
| **Fusion Reactor** | $300 | +100 power |
| **Water Recycling Plant** | $250 | +80 water |
| **Research Lab** | $400 | +10 research |
| **Defense Grid** | $350 | +50 defense |
| **Cyber Park** | $80 | +10 happiness |
| **Medical Center** | $300 | +30 health |
| **Data Center** | $500 | +40 data, +5 research |

## 🎲 Roguelike Features

### Random Events
Experience unexpected events that will test your city management skills:
- 🔴 **Cyber Attacks** - Hackers breach your systems
- 🔬 **Tech Breakthroughs** - Scientific discoveries
- 📈 **Economic Booms** - Financial windfalls
- 🌊 **Natural Disasters** - Earthquakes and catastrophes
- 🦠 **Disease Outbreaks** - Health crises
- ⚡ **Energy Crises** - Power shortages
- 🌞 **Solar Flares** - Electronic disruptions
- And more!

### Permadeath
Each game is unique. Once your city falls, you must start fresh with a new city!

## 🚀 Getting Started

### Requirements
- Python 3.8 or higher
- No external dependencies required! (Uses Python standard library only)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Ed-Lam-11111010010/Christmas_new_game_idea_2025.git
cd Christmas_new_game_idea_2025
```

2. Run the game:
```bash
python main.py
```

Or make it executable and run directly:
```bash
chmod +x main.py
./main.py
```

## 📖 How to Play

### Main Menu Actions
1. **Build** - Construct new buildings on the city grid
2. **View Grid** - See your city layout and building details
3. **Next Turn** - Advance time and process city maintenance
4. **Status** - View detailed city statistics
5. **Help** - Display game instructions
6. **Quit** - Exit the game

### Building Strategy
- Start with **Residential Towers** to increase population capacity
- Build **Fusion Reactors** and **Water Plants** to meet resource needs
- Add **Commercial Complexes** for steady income
- Invest in **Research Labs** to advance technology
- Use **Medical Centers** and **Cyber Parks** to maintain citizen well-being

### Resource Management
- **Money**: Required for construction and paid as upkeep each turn
- **Population**: Grows when happiness is high and housing is available
- **Power & Water**: Essential utilities - shortages reduce happiness
- **Food**: Automatically produced, consumed by population
- **Happiness**: Affects population growth/decline
- **Health**: Keeps citizens alive and productive
- **Tech Level**: Unlocked through research buildings

## 🎨 Game Features

### City Grid System
- 10x10 grid for strategic building placement
- Visual representation of your city layout
- Each building shows its type and level

### Dynamic Events
- Events become more frequent as the game progresses
- Random outcomes keep each playthrough unique
- Balance risk and reward in your decisions

### Turn-Based Gameplay
- Take your time to plan each move
- No time pressure - pure strategy
- Watch your city evolve turn by turn

## 🗂️ Project Structure

```
Christmas_new_game_idea_2025/
├── game/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py          # Game engine and state management
│   ├── city/
│   │   ├── __init__.py
│   │   ├── buildings.py       # Building types and mechanics
│   │   └── city.py            # City management system
│   ├── roguelike/
│   │   ├── __init__.py
│   │   └── events.py          # Random events system
│   └── ui/
│       ├── __init__.py
│       └── display.py         # Terminal UI and display
├── main.py                     # Game entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## 🎯 Strategy Tips

1. **Start Small**: Don't expand too quickly - balance income with expenses
2. **Resource Balance**: Keep power and water production ahead of demand
3. **Save Money**: Always maintain a financial buffer for emergencies
4. **Research Early**: Tech level is crucial for victory
5. **Happiness Matters**: Unhappy citizens will leave your city
6. **Plan Ahead**: Events are unpredictable - build redundancy into your city

## 🔧 Development

This game uses only Python's standard library, making it:
- ✅ Easy to install and run
- ✅ Lightweight and fast
- ✅ Portable across all platforms
- ✅ No dependency management required

## 📝 License

This project is open source and available for educational and entertainment purposes.

## 🙏 Credits

Created by Ed-Lam as a Python roguelike city management game experiment.

---

**Enjoy building your cyber city and may your reign be prosperous!** 🌆✨
