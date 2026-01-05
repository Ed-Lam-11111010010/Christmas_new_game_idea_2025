extends Node
class_name BuildManager
## Manages all building-related operations and neighbor synergy bonuses

const Consts = preload("res://scripts/consts.gd")

var game  # Reference to the main game
var neighbor_bonuses: Dictionary = {}  # {Vector2i(r,c): {"money": 15, "happy": 5}}
var neighbor_synergies: Array = []

func _init(game_ref, synergies = null):
	game = game_ref
	if synergies:
		neighbor_synergies = synergies
	else:
		# Default synergies (backward compatibility)
		neighbor_synergies = [
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

func get_neighbors_coords(r: int, c: int) -> Array:
	"""Get coordinates of all orthogonal neighbors"""
	var neighbors = []
	if r > 0:
		neighbors.append(Vector2i(r-1, c))
	if r < Consts.GRID_SIZE - 1:
		neighbors.append(Vector2i(r+1, c))
	if c > 0:
		neighbors.append(Vector2i(r, c-1))
	if c < Consts.GRID_SIZE - 1:
		neighbors.append(Vector2i(r, c+1))
	return neighbors

func get_neighbors(r: int, c: int) -> Array:
	"""Get building IDs of all neighbors"""
	var neighbor_ids = []
	for pos in get_neighbors_coords(r, c):
		neighbor_ids.append(game.grid[pos.x][pos.y])
	return neighbor_ids

func calculate_neighbor_bonus(r: int, c: int, b_id: int) -> Dictionary:
	"""Calculate neighbor-based bonuses for a building at position (r, c)"""
	var bonuses = {}
	var b = game.buildings[str(b_id)]
	var size = b["size"]
	var w = size[0]
	var h = size[1]
	
	# Collect all neighbors for all tiles of this building
	var neighbors = []
	for dr in range(h):
		for dc in range(w):
			neighbors.append_array(get_neighbors(r + dr, c + dc))
	
	# Apply all synergy rules
	for synergy in neighbor_synergies:
		if b_id in synergy["building_ids"]:
			# Check if any required neighbor is present
			var has_neighbor = false
			for n_id in synergy["neighbor_ids"]:
				if n_id in neighbors:
					has_neighbor = true
					break
			
			if has_neighbor:
				# Add bonuses
				for bonus_type in synergy["bonus"]:
					var bonus_value = synergy["bonus"][bonus_type]
					if bonus_type in bonuses:
						bonuses[bonus_type] += bonus_value
					else:
						bonuses[bonus_type] = bonus_value
	
	return bonuses

func can_place_building(r: int, c: int, b_id: int) -> bool:
	"""Check if a building can be placed at the given position"""
	var b = game.buildings[str(b_id)]
	var size = b["size"]
	var w = size[0]
	var h = size[1]
	
	# Check if building fits in grid
	if r + h > Consts.GRID_SIZE or c + w > Consts.GRID_SIZE:
		return false
	
	# Check if all tiles are available
	for dr in range(h):
		for dc in range(w):
			var tile = game.grid[r + dr][c + dc]
			if b_id == 8:  # Bridge - must be on water
				if tile != -1:
					return false
			else:  # Other buildings - must be on empty land
				if tile != 0:
					return false
	
	return true

func build(r: int, c: int, b_id: int, cost: int, ap_cost: int, play_sound_func: Callable, log_func: Callable) -> bool:
	"""Build a new building at the specified position"""
	if game.money < cost:
		play_sound_func.call("error")
		log_func.call("Need $%d!" % cost, Consts.RED)
		return false
	
	if game.actions < ap_cost:
		play_sound_func.call("error")
		log_func.call("Not enough Actions!", Consts.RED)
		return false
	
	game.money -= cost
	game.actions -= ap_cost
	force_build(r, c, b_id)
	
	play_sound_func.call("build")
	log_func.call("Built %s" % game.buildings[str(b_id)]["name"], Consts.GREEN)
	return true

func force_build(r: int, c: int, b_id: int) -> void:
	"""Force build a building without cost checks (used for relics, etc.)"""
	var b = game.buildings[str(b_id)]
	var size = b["size"]
	var w = size[0]
	var h = size[1]
	
	# Place building on grid
	for dr in range(h):
		for dc in range(w):
			game.grid[r + dr][c + dc] = b_id
	
	# Calculate and store neighbor bonuses
	var bonus = calculate_neighbor_bonus(r, c, b_id)
	if not bonus.is_empty():
		neighbor_bonuses[Vector2i(r, c)] = bonus

func upgrade_building(r: int, c: int, play_sound_func: Callable, log_func: Callable) -> bool:
	"""Upgrade a building at the given position"""
	var b_id = game.grid[r][c]
	var b_data = game.buildings[str(b_id)]
	
	if b_data["upgrade_to"] == null:
		return false
	
	var up_id = b_data["upgrade_to"]
	var up_cost = b_data["upgrade_cost"]
	
	if game.money < up_cost:
		return false
	
	# Preserve existing neighbor bonuses before upgrade
	var old_bonus = neighbor_bonuses.get(Vector2i(r, c), {})
	
	game.money -= up_cost
	var up_data = game.buildings[str(up_id)]
	var size = up_data["size"]
	var w = size[0]
	var h = size[1]
	
	# Place upgraded building
	for dr in range(h):
		for dc in range(w):
			game.grid[r + dr][c + dc] = up_id
	
	# Recalculate bonuses after upgrade and merge with old ones
	var new_bonus = calculate_neighbor_bonus(r, c, up_id)
	var merged = old_bonus.duplicate()
	for key in new_bonus:
		if key in merged:
			merged[key] += new_bonus[key]
		else:
			merged[key] = new_bonus[key]
	
	if not merged.is_empty():
		neighbor_bonuses[Vector2i(r, c)] = merged
	
	play_sound_func.call("build")
	log_func.call("Upgraded!", Consts.CYAN)
	return true

func demolish_building(r: int, c: int, total_cost_func: Callable, play_sound_func: Callable, log_func: Callable) -> int:
	"""Demolish a building and refund 50% of total cost"""
	var b_id = game.grid[r][c]
	
	# Calculate proper refund: 50% of (building cost + all upgrade costs)
	var total_cost = total_cost_func.call(b_id)
	var refund = int(total_cost * 0.5)
	
	var b = game.buildings[str(b_id)]
	var size = b["size"]
	var w = size[0]
	var h = size[1]
	
	# Remove building from grid
	for dr in range(h):
		for dc in range(w):
			if b_id == 8:  # Bridge - restore to water
				game.grid[r + dr][c + dc] = -1
			else:  # Other buildings - restore to empty
				game.grid[r + dr][c + dc] = 0
	
	# Clear neighbor bonuses for this building
	var key = Vector2i(r, c)
	if key in neighbor_bonuses:
		neighbor_bonuses.erase(key)
	
	game.money += refund
	play_sound_func.call("money")
	log_func.call("Sold (+$%d)" % refund, Consts.GRAY)
	
	return refund

func predict_building_effects(r: int, c: int, b_id: int) -> Array:
	"""Predict the effects of placing a building (for UI preview)"""
	var effects = []
	var b = game.buildings[str(b_id)]
	var ap_cost = b.get("ap_cost", 0)
	
	# Check action points
	if game.actions < ap_cost:
		effects.append("⚠ Need %d AP!" % ap_cost)
	
	# Check road connectivity
	var has_neighbor = false
	var neighbors = []
	var size = b["size"]
	var w = size[0]
	var h = size[1]
	
	for dr in range(h):
		for dc in range(w):
			for pos in get_neighbors_coords(r + dr, c + dc):
				if game.grid[pos.x][pos.y] > 0:
					has_neighbor = true
				neighbors.append(game.grid[pos.x][pos.y])
	
	if b["needs_road"] and not has_neighbor:
		effects.append("⚠ Disconnected")
	
	# Show neighbor synergy bonuses
	for synergy in neighbor_synergies:
		if b_id in synergy["building_ids"]:
			var has_synergy_neighbor = false
			for n_id in synergy["neighbor_ids"]:
				if n_id in neighbors:
					has_synergy_neighbor = true
					break
			
			if has_synergy_neighbor:
				var bonus = synergy["bonus"]
				if "money" in bonus:
					effects.append("Combo: +%d💰" % bonus["money"])
				if "happy" in bonus:
					effects.append("Combo: +%d😊" % bonus["happy"])
	
	return effects

func get_all_neighbor_bonuses() -> Dictionary:
	"""Get all neighbor bonuses for saving"""
	return neighbor_bonuses

func load_neighbor_bonuses(bonuses_data: Dictionary) -> void:
	"""Load neighbor bonuses from saved data"""
	neighbor_bonuses.clear()
	for key_str in bonuses_data:
		var parts = key_str.split(",")
		if parts.size() >= 2:
			var r = parts[0].to_int()
			var c = parts[1].to_int()
			neighbor_bonuses[Vector2i(r, c)] = bonuses_data[key_str]

func clear_neighbor_bonuses() -> void:
	"""Clear all neighbor bonuses (used when resetting game)"""
	neighbor_bonuses.clear()
