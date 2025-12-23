"""
Building types for the high-tech city
"""
from enum import Enum
from typing import Dict


class BuildingType(Enum):
    """Types of buildings available in the city."""
    RESIDENTIAL = "Residential Tower"
    COMMERCIAL = "Commercial Complex"
    INDUSTRIAL = "Tech Factory"
    POWER = "Fusion Reactor"
    WATER = "Water Recycling Plant"
    RESEARCH = "Research Lab"
    DEFENSE = "Defense Grid"
    PARK = "Cyber Park"
    HOSPITAL = "Medical Center"
    DATACENTER = "Data Center"


class Building:
    """Represents a building in the city."""
    
    BUILDING_COSTS = {
        BuildingType.RESIDENTIAL: 100,
        BuildingType.COMMERCIAL: 150,
        BuildingType.INDUSTRIAL: 200,
        BuildingType.POWER: 300,
        BuildingType.WATER: 250,
        BuildingType.RESEARCH: 400,
        BuildingType.DEFENSE: 350,
        BuildingType.PARK: 80,
        BuildingType.HOSPITAL: 300,
        BuildingType.DATACENTER: 500,
    }
    
    BUILDING_EFFECTS = {
        BuildingType.RESIDENTIAL: {'population': 50, 'upkeep': 5},
        BuildingType.COMMERCIAL: {'money_per_turn': 20, 'upkeep': 10},
        BuildingType.INDUSTRIAL: {'production': 15, 'upkeep': 15, 'pollution': 5},
        BuildingType.POWER: {'power': 100, 'upkeep': 20},
        BuildingType.WATER: {'water': 80, 'upkeep': 15},
        BuildingType.RESEARCH: {'research': 10, 'upkeep': 25},
        BuildingType.DEFENSE: {'defense': 50, 'upkeep': 30},
        BuildingType.PARK: {'happiness': 10, 'upkeep': 5},
        BuildingType.HOSPITAL: {'health': 30, 'upkeep': 20},
        BuildingType.DATACENTER: {'data': 40, 'upkeep': 35, 'research': 5},
    }
    
    def __init__(self, building_type: BuildingType, x: int, y: int):
        self.type = building_type
        self.x = x
        self.y = y
        self.level = 1
        
    def get_effects(self) -> Dict[str, int]:
        """Get the effects this building provides."""
        return self.BUILDING_EFFECTS.get(self.type, {}).copy()
        
    def get_cost(self) -> int:
        """Get the construction cost."""
        return self.BUILDING_COSTS.get(self.type, 0)
        
    def upgrade(self) -> int:
        """Upgrade the building, returns cost."""
        cost = self.get_cost() * self.level
        self.level += 1
        return cost
        
    def __str__(self):
        return f"{self.type.value} (Lv{self.level})"
