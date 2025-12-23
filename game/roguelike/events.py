"""
Random events for the roguelike experience
"""
import random
from typing import Optional
from enum import Enum


class EventType(Enum):
    """Types of random events that can occur."""
    CYBER_ATTACK = "Cyber Attack"
    TECH_BREAKTHROUGH = "Tech Breakthrough"
    POPULATION_BOOM = "Population Boom"
    NATURAL_DISASTER = "Natural Disaster"
    ECONOMIC_BOOM = "Economic Boom"
    DISEASE_OUTBREAK = "Disease Outbreak"
    ENERGY_CRISIS = "Energy Crisis"
    WATER_SHORTAGE = "Water Shortage"
    CRIME_WAVE = "Crime Wave"
    AI_MALFUNCTION = "AI Malfunction"
    SOLAR_FLARE = "Solar Flare"
    TRADE_DEAL = "Trade Deal"


class Event:
    """Represents a random event."""
    
    def __init__(self, event_type: EventType, description: str, effects: dict):
        self.type = event_type
        self.description = description
        self.effects = effects
        
    def apply(self, city) -> str:
        """Apply event effects to the city."""
        message = f"EVENT: {self.type.value}! {self.description}\n"
        
        for key, value in self.effects.items():
            if hasattr(city, key):
                old_value = getattr(city, key)
                new_value = max(0, old_value + value)
                setattr(city, key, new_value)
                
                if value > 0:
                    message += f"  +{value} {key}\n"
                else:
                    message += f"  {value} {key}\n"
                    
        return message.strip()


class EventManager:
    """Manages random events in the game."""
    
    def __init__(self, city):
        self.city = city
        self.event_chance = 0.3  # 30% chance per turn
        self.events = self._create_events()
        
    def _create_events(self):
        """Create all possible events."""
        return [
            Event(
                EventType.CYBER_ATTACK,
                "Hackers have breached your systems!",
                {'money': -200, 'happiness': -10}
            ),
            Event(
                EventType.TECH_BREAKTHROUGH,
                "Scientists make a major discovery!",
                {'tech_level': 1, 'happiness': 10}
            ),
            Event(
                EventType.POPULATION_BOOM,
                "Immigrants flock to your prosperous city!",
                {'population': 30}
            ),
            Event(
                EventType.NATURAL_DISASTER,
                "An earthquake strikes the city!",
                {'money': -300, 'population': -20, 'happiness': -15}
            ),
            Event(
                EventType.ECONOMIC_BOOM,
                "The economy is thriving!",
                {'money': 400, 'happiness': 15}
            ),
            Event(
                EventType.DISEASE_OUTBREAK,
                "A virus spreads through the city!",
                {'population': -15, 'health': -20, 'happiness': -10}
            ),
            Event(
                EventType.ENERGY_CRISIS,
                "Power shortages affect the city!",
                {'power': -30, 'happiness': -15}
            ),
            Event(
                EventType.WATER_SHORTAGE,
                "Water supplies run low!",
                {'water': -25, 'happiness': -10}
            ),
            Event(
                EventType.CRIME_WAVE,
                "Crime rates spike in the city!",
                {'money': -150, 'happiness': -20}
            ),
            Event(
                EventType.AI_MALFUNCTION,
                "City AI systems malfunction!",
                {'power': -20, 'money': -100}
            ),
            Event(
                EventType.SOLAR_FLARE,
                "A solar flare disrupts electronics!",
                {'power': -40, 'tech_level': -1}
            ),
            Event(
                EventType.TRADE_DEAL,
                "A lucrative trade agreement is signed!",
                {'money': 300, 'food': 50}
            ),
        ]
        
    def check_events(self, turn: int) -> Optional[Event]:
        """Check if an event occurs this turn."""
        # Increase chance slightly as game progresses
        chance = min(0.5, self.event_chance + (turn * 0.01))
        
        if random.random() < chance:
            return random.choice(self.events)
        return None
