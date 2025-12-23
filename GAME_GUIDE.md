# Cyber City Survival - Complete Game Guide

## 🎮 Quick Start

```bash
python main.py
```

Then follow the on-screen prompts to play!

## 📚 Detailed Gameplay Guide

### Starting Your City

When you start a new game:
1. Enter a name for your city (or press Enter for default "Neo City")
2. You'll start with:
   - $1000 in funds
   - 100 citizens
   - 3 basic buildings (1 Residential, 1 Power, 1 Commercial)
   - Tech Level 1

### Understanding the Interface

#### Status Display
```
============================================================
  Turn: 5  |  City: Neo City
============================================================
  💰 Money: $450
  👥 Population: 120
  🏢 Buildings: 5
  🔬 Tech Level: 2
============================================================
  😊 Happiness: 65%
  ❤️  Health: 70%
  ⚡ Power: 150
  💧 Water: 80
  🍎 Food: 95
============================================================
```

#### Grid Display
The city is represented as a 10x10 grid:
```
  0  1  2  3  4  5  6  7  8  9
0 ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  
1 ·  C  ·  ·  ·  ·  ·  ·  ·  ·  
2 ·  ·  R  ·  ·  ·  ·  ·  ·  ·  
3 ·  ·  ·  ·  ·  ·  ·  C  ·  ·  
```

Where:
- `·` = Empty space
- `R` = Residential
- `C` = Commercial
- `I` = Industrial
- `E` = Energy/Power (Fusion Reactor)
- `W` = Water (Recycling Plant)
- `L` = Research Lab
- `D` = Defense Grid
- `T` = Data Center
- `K` = Park (Cyber Park)
- `H` = Hospital (Medical Center)

### Building Strategy Guide

#### Early Game (Turns 1-20)
**Priority: Establish stable income and resources**

1. **Build 1-2 Commercial Complexes** ($150 each)
   - Provides steady income (+20/turn each)
   - Essential for early economy

2. **Add Power Generation** ($300)
   - Fusion Reactor provides 100 power
   - Prevents happiness penalties

3. **Build Residential Towers** ($100 each)
   - Increases population capacity
   - Cheap and effective

**Expected Outcome:** Positive cash flow, growing population

#### Mid Game (Turns 20-50)
**Priority: Scale up and invest in technology**

1. **Build Research Labs** ($400 each)
   - +10 research per turn
   - Critical for reaching tech level 10

2. **Add Medical Centers** ($300)
   - +30 health
   - Prevents disease impact

3. **Build Water Recycling Plants** ($250)
   - Essential resource
   - Prevents happiness loss

4. **Add Cyber Parks** ($80)
   - Cheap happiness boost
   - Good filler buildings

**Expected Outcome:** Tech level 3-5, population 300-500

#### Late Game (Turns 50+)
**Priority: Push toward victory conditions**

1. **Maximum Research Labs**
   - Need tech level 10 to win
   - Each lab gives 10 research/turn

2. **Data Centers** ($500)
   - Expensive but powerful
   - +40 data, +5 research

3. **More Residential Towers**
   - Need 1000 population to win
   - Build 15-20 total

4. **Defense Grids** ($350)
   - Reduces event damage
   - Insurance against disasters

**Victory Target:** 1000 population + Tech Level 10

### Resource Management

#### Money 💰
- **Income Sources:**
  - Commercial Complexes: +20/turn each
  - Starting balance: $1000
  
- **Expenses:**
  - Building construction (one-time)
  - Upkeep costs (every turn)
  
- **Tips:**
  - Always keep $500+ reserve
  - Build income buildings early
  - Demolish unprofitable buildings (50% refund)

#### Population 👥
- **Growth Factors:**
  - Requires available housing (Residential Towers)
  - Needs happiness > 30%
  - Grows 1-5 per turn when conditions met
  
- **Decline Factors:**
  - Happiness < 20%
  - Loses 1-3 per turn
  - Events can cause sudden drops

- **Tips:**
  - Build housing ahead of demand
  - Maintain happiness above 30%
  - Medical Centers reduce disease impact

#### Happiness 😊
- **Base:** 50%
- **Penalties:**
  - Power shortage: -20%
  - Water shortage: -20%
  - Random events: varies
  
- **Bonuses:**
  - Cyber Parks: +10% each
  - Random events: varies
  
- **Tips:**
  - Keep power/water ahead of population
  - Build parks when happiness drops
  - Aim for 50%+ consistently

#### Tech Level 🔬
- **Increases from:**
  - Research Labs: +10 research/turn each
  - Data Centers: +5 research/turn each
  - Tech Breakthrough events: +1 level
  
- **Important:**
  - Research is RNG-based (10% chance/turn)
  - More research = faster advancement
  - Need level 10 to win
  
- **Tips:**
  - Build 3-4 Research Labs minimum
  - Data Centers are expensive but effective
  - Don't rely only on events

### Dealing with Random Events

#### Positive Events 🎉
- **Tech Breakthrough:** +1 tech level, +10 happiness
  - Awesome! Build research labs to increase odds
  
- **Economic Boom:** +$400, +15 happiness
  - Use windfall to build expensive buildings
  
- **Population Boom:** +30 population
  - Make sure you have housing ready!
  
- **Trade Deal:** +$300, +50 food
  - Free money, no downside

#### Negative Events ⚠️
- **Cyber Attack:** -$200, -10 happiness
  - Build Defense Grids to reduce frequency
  
- **Natural Disaster:** -$300, -20 population, -15 happiness
  - Keep reserves for recovery
  - Build Medical Centers
  
- **Disease Outbreak:** -15 population, -20 health, -10 happiness
  - Medical Centers help prevent
  - Health management is key
  
- **Energy Crisis:** -30 power, -15 happiness
  - Build extra Fusion Reactors
  - Maintain power surplus
  
- **Crime Wave:** -$150, -20 happiness
  - Defense Grids help
  - Keep happiness high

#### Event Management Tips
1. **Prepare for worst case:** Events become more frequent over time
2. **Build redundancy:** Extra power, water, and money reserves
3. **React quickly:** Build what you need after bad events
4. **Leverage good events:** Use windfalls strategically

### Win Conditions & Game Over

#### Victory 🎉
You win when you achieve BOTH:
- **Population ≥ 1000**
- **Tech Level ≥ 10**

Typical winning game: 60-100 turns

#### Defeat 💀
You lose if ANY of these occur:
- **Population = 0:** City abandoned
- **Money < -$1000:** Bankruptcy

### Advanced Strategies

#### The "Tech Rush" Strategy
- Focus heavily on research early
- Build 4-5 Research Labs by turn 30
- Reach tech 10, then grow population
- **Risk:** Low population, vulnerable to events
- **Reward:** Faster wins (50-70 turns)

#### The "Stable Growth" Strategy
- Balance all resources evenly
- Gradual expansion across all building types
- Slower but safer
- **Risk:** Longer games = more events
- **Reward:** More resilient to disasters

#### The "Economic Engine" Strategy
- Build many Commercial Complexes early
- Use profits to rapidly expand
- Money solves most problems
- **Risk:** High upkeep costs
- **Reward:** Can recover from any event

### Common Mistakes to Avoid

1. **Over-building too fast**
   - Each building has upkeep
   - Can quickly bankrupt you
   - Build gradually

2. **Ignoring happiness**
   - Low happiness = population decline
   - Population decline = defeat
   - Always monitor happiness

3. **No reserves**
   - Events can cost $300+ suddenly
   - Need buffer for emergencies
   - Keep $500+ always

4. **Neglecting research**
   - Tech level 10 is required to win
   - Takes many turns to achieve
   - Start building labs early

5. **Poor building placement**
   - Once built, location is permanent
   - Plan ahead for growth
   - Leave room for expansion

### Tips for Winning

1. **First 10 turns:**
   - Build 2 Commercial Complexes
   - Add 1 Fusion Reactor
   - Build 1 Research Lab if affordable

2. **Turns 10-30:**
   - Maintain positive cash flow
   - Build 2-3 total Research Labs
   - Add Medical Center and Parks
   - Keep happiness > 40%

3. **Turns 30-60:**
   - Focus on research buildings
   - Build Residential Towers for population
   - Maintain resource balance
   - Target: Tech 7-8, Population 600+

4. **Final push (60+):**
   - Max out Research Labs (4-6 total)
   - Build Residential to 1000 population
   - Maintain financial stability
   - Weather events until victory!

### Keyboard Shortcuts & Commands

- **Menu Navigation:** Type numbers 1-6
- **Building Selection:** Type building number
- **Grid Coordinates:** Type "x,y" (e.g., "3,5")
- **Cancel:** Type "0" or "c"
- **Quit:** Select option 6 from main menu

## 🎯 Sample Winning Build Order

Here's a proven build order for a ~70 turn victory:

```
Turn 0-5:   Commercial Complex (1,1)
Turn 5-10:  Research Lab (3,3)
Turn 10-15: Commercial Complex (4,4)
Turn 15-20: Medical Center (6,6)
Turn 20-25: Research Lab (7,7)
Turn 25-30: Residential Tower (8,8)
Turn 30-35: Fusion Reactor (9,9)
Turn 35-40: Research Lab (0,5)
Turn 40-45: Residential Tower (0,6)
Turn 45-50: Data Center (0,7)
Turn 50-60: More Residential Towers
Turn 60-70: Continue until victory!
```

## 🐛 Troubleshooting

**Q: Game won't start**
- Ensure Python 3.8+ is installed
- Run: `python --version`
- Try: `python3 main.py`

**Q: Population won't grow**
- Check happiness (must be > 30%)
- Check you have Residential capacity
- Ensure population > 0 (can't recover from 0)

**Q: Running out of money**
- Build more Commercial Complexes
- Demolish expensive buildings with low value
- Reduce upkeep costs

**Q: Tech level stuck**
- Build more Research Labs
- Research advances randomly (10% chance/turn)
- More research = faster advancement

**Q: Keep losing to events**
- Build redundancy (extra resources)
- Maintain larger cash reserves
- Build Defense Grids and Medical Centers

## 📊 Building Reference Table

| Building | Cost | Upkeep | Key Benefit | When to Build |
|----------|------|--------|-------------|---------------|
| Residential Tower | $100 | $5 | +50 pop capacity | Early & often |
| Commercial Complex | $150 | $10 | +$20/turn | Early game |
| Tech Factory | $200 | $15 | +15 production | Optional |
| Fusion Reactor | $300 | $20 | +100 power | When power needed |
| Water Plant | $250 | $15 | +80 water | When water needed |
| Research Lab | $400 | $25 | +10 research | Mid-game, essential |
| Defense Grid | $350 | $30 | +50 defense | Late game |
| Cyber Park | $80 | $5 | +10 happiness | Filler, cheap |
| Medical Center | $300 | $20 | +30 health | Mid game |
| Data Center | $500 | $35 | +40 data, +5 research | Late game |

## 🏆 Achievements to Try

While not tracked in-game, try these challenges:

- **Speed Runner:** Win in under 60 turns
- **Minimalist:** Win with fewer than 15 buildings
- **Researcher:** Reach tech level 15
- **Metropolis:** Reach 2000 population
- **Wealthy:** Accumulate $5000+
- **Perfect City:** Win with 100% happiness
- **Survivor:** Win after experiencing 20+ events
- **Comeback Kid:** Win after dropping below $100

---

**Good luck, Mayor! May your city prosper! 🌆✨**
