"""
Display and UI system for the game
"""
import os
from typing import Optional


class Display:
    """Handles displaying game information to the player."""
    
    @staticmethod
    def clear():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    @staticmethod
    def show_title():
        """Display game title."""
        print("=" * 60)
        print("     CYBER CITY SURVIVAL - Roguelike City Management")
        print("=" * 60)
        print()
        
    @staticmethod
    def show_status(status: dict):
        """Display current game status."""
        city = status.get('city', {})
        
        print(f"\n{'=' * 60}")
        print(f"  Turn: {status['turn']}  |  City: {city.get('name', 'Unknown')}")
        print(f"{'=' * 60}")
        print(f"  💰 Money: ${city.get('money', 0):,}")
        print(f"  👥 Population: {city.get('population', 0):,}")
        print(f"  🏢 Buildings: {city.get('buildings', 0)}")
        print(f"  🔬 Tech Level: {city.get('tech_level', 0)}")
        print(f"{'=' * 60}")
        print(f"  😊 Happiness: {city.get('happiness', 0)}%")
        print(f"  ❤️  Health: {city.get('health', 0)}%")
        print(f"  ⚡ Power: {city.get('power', 0)}")
        print(f"  💧 Water: {city.get('water', 0)}")
        print(f"  🍎 Food: {city.get('food', 0)}")
        print(f"{'=' * 60}\n")
        
    @staticmethod
    def show_message(message: str):
        """Display a message to the player."""
        if message:
            print(f"\n📰 {message}\n")
            
    @staticmethod
    def show_grid(city):
        """Display the city grid."""
        print("\n  City Grid:")
        print("  " + "  ".join([str(i) for i in range(city.grid_size)]))
        
        for y in range(city.grid_size):
            row = f"{y} "
            for x in range(city.grid_size):
                building = city.get_building_at(x, y)
                if building:
                    # Use first letter of building type
                    symbol = building.type.name[0]
                else:
                    symbol = "·"
                row += f"{symbol}  "
            print(row)
        print()
        
    @staticmethod
    def show_buildings_legend():
        """Show what building symbols mean."""
        print("  Building Types:")
        print("  R=Residential, C=Commercial, I=Industrial, P=Power, W=Water")
        print("  R=Research, D=Defense/DataCenter, P=Park, H=Hospital")
        print()
        
    @staticmethod
    def show_menu():
        """Display the main menu options."""
        print("\nActions:")
        print("  1) Build")
        print("  2) View Grid")
        print("  3) Next Turn")
        print("  4) Status")
        print("  5) Help")
        print("  6) Quit")
        
    @staticmethod
    def show_build_menu():
        """Display building options."""
        from game.city.buildings import BuildingType, Building
        
        print("\nAvailable Buildings:")
        for i, building_type in enumerate(BuildingType, 1):
            cost = Building.BUILDING_COSTS.get(building_type, 0)
            print(f"  {i}) {building_type.value} - ${cost}")
        print("  0) Cancel")
        
    @staticmethod
    def show_help():
        """Display help information."""
        print("\n" + "=" * 60)
        print("HELP - How to Play")
        print("=" * 60)
        print("""
Your goal is to build a thriving high-tech city while managing resources
and responding to random events.

WIN CONDITIONS:
- Reach 1000 population AND tech level 10

LOSE CONDITIONS:
- Population drops to 0
- Money drops below -$1000

RESOURCES:
- Money: Build buildings and maintain the city
- Population: Citizens living in your city
- Tech Level: Advances through research
- Happiness: Affects population growth
- Health: Keeps your citizens alive
- Power/Water/Food: Essential resources

BUILDINGS:
Each building provides different benefits and costs upkeep per turn.
Build strategically to balance your resources!

RANDOM EVENTS:
Events occur randomly and can help or harm your city.
Prepare for the unexpected!

Good luck, Mayor!
""")
        print("=" * 60)
        
    @staticmethod
    def show_game_over(victory: bool):
        """Display game over screen."""
        print("\n" + "=" * 60)
        if victory:
            print("        🎉 VICTORY! 🎉")
            print("  Your city has become a technological marvel!")
        else:
            print("        💀 GAME OVER 💀")
            print("     Your city has fallen...")
        print("=" * 60)
        
    @staticmethod
    def prompt(message: str) -> str:
        """Prompt user for input."""
        return input(f"{message}: ").strip()
