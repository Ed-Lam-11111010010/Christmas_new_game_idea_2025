"""
City - Main city management class
"""
import random
from typing import List, Dict, Optional
from game.city.buildings import Building, BuildingType


class City:
    """Represents the player's city."""
    
    def __init__(self, name: str):
        self.name = name
        self.money = 1000
        self.population = 100
        self.tech_level = 1
        self.happiness = 50
        self.health = 50
        
        # Resources
        self.power = 50
        self.water = 50
        self.food = 100
        
        # Grid system (10x10 for simplicity)
        self.grid_size = 10
        self.buildings: List[Building] = []
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Initialize with some basic buildings
        self._initialize_city()
        
    def _initialize_city(self):
        """Set up initial city buildings."""
        # Start with one of each basic building
        self.build(BuildingType.RESIDENTIAL, 2, 2)
        self.build(BuildingType.POWER, 5, 5)
        self.build(BuildingType.COMMERCIAL, 7, 3)
        
    def build(self, building_type: BuildingType, x: int, y: int) -> bool:
        """Build a new building at the specified location."""
        # Check if position is valid
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
            
        # Check if position is occupied
        if self.grid[y][x] is not None:
            return False
            
        # Create building
        building = Building(building_type, x, y)
        cost = building.get_cost()
        
        # Check if we can afford it
        if self.money < cost:
            return False
            
        # Build it
        self.money -= cost
        self.buildings.append(building)
        self.grid[y][x] = building
        return True
        
    def demolish(self, x: int, y: int) -> bool:
        """Demolish a building at the specified location."""
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
            
        building = self.grid[y][x]
        if building is None:
            return False
            
        # Remove building and get partial refund
        self.buildings.remove(building)
        self.grid[y][x] = None
        refund = building.get_cost() // 2
        self.money += refund
        return True
        
    def process_turn(self):
        """Process city maintenance for one turn."""
        # Calculate resource production and consumption
        total_effects = self._calculate_total_effects()
        
        # Apply effects
        self.money += total_effects.get('money_per_turn', 0)
        self.money -= total_effects.get('upkeep', 0)
        self.power = total_effects.get('power', 0)
        self.water = total_effects.get('water', 0)
        
        # Population can grow based on available housing
        max_population = total_effects.get('population', 100)
        if self.population > 0 and self.population < max_population and self.happiness > 30:
            growth = random.randint(1, 5)
            self.population = min(self.population + growth, max_population)
        elif self.happiness < 20 and self.population > 0:
            # People leave if unhappy
            self.population = max(0, self.population - random.randint(1, 3))
            
        # Update happiness based on resources
        self.happiness = 50
        if self.power < self.population * 0.5:
            self.happiness -= 20
        if self.water < self.population * 0.4:
            self.happiness -= 20
        self.happiness += total_effects.get('happiness', 0)
        self.happiness = max(0, min(100, self.happiness))
        
        # Update health
        self.health = 50 + total_effects.get('health', 0)
        self.health = max(0, min(100, self.health))
        
        # Tech level increases with research
        research_points = total_effects.get('research', 0)
        if research_points > 0 and random.random() < 0.1:
            self.tech_level += 1
            
        # Food production (simplified)
        self.food += 10
        self.food -= self.population // 10
        self.food = max(0, self.food)
        
    def _calculate_total_effects(self) -> Dict[str, int]:
        """Calculate total effects from all buildings."""
        total = {}
        for building in self.buildings:
            effects = building.get_effects()
            for key, value in effects.items():
                total[key] = total.get(key, 0) + value * building.level
        return total
        
    def get_status(self) -> dict:
        """Get current city status."""
        return {
            'name': self.name,
            'money': self.money,
            'population': self.population,
            'tech_level': self.tech_level,
            'happiness': self.happiness,
            'health': self.health,
            'power': self.power,
            'water': self.water,
            'food': self.food,
            'buildings': len(self.buildings)
        }
        
    def get_building_at(self, x: int, y: int) -> Optional[Building]:
        """Get building at specified position."""
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return None
        return self.grid[y][x]
