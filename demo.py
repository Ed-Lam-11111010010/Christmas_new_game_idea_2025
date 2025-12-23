#!/usr/bin/env python3
"""
Automated Demo - Shows a sample gameplay session of Cyber City Survival
This script simulates a player session to demonstrate the game mechanics.
"""
import sys
sys.path.insert(0, '/home/runner/work/Christmas_new_game_idea_2025/Christmas_new_game_idea_2025')

from game.core.engine import GameEngine
from game.city.buildings import BuildingType
from game.ui.display import Display
import time


def demo_game():
    """Run an automated demo of the game."""
    display = Display()
    engine = GameEngine()
    
    print("\n" + "=" * 70)
    print("CYBER CITY SURVIVAL - AUTOMATED DEMO")
    print("=" * 70)
    print("\nThis demo will showcase the game mechanics automatically.")
    print("Press Ctrl+C at any time to stop.\n")
    time.sleep(2)
    
    # Start new game
    print(">>> Starting new game: 'Demo City'")
    engine.new_game("Demo City")
    time.sleep(1)
    
    # Show initial status
    print("\n--- INITIAL STATE ---")
    status = engine.get_status()
    display.show_status(status)
    display.show_message(status['message'])
    time.sleep(3)
    
    # Show initial grid
    print("\n>>> Viewing initial city grid")
    display.show_grid(engine.city)
    display.show_buildings_legend()
    print("\nInitial buildings:")
    for building in engine.city.buildings:
        print(f"  - {building} at ({building.x}, {building.y})")
    time.sleep(3)
    
    # Build some buildings
    print("\n--- BUILDING PHASE ---")
    buildings_to_build = [
        (BuildingType.COMMERCIAL, 1, 1, "Commercial Complex for income"),
        (BuildingType.RESEARCH, 3, 3, "Research Lab for tech advancement"),
        (BuildingType.HOSPITAL, 6, 6, "Medical Center for citizen health"),
        (BuildingType.PARK, 8, 8, "Cyber Park for happiness"),
    ]
    
    for building_type, x, y, reason in buildings_to_build:
        cost = engine.city.money
        if engine.city.build(building_type, x, y):
            new_cost = engine.city.money
            print(f"✓ Built {building_type.value} at ({x},{y}) - {reason}")
            print(f"  Cost: ${cost - new_cost}")
        else:
            print(f"✗ Failed to build {building_type.value} at ({x},{y})")
        time.sleep(1)
    
    # Show updated grid
    print("\n>>> Updated city grid after construction:")
    display.show_grid(engine.city)
    time.sleep(2)
    
    # Simulate several turns
    print("\n--- SIMULATION: 15 TURNS ---")
    for turn_num in range(15):
        engine.process_turn()
        status = engine.get_status()
        
        print(f"\nTurn {status['turn']}:")
        print(f"  💰 ${status['city']['money']:,} | "
              f"👥 {status['city']['population']:,} | "
              f"😊 {status['city']['happiness']}% | "
              f"🔬 Tech Lv.{status['city']['tech_level']}")
        
        if "EVENT:" in status['message']:
            print(f"  🎲 {status['message']}")
            time.sleep(2)
        
        if engine.state.game_over:
            print(f"\n  ⚠️  {status['message']}")
            break
            
        time.sleep(0.5)
    
    # Final status
    print("\n--- FINAL STATUS ---")
    final_status = engine.get_status()
    display.show_status(final_status)
    
    if engine.state.game_over:
        display.show_game_over(engine.state.victory)
    else:
        print("\nDemo completed successfully! The city continues to thrive.")
        print("\nTo play the full game, run: python main.py")
    
    # Show final statistics
    print("\n--- STATISTICS ---")
    print(f"Total Turns Played: {final_status['turn']}")
    print(f"Final Population: {final_status['city']['population']:,}")
    print(f"Final Money: ${final_status['city']['money']:,}")
    print(f"Final Tech Level: {final_status['city']['tech_level']}")
    print(f"Buildings Constructed: {final_status['city']['buildings']}")
    print(f"Citizen Happiness: {final_status['city']['happiness']}%")
    print(f"Citizen Health: {final_status['city']['health']}%")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ City initialization with starting buildings")
    print("  ✓ Building construction system")
    print("  ✓ Turn-based gameplay mechanics")
    print("  ✓ Resource management (money, population, happiness)")
    print("  ✓ Random events system")
    print("  ✓ City grid visualization")
    print("  ✓ Game state tracking")
    print("\nTo play the interactive game: python main.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        demo_game()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
