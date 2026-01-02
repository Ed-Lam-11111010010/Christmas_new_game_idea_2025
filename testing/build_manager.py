"""
Build Manager
Handles all building placement, upgrade, demolition, and neighbor synergy logic for City Rogue
"""

class BuildManager:
    """Manages all building-related operations and neighbor synergy bonuses"""
    
    def __init__(self, game, synergies=None):
        """
        Initialize the build manager
        
        Args:
            game: Reference to the main game object
            synergies: List of neighbor synergy rules (optional, will use default if None)
        """
        self.game = game
        self.neighbor_bonuses = {}  # Track neighbor bonuses: {(r,c): {"money": 15, "happy": 5}}
        
        # Load synergies from parameter or use default
        if synergies:
            self.neighbor_synergies = synergies
        else:
            # Default synergies (backward compatibility)
            self.neighbor_synergies = [
                {
                    "id": "shop_residential",
                    "name": "Shop + Residential Synergy",
                    "desc": "Shops and Malls gain +15 income near Houses/Apartments",
                    "building_ids": [6, 11],
                    "neighbor_ids": [1, 5],
                    "bonus": {"money": 15}
                },
                {
                    "id": "park_residential",
                    "name": "Park + Residential Synergy",
                    "desc": "Parks gain +5 happiness near Houses/Apartments",
                    "building_ids": [4, 12],
                    "neighbor_ids": [1, 5],
                    "bonus": {"happy": 5}
                },
                {
                    "id": "office_commercial",
                    "name": "Office + Commercial Synergy",
                    "desc": "Offices gain +10 income near Shops/Malls",
                    "building_ids": [2],
                    "neighbor_ids": [6, 11],
                    "bonus": {"money": 10}
                },
                {
                    "id": "factory_power",
                    "name": "Factory + Power Synergy",
                    "desc": "Factories gain +20 income near Power Plants",
                    "building_ids": [10],
                    "neighbor_ids": [3],
                    "bonus": {"money": 20}
                }
            ]
    
    def get_neighbors_coords(self, r, c):
        """
        Get coordinates of all orthogonal neighbors
        
        Args:
            r: Row position
            c: Column position
            
        Returns:
            List of (row, col) tuples for valid neighbors
        """
        from consts import GRID_SIZE
        neighbors = []
        if r > 0:
            neighbors.append((r-1, c))
        if r < GRID_SIZE - 1:
            neighbors.append((r+1, c))
        if c > 0:
            neighbors.append((r, c-1))
        if c < GRID_SIZE - 1:
            neighbors.append((r, c+1))
        return neighbors
    
    def get_neighbors(self, r, c):
        """
        Get building IDs of all neighbors
        
        Args:
            r: Row position
            c: Column position
            
        Returns:
            List of building IDs at neighbor positions
        """
        return [self.game.grid[nr][nc] for nr, nc in self.get_neighbors_coords(r, c)]
    
    def calculate_neighbor_bonus(self, r, c, b_id):
        """
        Calculate neighbor-based bonuses for a building at position (r, c)
        
        Args:
            r: Row position
            c: Column position
            b_id: Building ID
            
        Returns:
            Dictionary with bonus values {"money": X, "happy": Y}
        """
        bonuses = {}
        b = self.game.buildings[b_id]
        w, h = b["size"]
        
        # Collect all neighbors for all tiles of this building
        neighbors = []
        for dr in range(h):
            for dc in range(w):
                neighbors.extend(self.get_neighbors(r + dr, c + dc))
        
        # Apply all synergy rules
        for synergy in self.neighbor_synergies:
            if b_id in synergy["building_ids"]:
                # Check if any required neighbor is present
                if any(n_id in neighbors for n_id in synergy["neighbor_ids"]):
                    # Add bonuses
                    for bonus_type, bonus_value in synergy["bonus"].items():
                        bonuses[bonus_type] = bonuses.get(bonus_type, 0) + bonus_value
        
        return bonuses
    
    def can_place_building(self, r, c, b_id):
        """
        Check if a building can be placed at the given position
        
        Args:
            r: Row position
            c: Column position
            b_id: Building ID
            
        Returns:
            Boolean indicating if placement is valid
        """
        from consts import GRID_SIZE
        
        w, h = self.game.buildings[b_id]["size"]
        
        # Check if building fits in grid
        if r + h > GRID_SIZE or c + w > GRID_SIZE:
            return False
        
        # Check if all tiles are available
        for dr in range(h):
            for dc in range(w):
                tile = self.game.grid[r + dr][c + dc]
                if b_id == 8:  # Bridge - must be on water
                    if tile != -1:
                        return False
                else:  # Other buildings - must be on empty land
                    if tile != 0:
                        return False
        
        return True
    
    def build(self, r, c, b_id, cost, ap_cost, play_sound_func, log_func):
        """
        Build a new building at the specified position
        
        Args:
            r: Row position
            c: Column position
            b_id: Building ID
            cost: Money cost
            ap_cost: Action points cost
            play_sound_func: Function to play sound effects
            log_func: Function to log messages
            
        Returns:
            Boolean indicating if build was successful
        """
        from consts import RED
        
        if self.game.money < cost:
            play_sound_func("error")
            log_func(f"Need ${cost}!", RED)
            return False
        
        if self.game.actions < ap_cost:
            play_sound_func("error")
            log_func("Not enough Actions!", RED)
            return False
        
        self.game.money -= cost
        self.game.actions -= ap_cost
        self.force_build(r, c, b_id)
        
        from consts import GREEN
        play_sound_func("build")
        log_func(f"Built {self.game.buildings[b_id]['name']}", GREEN)
        return True
    
    def force_build(self, r, c, b_id):
        """
        Force build a building without cost checks (used for relics, etc.)
        
        Args:
            r: Row position
            c: Column position
            b_id: Building ID
        """
        w, h = self.game.buildings[b_id]["size"]
        
        # Place building on grid
        for dr in range(h):
            for dc in range(w):
                self.game.grid[r + dr][c + dc] = b_id
        
        # Calculate and store neighbor bonuses
        bonus = self.calculate_neighbor_bonus(r, c, b_id)
        if bonus:
            self.neighbor_bonuses[(r, c)] = bonus
    
    def upgrade_building(self, r, c, play_sound_func, log_func):
        """
        Upgrade a building at the given position
        
        Args:
            r: Row position
            c: Column position
            play_sound_func: Function to play sound effects
            log_func: Function to log messages
            
        Returns:
            Boolean indicating if upgrade was successful
        """
        from consts import CYAN
        
        b_id = self.game.grid[r][c]
        b_data = self.game.buildings[b_id]
        
        if not b_data["upgrade_to"]:
            return False
        
        up_id = b_data["upgrade_to"]
        up_cost = b_data["upgrade_cost"]
        
        if self.game.money < up_cost:
            return False
        
        # Preserve existing neighbor bonuses before upgrade
        old_bonus = self.neighbor_bonuses.get((r, c), {})
        
        self.game.money -= up_cost
        w, h = self.game.buildings[up_id]["size"]
        
        # Place upgraded building
        for dr in range(h):
            for dc in range(w):
                self.game.grid[r + dr][c + dc] = up_id
        
        # Recalculate bonuses after upgrade and merge with old ones
        new_bonus = self.calculate_neighbor_bonus(r, c, up_id)
        merged = old_bonus.copy()
        for key in new_bonus:
            merged[key] = merged.get(key, 0) + new_bonus[key]
        
        if merged:
            self.neighbor_bonuses[(r, c)] = merged
        
        play_sound_func("build")
        log_func(f"Upgraded!", CYAN)
        return True
    
    def demolish_building(self, r, c, total_cost_func, play_sound_func, log_func):
        """
        Demolish a building and refund 50% of total cost
        
        Args:
            r: Row position
            c: Column position
            total_cost_func: Function to calculate total building cost
            play_sound_func: Function to play sound effects
            log_func: Function to log messages
            
        Returns:
            Integer refund amount
        """
        from consts import GRAY
        
        b_id = self.game.grid[r][c]
        
        # Calculate proper refund: 50% of (building cost + all upgrade costs)
        total_cost = total_cost_func(b_id)
        refund = int(total_cost * 0.5)
        
        w, h = self.game.buildings[b_id]["size"]
        
        # Remove building from grid
        for dr in range(h):
            for dc in range(w):
                if b_id == 8:  # Bridge - restore to water
                    self.game.grid[r + dr][c + dc] = -1
                else:  # Other buildings - restore to empty
                    self.game.grid[r + dr][c + dc] = 0
        
        # Clear neighbor bonuses for this building
        if (r, c) in self.neighbor_bonuses:
            del self.neighbor_bonuses[(r, c)]
        
        self.game.money += refund
        play_sound_func("money")
        log_func(f"Sold (+${refund})", GRAY)
        
        return refund
    
    def predict_building_effects(self, r, c, b_id):
        """
        Predict the effects of placing a building (for UI preview)
        
        Args:
            r: Row position
            c: Column position
            b_id: Building ID
            
        Returns:
            List of effect strings to display
        """
        effects = []
        b = self.game.buildings[b_id]
        ap_cost = b.get("ap_cost", 0)
        
        # Check action points
        if self.game.actions < ap_cost:
            effects.append(f"⚠ Need {ap_cost} AP!")
        
        # Check road connectivity
        has_neighbor = False
        neighbors = []
        w, h = b["size"]
        
        for dr in range(h):
            for dc in range(w):
                for nr, nc in self.get_neighbors_coords(r + dr, c + dc):
                    if self.game.grid[nr][nc] > 0:
                        has_neighbor = True
                    neighbors.append(self.game.grid[nr][nc])
        
        if b["needs_road"] and not has_neighbor:
            effects.append("⚠ Disconnected")
        
        # Show neighbor synergy bonuses
        for synergy in self.neighbor_synergies:
            if b_id in synergy["building_ids"]:
                if any(n_id in neighbors for n_id in synergy["neighbor_ids"]):
                    # Show bonuses
                    bonus = synergy["bonus"]
                    if "money" in bonus:
                        effects.append(f"Combo: +{bonus['money']}💰")
                    if "happy" in bonus:
                        effects.append(f"Combo: +{bonus['happy']}😊")
        
        return effects
    
    def get_all_neighbor_bonuses(self):
        """
        Get all neighbor bonuses for saving
        
        Returns:
            Dictionary mapping position tuples to bonus dictionaries
        """
        return self.neighbor_bonuses
    
    def load_neighbor_bonuses(self, bonuses_data):
        """
        Load neighbor bonuses from saved data
        
        Args:
            bonuses_data: Dictionary with string keys like "r,c" mapping to bonus dicts
        """
        self.neighbor_bonuses = {
            tuple(map(int, k.split(","))): v 
            for k, v in bonuses_data.items()
        }
    
    def clear_neighbor_bonuses(self):
        """Clear all neighbor bonuses (used when resetting game)"""
        self.neighbor_bonuses = {}
