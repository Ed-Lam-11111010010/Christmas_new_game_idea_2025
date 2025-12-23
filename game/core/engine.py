"""
Game Engine - Core game loop and state management
"""
from typing import Optional
from game.city.city import City
from game.roguelike.events import EventManager
from game.ui.display import Display


class GameState:
    """Represents the current state of the game."""
    
    def __init__(self):
        self.turn = 0
        self.game_over = False
        self.victory = False
        self.message = ""


class GameEngine:
    """Main game engine handling game loop and state."""
    
    def __init__(self):
        self.state = GameState()
        self.city: Optional[City] = None
        self.event_manager: Optional[EventManager] = None
        self.display = Display()
        
    def new_game(self, city_name: str = "Neo City"):
        """Start a new game."""
        self.state = GameState()
        self.city = City(city_name)
        self.event_manager = EventManager(self.city)
        self.state.message = f"Welcome to {city_name}! Your journey begins..."
        
    def process_turn(self):
        """Process one game turn."""
        if self.state.game_over:
            return
            
        self.state.turn += 1
        
        # City upkeep and maintenance
        self.city.process_turn()
        
        # Check for random events
        event = self.event_manager.check_events(self.state.turn)
        if event:
            self.state.message = event.apply(self.city)
        else:
            self.state.message = f"Turn {self.state.turn}: The city continues to grow..."
            
        # Check win/loss conditions
        self._check_game_over()
        
    def _check_game_over(self):
        """Check if the game is over."""
        if self.city.population <= 0:
            self.state.game_over = True
            self.state.message = "GAME OVER: Your city has been abandoned!"
        elif self.city.money < -1000:
            self.state.game_over = True
            self.state.message = "GAME OVER: Bankruptcy! Your city has collapsed!"
        elif self.city.population >= 1000 and self.city.tech_level >= 10:
            self.state.game_over = True
            self.state.victory = True
            self.state.message = "VICTORY! Your city has become a technological marvel!"
            
    def get_status(self) -> dict:
        """Get current game status."""
        return {
            'turn': self.state.turn,
            'city': self.city.get_status() if self.city else {},
            'message': self.state.message,
            'game_over': self.state.game_over,
            'victory': self.state.victory
        }
