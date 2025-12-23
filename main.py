#!/usr/bin/env python3
"""
Main entry point for Cyber City Survival
A Roguelike City Management Game
"""
from game.core.engine import GameEngine
from game.city.buildings import BuildingType, Building
from game.ui.display import Display


class Game:
    """Main game controller."""
    
    def __init__(self):
        self.engine = GameEngine()
        self.display = Display()
        self.running = False
        
    def start(self):
        """Start the game."""
        self.display.clear()
        self.display.show_title()
        
        print("Welcome to Cyber City Survival!")
        city_name = self.display.prompt("Enter your city name (or press Enter for 'Neo City')")
        if not city_name:
            city_name = "Neo City"
            
        self.engine.new_game(city_name)
        self.running = True
        
        # Show initial help
        self.display.show_help()
        input("\nPress Enter to begin...")
        
        self.game_loop()
        
    def game_loop(self):
        """Main game loop."""
        while self.running and not self.engine.state.game_over:
            self.display.clear()
            self.display.show_title()
            
            # Show status
            status = self.engine.get_status()
            self.display.show_status(status)
            self.display.show_message(status['message'])
            
            # Show menu and get action
            self.display.show_menu()
            choice = self.display.prompt("Choose an action")
            
            self.handle_action(choice)
            
        # Game over
        if self.engine.state.game_over:
            self.display.clear()
            self.display.show_title()
            status = self.engine.get_status()
            self.display.show_status(status)
            self.display.show_message(status['message'])
            self.display.show_game_over(self.engine.state.victory)
            
    def handle_action(self, choice: str):
        """Handle player action."""
        if choice == "1":
            self.handle_build()
        elif choice == "2":
            self.handle_view_grid()
        elif choice == "3":
            self.handle_next_turn()
        elif choice == "4":
            # Status is already shown, just pause
            input("\nPress Enter to continue...")
        elif choice == "5":
            self.display.show_help()
            input("\nPress Enter to continue...")
        elif choice == "6":
            self.running = False
        else:
            print("Invalid choice!")
            input("\nPress Enter to continue...")
            
    def handle_build(self):
        """Handle building construction."""
        self.display.show_build_menu()
        choice = self.display.prompt("Select building type")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
                
            building_types = list(BuildingType)
            if 1 <= choice_num <= len(building_types):
                building_type = building_types[choice_num - 1]
                
                # Show cost
                cost = Building.BUILDING_COSTS.get(building_type, 0)
                print(f"\n{building_type.value} costs ${cost}")
                
                if self.engine.city.money < cost:
                    print("Not enough money!")
                    input("\nPress Enter to continue...")
                    return
                
                # Show grid
                self.display.show_grid(self.engine.city)
                self.display.show_buildings_legend()
                
                # Get position
                pos = self.display.prompt("Enter position (x,y) or 'c' to cancel")
                if pos.lower() == 'c':
                    return
                    
                try:
                    x, y = map(int, pos.split(','))
                    if self.engine.city.build(building_type, x, y):
                        print(f"\n✓ Built {building_type.value} at ({x},{y})!")
                    else:
                        print("\n✗ Cannot build there!")
                except ValueError:
                    print("\n✗ Invalid position!")
                    
                input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("Invalid choice!")
            input("\nPress Enter to continue...")
            
    def handle_view_grid(self):
        """Handle viewing the city grid."""
        self.display.clear()
        self.display.show_title()
        self.display.show_grid(self.engine.city)
        self.display.show_buildings_legend()
        
        # Show building details
        print("Building Details:")
        for building in self.engine.city.buildings:
            effects = building.get_effects()
            effects_str = ", ".join([f"{k}:{v}" for k, v in effects.items()])
            print(f"  ({building.x},{building.y}) {building} - {effects_str}")
            
        input("\nPress Enter to continue...")
        
    def handle_next_turn(self):
        """Handle advancing to next turn."""
        self.engine.process_turn()
        # Message will be shown in the main loop
        

def main():
    """Main entry point."""
    game = Game()
    try:
        game.start()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        raise
    finally:
        print("\nThank you for playing Cyber City Survival!")


if __name__ == "__main__":
    main()
