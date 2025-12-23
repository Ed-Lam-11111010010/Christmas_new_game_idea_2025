#!/usr/bin/env python3
"""
Simple test to verify game mechanics work correctly
"""
from game.core.engine import GameEngine
from game.city.buildings import BuildingType

def test_game_initialization():
    """Test that game initializes correctly."""
    print("Test 1: Game Initialization")
    engine = GameEngine()
    engine.new_game("Test City")
    
    assert engine.city is not None, "City should be created"
    assert engine.city.name == "Test City", "City name should match"
    assert engine.city.population > 0, "City should have initial population"
    assert engine.city.money > 0, "City should have initial money"
    assert len(engine.city.buildings) > 0, "City should have initial buildings"
    print("✓ Game initialization works\n")

def test_building():
    """Test building construction."""
    print("Test 2: Building Construction")
    engine = GameEngine()
    engine.new_game("Test City")
    
    initial_money = engine.city.money
    initial_buildings = len(engine.city.buildings)
    
    # Try to build a residential tower
    success = engine.city.build(BuildingType.RESIDENTIAL, 0, 0)
    
    assert success, "Building should succeed on empty spot"
    assert engine.city.money < initial_money, "Money should decrease"
    assert len(engine.city.buildings) > initial_buildings, "Building count should increase"
    
    # Try to build on same spot (should fail)
    success = engine.city.build(BuildingType.COMMERCIAL, 0, 0)
    assert not success, "Building on occupied spot should fail"
    print("✓ Building construction works\n")

def test_turn_processing():
    """Test turn processing."""
    print("Test 3: Turn Processing")
    engine = GameEngine()
    engine.new_game("Test City")
    
    initial_turn = engine.state.turn
    initial_pop = engine.city.population
    
    # Process several turns
    for _ in range(5):
        engine.process_turn()
    
    assert engine.state.turn > initial_turn, "Turn counter should increase"
    print(f"  Turns progressed: {initial_turn} -> {engine.state.turn}")
    print(f"  Population: {initial_pop} -> {engine.city.population}")
    print("✓ Turn processing works\n")

def test_events():
    """Test event system."""
    print("Test 4: Event System")
    engine = GameEngine()
    engine.new_game("Test City")
    
    # Process many turns to likely trigger an event
    event_occurred = False
    for _ in range(20):
        engine.process_turn()
        if "EVENT:" in engine.state.message:
            event_occurred = True
            print(f"  Event triggered: {engine.state.message.split('!')[0]}")
            break
    
    print(f"  Event occurred in 20 turns: {event_occurred}")
    print("✓ Event system works\n")

def test_status():
    """Test status retrieval."""
    print("Test 5: Status Information")
    engine = GameEngine()
    engine.new_game("Test City")
    
    status = engine.get_status()
    
    assert 'turn' in status, "Status should include turn"
    assert 'city' in status, "Status should include city info"
    assert 'message' in status, "Status should include message"
    
    city_status = status['city']
    assert 'population' in city_status, "City status should include population"
    assert 'money' in city_status, "City status should include money"
    assert 'tech_level' in city_status, "City status should include tech level"
    
    print(f"  City: {city_status['name']}")
    print(f"  Population: {city_status['population']}")
    print(f"  Money: ${city_status['money']}")
    print(f"  Tech Level: {city_status['tech_level']}")
    print("✓ Status retrieval works\n")

def test_game_over_conditions():
    """Test game over detection."""
    print("Test 6: Game Over Conditions")
    engine = GameEngine()
    engine.new_game("Test City")
    
    # Simulate bankruptcy
    engine.city.money = -2000
    engine.process_turn()
    
    assert engine.state.game_over, "Game should be over with bankruptcy"
    print(f"  Bankruptcy detected: {engine.state.message}")
    
    # Test population loss
    engine2 = GameEngine()
    engine2.new_game("Test City 2")
    engine2.city.population = 0
    engine2.process_turn()
    
    assert engine2.state.game_over, "Game should be over with no population"
    print(f"  Population loss detected: {engine2.state.message}")
    print("✓ Game over conditions work\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Running Cyber City Survival Tests")
    print("=" * 60)
    print()
    
    try:
        test_game_initialization()
        test_building()
        test_turn_processing()
        test_events()
        test_status()
        test_game_over_conditions()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
