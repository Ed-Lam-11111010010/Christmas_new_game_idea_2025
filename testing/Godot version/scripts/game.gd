extends Node2D
## Main game script for City Rogue

# Autoload references
var Consts = preload("res://scripts/consts.gd").new()

# Managers
var event_log: EventLogManager
var build_mgr: BuildManager

# Game State
var state: int = Consts.GameState.MENU
var difficulty: String = "Normal"
var relic: Dictionary = {}

# Resources
var buildings: Dictionary = {}
var relics: Array = []
var events: Array = []
var milestones_data: Array = []

# Game Variables
var grid: Array = []
var network_map: Dictionary = {}
var island_stats: Dictionary = {}
var active_road_tiles: Array = []
var active_buildings: Array = []

var money: int = 500
var actions: int = 3
var max_actions: int = 3
var energy: int = 10
var population: int = 0
var jobs_total: int = 0
var happiness: int = 60
var round_num: int = 1

var selected_building: int = 1
var active_events: Array = []
var unlocked_milestones: Array = []
var drawn_event_ids: Array = []

var mods: Dictionary = {
	"cost_mult": 1.0,
	"pop_flat": 0,
	"money_mult": 1.0,
	"energy_flat": 0,
	"happy_flat": 0,
	"action_mod": 0
}

var prev_pop: int = 0
var prev_happy: int = 60
var prev_energy: int = 10

var game_over: bool = false
var win: bool = false

# Camera variables
var cam_offset: Vector2 = Vector2.ZERO
var zoom_level: float = 1.0
var dragging: bool = false
var last_mouse_pos: Vector2 = Vector2.ZERO

# Popup
var popup_active: bool = false
var popup_coords: Vector2i = Vector2i(-1, -1)
var popup_queue: Array = []

# High Scores
var high_scores: Array = []

# Settings
var volume: float = 0.5
var resolutions: Array = [Vector2i(950, 650), Vector2i(1280, 720), Vector2i(1600, 900)]
var res_index: int = 0

# Sounds
var sounds: Dictionary = {}

# UI references (will be set by UI nodes)
var ui_layer: CanvasLayer

func _ready():
	randomize()
	
	# Initialize managers
	event_log = EventLogManager.new()
	add_child(event_log)
	
	load_settings()
	load_game_data()
	
	# Initialize BuildManager after loading game data
	var synergies = null
	if "neighbor_synergies" in buildings:
		synergies = buildings["neighbor_synergies"]
	build_mgr = BuildManager.new(self, synergies)
	add_child(build_mgr)
	
	load_sounds()
	high_scores = load_scores()
	
	reset_game_data()
	
	# Setup UI (create UI layer dynamically)
	create_ui()

func create_ui():
	"""Create the UI layer and all UI elements"""
	ui_layer = CanvasLayer.new()
	add_child(ui_layer)
	
	# UI will be drawn using custom rendering
	# For now, we'll use a Control node for input handling
	var ui_control = Control.new()
	ui_control.set_anchors_preset(Control.PRESET_FULL_RECT)
	ui_control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_layer.add_child(ui_control)

func _input(event):
	if event is InputEventMouseButton:
		if event.pressed:
			handle_mouse_down(event.position)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			dragging = false
	
	if event is InputEventMouseMotion:
		handle_mouse_move(event.position)
	
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP and state == Consts.GameState.GAME:
			zoom_level = clampf(zoom_level + 0.1, 0.5, 2.0)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and state == Consts.GameState.GAME:
			zoom_level = clampf(zoom_level - 0.1, 0.5, 2.0)
	
	if event is InputEventKey and event.pressed:
		handle_keys(event)

func _process(_delta):
	queue_redraw()

func _draw():
	match state:
		Consts.GameState.MENU:
			draw_menu()
		Consts.GameState.RELIC:
			draw_relic_screen()
		Consts.GameState.SETTINGS:
			draw_settings()
		Consts.GameState.GAME:
			draw_game()
		Consts.GameState.GAMEOVER:
			draw_gameover()

# ===== GAME DATA MANAGEMENT =====

func load_game_data():
	"""Load buildings, relics, events from JSON"""
	var file = FileAccess.open(Consts.DATA_FILE, FileAccess.READ)
	if file:
		var json = JSON.new()
		var parse_result = json.parse(file.get_as_text())
		if parse_result == OK:
			var data = json.data
			buildings = data.get("buildings", {})
			relics = data.get("relics", [])
			events = data.get("events", [])
			milestones_data = data.get("milestones", [])
		file.close()

func load_settings():
	"""Load settings from file"""
	if FileAccess.file_exists(Consts.SETTINGS_FILE):
		var file = FileAccess.open(Consts.SETTINGS_FILE, FileAccess.READ)
		if file:
			var json = JSON.new()
			var parse_result = json.parse(file.get_as_text())
			if parse_result == OK:
				var data = json.data
				volume = data.get("volume", 0.5)
				res_index = data.get("res_index", 0)
			file.close()

func save_settings():
	"""Save settings to file"""
	var file = FileAccess.open(Consts.SETTINGS_FILE, FileAccess.WRITE)
	if file:
		var data = {"volume": volume, "res_index": res_index}
		file.store_string(JSON.stringify(data))
		file.close()

func load_sounds():
	"""Load sound effects"""
	# Note: In Godot, you'll need to add AudioStreamPlayer nodes or load audio files
	# For now, this is a placeholder
	pass

func play_sound(sound_name: String):
	"""Play a sound effect"""
	# Placeholder - implement with AudioStreamPlayer nodes
	pass

func load_scores() -> Array:
	"""Load high scores from file"""
	if FileAccess.file_exists(Consts.SCORE_FILE):
		var file = FileAccess.open(Consts.SCORE_FILE, FileAccess.READ)
		if file:
			var json = JSON.new()
			var parse_result = json.parse(file.get_as_text())
			if parse_result == OK:
				file.close()
				return json.data
			file.close()
	return []

func save_high_score():
	"""Save current game as high score"""
	var score = int(max(0, money) + (population * 10) + (happiness * 5) + (round_num * 20))
	var entry = {
		"score": score,
		"status": "Victory" if win else "Round %d" % round_num,
		"date": Time.get_datetime_string_from_system()
	}
	high_scores.append(entry)
	high_scores.sort_custom(func(a, b): return a["score"] > b["score"])
	high_scores = high_scores.slice(0, 5)
	
	var file = FileAccess.open(Consts.SCORE_FILE, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(high_scores))
		file.close()

func save_game():
	"""Save current game state"""
	var serial_logs = []
	for log in event_log.get_all_logs():
		serial_logs.append([log[0], [log[1].r, log[1].g, log[1].b]])
	
	var rid = relic.get("id", null)
	var nb = build_mgr.get_all_neighbor_bonuses()
	var nb_serialized = {}
	for pos in nb:
		nb_serialized["%d,%d" % [pos.x, pos.y]] = nb[pos]
	
	var data = {
		"grid": grid,
		"money": money,
		"actions": actions,
		"max_actions": max_actions,
		"energy": energy,
		"round": round_num,
		"difficulty": difficulty,
		"active_events": active_events,
		"mods": mods,
		"logs": serial_logs,
		"relic_id": rid,
		"unlocked_milestones": unlocked_milestones,
		"drawn_event_ids": drawn_event_ids,
		"neighbor_bonuses": nb_serialized
	}
	
	var file = FileAccess.open(Consts.SAVE_FILE, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data))
		file.close()

func load_game_from_file():
	"""Load saved game"""
	if not FileAccess.file_exists(Consts.SAVE_FILE):
		log_message("No save file found.", Consts.RED)
		return
	
	# Safety check for managers
	if not event_log or not build_mgr:
		print("Error: Managers not initialized")
		return
	
	var file = FileAccess.open(Consts.SAVE_FILE, FileAccess.READ)
	if file:
		var json = JSON.new()
		var parse_result = json.parse(file.get_as_text())
		if parse_result == OK:
			var data = json.data
			grid = data["grid"]
			money = data["money"]
			actions = data.get("actions", 3)
			max_actions = data.get("max_actions", 3)
			energy = data["energy"]
			round_num = data["round"]
			difficulty = data["difficulty"]
			active_events = data["active_events"]
			mods = data["mods"]
			event_log.load_logs(data["logs"])
			
			var rid = data.get("relic_id")
			if rid:
				for r in relics:
					if r["id"] == rid:
						relic = r
						break
			
			unlocked_milestones = data.get("unlocked_milestones", [])
			drawn_event_ids = data.get("drawn_event_ids", [])
			
			var nb_data = data.get("neighbor_bonuses", {})
			build_mgr.load_neighbor_bonuses(nb_data)
			
			recalc_stats()
			state = Consts.GameState.GAME
			log_message("Game Loaded.", Consts.GREEN)
			file.close()
		else:
			print("Error parsing save file")
			file.close()
	else:
		print("Error opening save file")

func delete_save():
	"""Delete save file"""
	if FileAccess.file_exists(Consts.SAVE_FILE):
		DirAccess.remove_absolute(Consts.SAVE_FILE)

func reset_game_data():
	"""Reset all game state for new game"""
	grid = []
	for _r in range(Consts.GRID_SIZE):
		var row = []
		for _c in range(Consts.GRID_SIZE):
			row.append(0)
		grid.append(row)
	
	network_map.clear()
	island_stats.clear()
	active_road_tiles.clear()
	active_buildings.clear()
	
	if build_mgr:
		build_mgr.clear_neighbor_bonuses()
	
	unlocked_milestones.clear()
	drawn_event_ids.clear()
	
	generate_river()
	
	money = 500 if difficulty == "Normal" else 350
	actions = 3
	max_actions = 3
	energy = 10
	population = 0
	jobs_total = 0
	happiness = 60
	round_num = 1
	game_over = false
	win = false
	selected_building = 1
	relic = {}
	
	popup_queue.clear()
	active_events.clear()
	mods = {
		"cost_mult": 1.0,
		"pop_flat": 0,
		"money_mult": 1.0,
		"energy_flat": 0,
		"happy_flat": 0,
		"action_mod": 0
	}
	
	popup_active = false
	popup_coords = Vector2i(-1, -1)
	event_log.clear()
	prev_pop = 0
	prev_happy = 60
	prev_energy = 10
	
	log_message("Welcome Mayor!", Consts.WHITE)
	recalc_stats()

func generate_river():
	"""Generate random rivers on the map"""
	for i in range(2):
		var r = randi() % Consts.GRID_SIZE
		var c = 0
		grid[r][c] = -1
		
		while c < Consts.GRID_SIZE - 1:
			var moves = [[0, 1], [0, 1], [-1, 0], [1, 0]]
			var move = moves[randi() % moves.size()]
			r += move[0]
			c += move[1]
			
			if r >= 0 and r < Consts.GRID_SIZE and c >= 0 and c < Consts.GRID_SIZE:
				grid[r][c] = -1
			else:
				break

# ===== GAME LOGIC =====

func log_message(text: String, color: Color = Consts.WHITE):
	"""Add log message"""
	event_log.log(text, color)

func screen_to_world(screen_pos: Vector2) -> Vector2i:
	"""Convert screen position to grid coordinates"""
	var world_x = (screen_pos.x / zoom_level) + cam_offset.x
	var world_y = (screen_pos.y / zoom_level) + cam_offset.y
	return Vector2i(int(world_y / Consts.TILE_SIZE), int(world_x / Consts.TILE_SIZE))

func get_cost(b_id: int) -> int:
	"""Calculate cost of building with modifiers"""
	var b_data = buildings[str(b_id)]
	var base = b_data["cost"]
	if base == 0:
		return 0
	
	if relic:
		if relic.get("id") == "industrialist" and b_id == 3:
			return 50
		if relic.get("id") == "tycoon":
			base = int(base * 1.2)
	
	return int(base * mods["cost_mult"])

func get_building_total_cost(b_id: int) -> int:
	"""Calculate total cost including upgrade chain"""
	var total = get_cost(b_id)
	for check_id in buildings:
		var data = buildings[check_id]
		if data.get("upgrade_to") == b_id:
			total += get_cost(int(check_id))
			total += data.get("upgrade_cost", 0)
			var parent_total = get_building_total_cost(int(check_id))
			if parent_total > get_cost(int(check_id)):
				total = parent_total + data.get("upgrade_cost", 0)
			break
	return total

func can_place_building(r: int, c: int, b_id: int) -> bool:
	"""Check if building can be placed"""
	return build_mgr.can_place_building(r, c, b_id)

func build(r: int, c: int):
	"""Build a building"""
	var b_id = selected_building
	var cost = get_cost(b_id)
	var ap_cost = buildings[str(b_id)].get("ap_cost", 0)
	var success = build_mgr.build(r, c, b_id, cost, ap_cost, play_sound, log_message)
	if success:
		recalc_stats()

func force_build(r: int, c: int, b_id: int):
	"""Force build without checks"""
	build_mgr.force_build(r, c, b_id)
	recalc_stats()

func upgrade_building():
	"""Upgrade selected building"""
	var r = popup_coords.x
	var c = popup_coords.y
	var success = build_mgr.upgrade_building(r, c, play_sound, log_message)
	if success:
		recalc_stats()
		popup_active = false

func demolish_building():
	"""Demolish selected building"""
	var r = popup_coords.x
	var c = popup_coords.y
	build_mgr.demolish_building(r, c, get_building_total_cost, play_sound, log_message)
	popup_active = false
	recalc_stats()

func update_road_networks():
	"""Update network connections and island statistics"""
	network_map.clear()
	island_stats.clear()
	active_road_tiles.clear()
	active_buildings.clear()
	
	var visited = {}
	var nid = 1
	
	for r in range(Consts.GRID_SIZE):
		for c in range(Consts.GRID_SIZE):
			var key = Vector2i(r, c)
			if grid[r][c] > 0 and not visited.has(key):
				var queue = [key]
				visited[key] = true
				network_map[key] = nid
				
				while queue.size() > 0:
					var curr = queue.pop_front()
					for neighbor_pos in build_mgr.get_neighbors_coords(curr.x, curr.y):
						if grid[neighbor_pos.x][neighbor_pos.y] > 0 and not visited.has(neighbor_pos):
							visited[neighbor_pos] = true
							network_map[neighbor_pos] = nid
							queue.append(neighbor_pos)
				nid += 1
	
	var processed = {}
	for r in range(Consts.GRID_SIZE):
		for c in range(Consts.GRID_SIZE):
			var key = Vector2i(r, c)
			if processed.has(key):
				continue
			
			var b_id = grid[r][c]
			if b_id > 0:
				var iid = network_map.get(key)
				if not iid:
					continue
				
				if not island_stats.has(iid):
					island_stats[iid] = {"pop": 0, "jobs": 0, "active": false}
				
				var b = buildings[str(b_id)]
				var size = b["size"]
				var w = size[0]
				var h = size[1]
				
				for dr in range(h):
					for dc in range(w):
						processed[Vector2i(r+dr, c+dc)] = true
				
				var pop_gain = max(0, b["pop"] + (mods["pop_flat"] if b["pop"] > 0 else 0))
				island_stats[iid]["pop"] += pop_gain
				island_stats[iid]["jobs"] += b["work"]
				
				if pop_gain > 0 or b["work"] > 0:
					island_stats[iid]["active"] = true
	
	for coord in network_map:
		var iid = network_map[coord]
		if grid[coord.x][coord.y] in [7, 8]:
			if island_stats[iid]["active"]:
				active_road_tiles.append(coord)
		else:
			active_buildings.append(coord)

func recalc_stats():
	"""Recalculate all game statistics"""
	update_road_networks()
	
	var total_pop = 0
	var total_jobs = 0
	var raw_happy = 50 + mods["happy_flat"]
	
	if relic and relic.get("id") == "ecotopia":
		raw_happy += 10
	
	var processed = {}
	for r in range(Consts.GRID_SIZE):
		for c in range(Consts.GRID_SIZE):
			var key = Vector2i(r, c)
			if processed.has(key):
				continue
			
			var b_id = grid[r][c]
			if b_id > 0:
				var b = buildings[str(b_id)]
				var size = b["size"]
				var w = size[0]
				var h = size[1]
				
				for dr in range(h):
					for dc in range(w):
						processed[Vector2i(r+dr, c+dc)] = true
				
				var iid = network_map.get(key)
				var is_valid = false
				
				if iid and island_stats.has(iid) and island_stats[iid]["pop"] > 0:
					is_valid = true
				elif b["pop"] > 0:
					is_valid = true
				
				if is_valid:
					total_pop += max(0, b["pop"] + (mods["pop_flat"] if b["pop"] > 0 else 0))
					total_jobs += b["work"]
				
				raw_happy += b["happy"]
				
				if b["needs_road"] and not is_valid:
					raw_happy -= 5
				
				# Apply neighbor happiness bonuses
				var nb_bonuses = build_mgr.neighbor_bonuses
				if nb_bonuses.has(key):
					var nb = nb_bonuses[key]
					raw_happy += nb.get("happy", 0)
	
	population = total_pop
	jobs_total = total_jobs
	happiness = clampi(raw_happy, 0, 100)

func calculate_turn_income() -> Array:
	"""Calculate money and energy changes for the turn"""
	var money_change = 0
	var energy_change = 0
	var happy_mult = 1.0
	
	if happiness >= 80:
		happy_mult = 1.2
	elif happiness <= 30:
		happy_mult = 0.5
	
	var processed = {}
	for r in range(Consts.GRID_SIZE):
		for c in range(Consts.GRID_SIZE):
			var key = Vector2i(r, c)
			if processed.has(key):
				continue
			
			var b_id = grid[r][c]
			if b_id > 0:
				var b = buildings[str(b_id)]
				var size = b["size"]
				var w = size[0]
				var h = size[1]
				
				for dr in range(h):
					for dc in range(w):
						processed[Vector2i(r+dr, c+dc)] = true
				
				var iid = network_map.get(key)
				if not iid:
					continue
				
				var istats = island_stats.get(iid)
				if not istats:
					continue
				
				var local_eff = 1.0
				if b["work"] > 0:
					if istats["pop"] > 0:
						local_eff = min(1.0, float(istats["pop"]) / float(istats["jobs"]))
					else:
						local_eff = 0
				
				var gain = float(b["money"])
				if gain > 0:
					gain = gain * local_eff * happy_mult
				
				# Apply neighbor bonuses
				var nb_bonuses = build_mgr.neighbor_bonuses
				if nb_bonuses.has(key):
					var nb = nb_bonuses[key]
					gain += nb.get("money", 0)
				
				money_change += gain
				energy_change += b["energy"] * local_eff
	
	return [int(money_change), int(energy_change)]

func check_milestones(income: int):
	"""Check and unlock milestones"""
	for m in milestones_data:
		var mid = m["id"]
		if mid not in unlocked_milestones:
			var fulfilled = false
			if m["cond"] == "income" and income >= m["val"]:
				fulfilled = true
			elif m["cond"] == "pop" and population >= m["val"]:
				fulfilled = true
			elif m["cond"] == "happy" and happiness >= m["val"]:
				fulfilled = true
			
			if fulfilled:
				unlocked_milestones.append(mid)
				popup_queue.append(["🏆 %s!" % m["name"], "Reward: %s" % m["desc"], Consts.GOLD])
				play_sound("build")
				
				if m["reward"] == "action_max":
					max_actions += m["amt"]
					actions += m["amt"]

func next_turn():
	"""Advance to next turn"""
	if game_over:
		return
	
	popup_active = false
	play_sound("money")
	actions = max_actions
	
	# Random event every 5 rounds
	if round_num % 5 == 0 and round_num < Consts.MAX_ROUNDS:
		var pool = []
		for e in events:
			if e["id"] not in drawn_event_ids:
				pool.append(e)
		
		if pool.size() > 0:
			var event = pool[randi() % pool.size()]
			drawn_event_ids.append(event["id"])
			active_events.append(event)
			
			match event["type"]:
				"cost":
					mods["cost_mult"] *= event["val"]
				"pop_mod":
					mods["pop_flat"] += event["val"]
				"money_mult":
					mods["money_mult"] *= event["val"]
				"energy_flat":
					mods["energy_flat"] += event["val"]
				"happy_flat":
					mods["happy_flat"] += event["val"]
				"action_mod":
					mods["action_mod"] += event["val"]
					max_actions += int(event["val"])
			
			popup_queue.append(["⚠ %s" % event["name"], event["desc"], Consts.PURPLE])
			log_message("⚠ EVENT: %s" % event["name"], Consts.PURPLE)
	
	recalc_stats()
	var turn_result = calculate_turn_income()
	var money_change = turn_result[0]
	var energy_change = turn_result[1]
	
	money += money_change
	energy = 10 + energy_change
	round_num += 1
	
	var d_pop = population - prev_pop
	var d_happy = happiness - prev_happy
	
	log_message("Round %d: %+d💰 | En: %+d⚡" % [round_num-1, money_change, energy_change], Consts.CYAN)
	log_message("Pop: %+d👥 | Happy: %+d😊" % [d_pop, d_happy], Consts.WHITE)
	
	if happiness < 40:
		log_message("⚠ Citizens Unhappy!", Consts.RED)
	if energy < 0:
		log_message("⚠ Power Shortage!", Consts.RED)
	if population < jobs_total:
		log_message("⚠ Citizens Shortage!", Consts.RED)
	
	prev_pop = population
	prev_happy = happiness
	
	check_milestones(money_change)
	
	if money < 0 or round_num > Consts.MAX_ROUNDS:
		game_over = true
		win = (money >= 0)
		save_high_score()
		delete_save()
		state = Consts.GameState.GAMEOVER
	else:
		save_game()

# ===== INPUT HANDLING =====

func handle_mouse_down(pos: Vector2):
	match state:
		Consts.GameState.MENU:
			handle_menu_click(pos)
		Consts.GameState.RELIC:
			handle_relic_click(pos)
		Consts.GameState.SETTINGS:
			handle_settings_click(pos)
		Consts.GameState.GAMEOVER:
			handle_gameover_click(pos)
		Consts.GameState.GAME:
			handle_game_click(pos)

func handle_mouse_move(pos: Vector2):
	if state == Consts.GameState.GAME and dragging:
		var dx = pos.x - last_mouse_pos.x
		var dy = pos.y - last_mouse_pos.y
		cam_offset.x -= dx / zoom_level
		cam_offset.y -= dy / zoom_level
		last_mouse_pos = pos

func handle_keys(event: InputEventKey):
	if state == Consts.GameState.GAME:
		if popup_queue.size() > 0:
			popup_queue.pop_front()
			return
		
		var key_map = {
			KEY_1: 1, KEY_2: 2, KEY_3: 3, KEY_4: 4,
			KEY_5: 6, KEY_6: 9, KEY_7: 10, KEY_8: 7, KEY_9: 8
		}
		
		if event.keycode in key_map:
			selected_building = key_map[event.keycode]
			play_sound("select")
		
		if event.keycode == KEY_SPACE and not popup_active:
			next_turn()
		
		if event.keycode == KEY_ESCAPE:
			if not game_over:
				save_game()
			state = Consts.GameState.MENU
	
	if state == Consts.GameState.SETTINGS:
		if event.keycode == KEY_ESCAPE:
			state = Consts.GameState.MENU

func handle_menu_click(pos: Vector2):
	# Menu buttons
	var buttons_y = [150, 220, 290, 360]  # NEW GAME, LOAD GAME, SETTINGS, QUIT
	for i in range(buttons_y.size()):
		var btn_rect = Rect2(50, buttons_y[i], 200, 50)
		if btn_rect.has_point(pos):
			match i:
				0:  # NEW GAME
					reset_game_data()
					state = Consts.GameState.RELIC
				1:  # LOAD GAME
					if FileAccess.file_exists(Consts.SAVE_FILE):
						load_game_from_file()
					else:
						log_message("No save file found!", Consts.RED)
				2:  # SETTINGS
					state = Consts.GameState.SETTINGS
				3:  # QUIT
					get_tree().quit()
			return

func handle_relic_click(pos: Vector2):
	var viewport_size = get_viewport().get_visible_rect().size
	
	# Check each relic button
	for i in range(relics.size()):
		var r = relics[i]
		var rect_pos = Vector2(viewport_size.x/2 - 200, 150 + i * 120)
		var rect_size = Vector2(400, 100)
		var btn_rect = Rect2(rect_pos, rect_size)
		
		if btn_rect.has_point(pos):
			# Select this relic
			relic = r
			money = 500
			
			if relic.get("id") == "tycoon":
				money = 1000
			elif relic.get("id") == "planner":
				money = 600
				force_build(17, 14, 7)
				force_build(17, 15, 7)
				force_build(17, 16, 7)
				force_build(17, 17, 7)
				force_build(16, 12, 1)
				force_build(16, 18, 1)
			
			var color_arr = relic["color"]
			var color = Color(color_arr[0]/255.0, color_arr[1]/255.0, color_arr[2]/255.0)
			log_message("Relic: %s" % relic["name"], color)
			recalc_stats()
			state = Consts.GameState.GAME
			return

func handle_settings_click(pos: Vector2):
	var viewport_size = get_viewport().get_visible_rect().size
	
	# Difficulty buttons (Normal / Hard)
	var btn_normal = Rect2(200, 200, 150, 50)
	var btn_hard = Rect2(370, 200, 150, 50)
	
	if btn_normal.has_point(pos):
		difficulty = "Normal"
		save_settings()
		play_sound("select")
		return
	
	if btn_hard.has_point(pos):
		difficulty = "Hard"
		save_settings()
		play_sound("select")
		return
	
	# Volume buttons (-, +)
	var btn_vol_minus = Rect2(200, 280, 50, 50)
	var btn_vol_plus = Rect2(470, 280, 50, 50)
	
	if btn_vol_minus.has_point(pos):
		volume = clampf(volume - 0.1, 0.0, 1.0)
		save_settings()
		play_sound("select")
		return
	
	if btn_vol_plus.has_point(pos):
		volume = clampf(volume + 0.1, 0.0, 1.0)
		save_settings()
		play_sound("select")
		return
	
	# Resolution buttons (-, +)
	var btn_res_minus = Rect2(200, 360, 50, 50)
	var btn_res_plus = Rect2(470, 360, 50, 50)
	
	if btn_res_minus.has_point(pos):
		res_index = clampi(res_index - 1, 0, resolutions.size() - 1)
		get_window().set_size(resolutions[res_index])
		save_settings()
		play_sound("select")
		return
	
	if btn_res_plus.has_point(pos):
		res_index = clampi(res_index + 1, 0, resolutions.size() - 1)
		get_window().set_size(resolutions[res_index])
		save_settings()
		play_sound("select")
		return

func handle_gameover_click(pos: Vector2):
	var viewport_size = get_viewport().get_visible_rect().size
	
	# RESTART button
	var btn_restart = Rect2(viewport_size.x/2 - 100, 350, 200, 50)
	if btn_restart.has_point(pos):
		reset_game_data()
		state = Consts.GameState.RELIC
		return
	
	# MENU button
	var btn_menu = Rect2(viewport_size.x/2 - 100, 420, 200, 50)
	if btn_menu.has_point(pos):
		state = Consts.GameState.MENU
		return

func handle_game_click(pos: Vector2):
	if popup_queue.size() > 0:
		popup_queue.pop_front()
		return
	
	# Handle building popup clicks
	if popup_active:
		var pr = popup_coords.x
		var pc = popup_coords.y
		
		if pr >= 0 and pc >= 0 and pr < Consts.GRID_SIZE and pc < Consts.GRID_SIZE:
			var b_id = grid[pr][pc]
			if b_id > 0:
				var b = buildings[str(b_id)]
				var viewport_size = get_viewport().get_visible_rect().size
				
				# Calculate popup position
				var world_pos = Vector2(pc * Consts.TILE_SIZE, pr * Consts.TILE_SIZE)
				var screen_pos = (world_pos - cam_offset) * zoom_level
				var px = clampf(screen_pos.x + 20, 10, viewport_size.x - 310)
				var py = clampf(screen_pos.y, 10, viewport_size.y - 150)
				
				var y_offset = py + 10
				
				# Check upgrade button click
				if b.get("upgrade_to"):
					var upgrade_rect = Rect2(px + 30, y_offset, 120, 25)
					if upgrade_rect.has_point(pos):
						upgrade_building()
						return
					y_offset += 30
				
				# Check sell button click
				var sell_rect = Rect2(px + 30, y_offset, 120, 25)
				if sell_rect.has_point(pos):
					demolish_building()
					return
				
				# Check close button click
				var close_rect = Rect2(px + 135, py - 10, 20, 20)
				if close_rect.has_point(pos):
					popup_active = false
					return
		return
	
	# Check for UI clicks
	var viewport_size = get_viewport().get_visible_rect().size
	
	# Sidebar click
	if pos.x > viewport_size.x - 280:
		handle_sidebar_click(pos)
		return
	
	# Map click
	var grid_pos = screen_to_world(pos)
	var r = grid_pos.x
	var c = grid_pos.y
	
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		dragging = true
		last_mouse_pos = pos
		return
	
	if r >= 0 and r < Consts.GRID_SIZE and c >= 0 and c < Consts.GRID_SIZE:
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
			if grid[r][c] in [0, -1]:
				if can_place_building(r, c, selected_building):
					build(r, c)
				else:
					play_sound("error")
					log_message("Invalid placement!", Consts.RED)
			else:
				popup_active = true
				popup_coords = Vector2i(r, c)
				
				# Adjust for 2x2 buildings
				var b_size = buildings[str(grid[r][c])]["size"]
				if b_size == [2, 2]:
					if r > 0 and grid[r-1][c] == grid[r][c]:
						popup_coords = Vector2i(r-1, c)
					if c > 0 and grid[r][c-1] == grid[r][c]:
						popup_coords = Vector2i(r, c-1)
					if r > 0 and c > 0 and grid[r-1][c-1] == grid[r][c]:
						popup_coords = Vector2i(r-1, c-1)
				
				play_sound("select")

func handle_sidebar_click(pos: Vector2):
	# Building selection buttons
	var viewport_size = get_viewport().get_visible_rect().size
	var sidebar_x = viewport_size.x - 280
	
	# Next turn button
	var btn_next = Rect2(sidebar_x + 20, viewport_size.y - 80, 240, 50)
	if btn_next.has_point(pos):
		next_turn()
		return
	
	# Building buttons (arranged in grid)
	var building_keys = [1, 2, 3, 4, 6, 9, 10, 7, 8]
	
	# Calculate button start Y position to match draw_game_ui
	# Stats take ~180px, then "BUILDINGS:" label adds ~50px
	var btn_start_y = 230
	
	for i in range(building_keys.size()):
		var b_id = building_keys[i]
		var btn_x = sidebar_x + 20 + (i % 4) * 60
		var btn_y = btn_start_y + int(i / 4) * 60
		var btn_rect = Rect2(btn_x, btn_y, 50, 50)
		
		if btn_rect.has_point(pos):
			selected_building = b_id
			play_sound("select")
			return

# ===== RENDERING =====

func draw_menu():
	# Clear screen
	draw_rect(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size), Consts.UI_BG)
	
	# Draw title
	var title = "CITY ROGUE"
	draw_string(ThemeDB.fallback_font, Vector2(50, 80), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Consts.WHITE)
	draw_string(ThemeDB.fallback_font, Vector2(50, 110), "v3.13.1", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.GRAY)
	
	# Draw buttons
	var buttons = ["NEW GAME", "LOAD GAME", "SETTINGS", "QUIT"]
	for i in range(buttons.size()):
		var btn_rect = Rect2(50, 150 + i * 70, 200, 50)
		draw_rect(btn_rect, Consts.DARK_GRAY)
		draw_string(ThemeDB.fallback_font, Vector2(70, 180 + i * 70), buttons[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	# Draw leaderboard
	draw_leaderboard(Vector2(400, 150))

func draw_leaderboard(pos: Vector2):
	var lb_size = Vector2(500, 350)
	draw_rect(Rect2(pos, lb_size), Color(0.08, 0.08, 0.1))
	draw_rect(Rect2(pos, lb_size), Consts.GOLD, false, 2)
	
	draw_string(ThemeDB.fallback_font, pos + Vector2(20, 40), "TOP MAYORS", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Consts.GOLD)
	
	for i in range(high_scores.size()):
		var score = high_scores[i]
		var text = "%d. %d - %s (%s)" % [i+1, score["score"], score["status"], score["date"]]
		draw_string(ThemeDB.fallback_font, pos + Vector2(30, 100 + i * 40), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Consts.WHITE)

func draw_relic_screen():
	draw_rect(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size), Consts.UI_BG)
	
	var viewport_size = get_viewport().get_visible_rect().size
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 150, 80), "CHOOSE RELIC", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Consts.WHITE)
	
	for i in range(relics.size()):
		var r = relics[i]
		var rect_pos = Vector2(viewport_size.x/2 - 200, 150 + i * 120)
		var rect_size = Vector2(400, 100)
		draw_rect(Rect2(rect_pos, rect_size), Consts.DARK_GRAY)
		
		var color_arr = r["color"]
		var color = Color(color_arr[0]/255.0, color_arr[1]/255.0, color_arr[2]/255.0)
		draw_rect(Rect2(rect_pos, rect_size), color, false, 2)
		
		draw_string(ThemeDB.fallback_font, rect_pos + Vector2(20, 30), r["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, color)
		draw_string(ThemeDB.fallback_font, rect_pos + Vector2(20, 60), r["desc"], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Consts.WHITE)

func draw_settings():
	draw_rect(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size), Consts.UI_BG)
	
	var viewport_size = get_viewport().get_visible_rect().size
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 100, 80), "SETTINGS", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Consts.WHITE)
	
	# Difficulty setting
	draw_string(ThemeDB.fallback_font, Vector2(100, 180), "Difficulty:", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	var btn_normal = Rect2(200, 200, 150, 50)
	var btn_hard = Rect2(370, 200, 150, 50)
	
	var normal_color = Consts.GREEN if difficulty == "Normal" else Consts.DARK_GRAY
	var hard_color = Consts.RED if difficulty == "Hard" else Consts.DARK_GRAY
	
	draw_rect(btn_normal, normal_color)
	draw_string(ThemeDB.fallback_font, Vector2(240, 230), "Normal", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	draw_rect(btn_hard, hard_color)
	draw_string(ThemeDB.fallback_font, Vector2(420, 230), "Hard", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	# Volume setting
	draw_string(ThemeDB.fallback_font, Vector2(100, 260), "Volume:", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	var btn_vol_minus = Rect2(200, 280, 50, 50)
	var btn_vol_plus = Rect2(470, 280, 50, 50)
	
	draw_rect(btn_vol_minus, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(218, 310), "-", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	draw_string(ThemeDB.fallback_font, Vector2(280, 310), "%.0f%%" % (volume * 100), HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	draw_rect(btn_vol_plus, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(488, 310), "+", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	# Resolution setting
	draw_string(ThemeDB.fallback_font, Vector2(100, 340), "Resolution:", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	var btn_res_minus = Rect2(200, 360, 50, 50)
	var btn_res_plus = Rect2(470, 360, 50, 50)
	
	draw_rect(btn_res_minus, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(218, 390), "-", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	var res = resolutions[res_index]
	draw_string(ThemeDB.fallback_font, Vector2(280, 390), "%dx%d" % [res.x, res.y], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.WHITE)
	
	draw_rect(btn_res_plus, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(488, 390), "+", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	# Instructions
	draw_string(ThemeDB.fallback_font, Vector2(100, 480), "Press ESC to return", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.GRAY)

func draw_game():
	# Draw background
	draw_rect(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size), Consts.UI_BG)
	
	# Draw grid
	draw_grid()
	
	# Draw UI
	draw_game_ui()
	
	# Draw building popup if active
	if popup_active:
		draw_building_popup()
	
	# Draw popups
	if popup_queue.size() > 0:
		draw_popup_queue()

func draw_grid():
	# Track which buildings have been drawn to avoid duplicates
	var drawn_buildings = {}
	
	# First pass: Draw base tiles and merged buildings
	for r in range(Consts.GRID_SIZE):
		for c in range(Consts.GRID_SIZE):
			var world_pos = Vector2(c * Consts.TILE_SIZE, r * Consts.TILE_SIZE)
			var screen_pos = (world_pos - cam_offset) * zoom_level
			var tile_size = Consts.TILE_SIZE * zoom_level
			
			var b_id = grid[r][c]
			var key = Vector2i(r, c)
			
			# Skip if already drawn as part of a multi-tile building
			if drawn_buildings.has(key):
				continue
			
			var color = Consts.GRAY
			
			# Determine tile color
			if b_id == -1:
				color = Consts.RIVER_BLUE
				draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), color)
				draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), Color(0.3, 0.3, 0.3), false, max(1, int(zoom_level)))
			elif b_id > 0:
				# Building tile - draw merged
				var b_data = buildings[str(b_id)]
				var col_arr = b_data["color"]
				color = Color(col_arr[0]/255.0, col_arr[1]/255.0, col_arr[2]/255.0)
				
				var size = b_data["size"]
				var w = size[0]
				var h = size[1]
				
				# Check if this is the origin (top-left) of the building
				var is_origin = true
				if w > 1 or h > 1:
					if c > 0 and grid[r][c-1] == b_id:
						is_origin = false
					if r > 0 and grid[r-1][c] == b_id:
						is_origin = false
				
				if is_origin:
					# Draw merged building as a single rectangle
					var building_rect = Rect2(screen_pos, Vector2(w * tile_size, h * tile_size))
					
					# Add subtle gradient for depth (lighter at top, darker at bottom)
					var top_color = color.lightened(0.15)
					var bottom_color = color.darkened(0.1)
					
					# Draw main building body
					draw_rect(building_rect, color)
					
					# Add top highlight
					var highlight_rect = Rect2(screen_pos, Vector2(w * tile_size, h * tile_size * 0.3))
					draw_rect(highlight_rect, top_color.lerp(color, 0.7))
					
					# Add shadow at bottom
					var shadow_offset = Vector2(2, 2) * zoom_level
					var shadow_rect = Rect2(screen_pos + shadow_offset, Vector2(w * tile_size, h * tile_size))
					draw_rect(shadow_rect, Color(0, 0, 0, 0.2))
					draw_rect(building_rect, Color(0, 0, 0, 0.15))
					draw_rect(building_rect, color)
					
					# Draw border around the entire building (not each tile)
					var border_color = color.darkened(0.3)
					draw_rect(building_rect, border_color, false, max(2, int(zoom_level * 2)))
					
					# Draw inner grid lines for multi-tile buildings (subtle)
					if w > 1 or h > 1:
						var grid_color = color.darkened(0.15)
						for dr in range(h + 1):
							var line_start = screen_pos + Vector2(0, dr * tile_size)
							var line_end = screen_pos + Vector2(w * tile_size, dr * tile_size)
							draw_line(line_start, line_end, grid_color, max(1, int(zoom_level * 0.5)))
						for dc in range(w + 1):
							var line_start = screen_pos + Vector2(dc * tile_size, 0)
							var line_end = screen_pos + Vector2(dc * tile_size, h * tile_size)
							draw_line(line_start, line_end, grid_color, max(1, int(zoom_level * 0.5)))
					
					# Draw centered emoji/symbol
					var symbol = b_data.get("symbol", "")
					if symbol:
						var center_offset = Vector2(w * tile_size / 2, h * tile_size / 2)
						var symbol_size = int(32 * zoom_level * (1.0 if w > 1 else 0.8))
						# Shift emoji left by reducing X offset from 0.3 to 0.4
						var text_pos = screen_pos + center_offset - Vector2(symbol_size * 0.4, -symbol_size * 0.3)
						
						# Draw shadow for emoji
						draw_string(ThemeDB.fallback_font, text_pos + Vector2(2, 2), symbol, HORIZONTAL_ALIGNMENT_CENTER, -1, symbol_size, Color(0, 0, 0, 0.5))
						# Draw emoji
						draw_string(ThemeDB.fallback_font, text_pos, symbol, HORIZONTAL_ALIGNMENT_CENTER, -1, symbol_size, Consts.WHITE)
					
					# Mark all tiles of this building as drawn
					for dr in range(h):
						for dc in range(w):
							drawn_buildings[Vector2i(r + dr, c + dc)] = true
			else:
				# Empty land - black background
				color = Color(0.0, 0.0, 0.0)
				draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), color)
				draw_rect(Rect2(screen_pos, Vector2(tile_size, tile_size)), Color(0.3, 0.3, 0.3, 0.5), false, max(1, int(zoom_level * 0.5)))
	
	# Draw white frame for hovered tile
	if state == Consts.GameState.GAME:
		var mouse_pos = get_viewport().get_mouse_position()
		var viewport_size = get_viewport().get_visible_rect().size
		
		# Only highlight if mouse is over the grid (not sidebar)
		if mouse_pos.x < viewport_size.x - 280:
			var grid_pos = screen_to_world(mouse_pos)
			var r = grid_pos.x
			var c = grid_pos.y
			
			if r >= 0 and r < Consts.GRID_SIZE and c >= 0 and c < Consts.GRID_SIZE:
				# Get building size for proper frame size
				var b_data = buildings[str(selected_building)]
				var size = b_data["size"]
				var w = size[0]
				var h = size[1]
				
				var world_pos = Vector2(c * Consts.TILE_SIZE, r * Consts.TILE_SIZE)
				var screen_pos = (world_pos - cam_offset) * zoom_level
				var tile_size = Consts.TILE_SIZE * zoom_level
				
				# Draw white highlight frame matching building size
				draw_rect(Rect2(screen_pos, Vector2(w * tile_size, h * tile_size)), Consts.WHITE, false, max(2, int(zoom_level * 3)))

func draw_game_ui():
	var viewport_size = get_viewport().get_visible_rect().size
	var sidebar_x = viewport_size.x - 280
	
	# Draw sidebar background
	draw_rect(Rect2(Vector2(sidebar_x, 0), Vector2(280, viewport_size.y)), Color(0.1, 0.1, 0.12))
	
	# Draw stats
	var y = 20
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Round: %d/%d" % [round_num, Consts.MAX_ROUNDS], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.WHITE)
	y += 30
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Money: $%d" % money, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.GREEN)
	y += 30
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Actions: %d/%d" % [actions, max_actions], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.CYAN)
	y += 30
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Pop: %d/%d" % [population, jobs_total], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.WHITE)
	y += 30
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Happy: %d" % happiness, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.YELLOW)
	y += 30
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "Energy: %d" % energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.YELLOW)
	
	# Draw building buttons
	y += 50
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 20, y), "BUILDINGS:", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.WHITE)
	y += 30
	
	var building_keys = [1, 2, 3, 4, 6, 9, 10, 7, 8]
	for i in range(building_keys.size()):
		var b_id = building_keys[i]
		var btn_x = sidebar_x + 20 + (i % 4) * 60
		var btn_y = y + (i / 4) * 60
		var btn_size = 50
		
		var btn_rect = Rect2(btn_x, btn_y, btn_size, btn_size)
		var btn_color = Consts.DARK_GRAY
		if b_id == selected_building:
			btn_color = Consts.BLUE
		
		draw_rect(btn_rect, btn_color)
		draw_rect(btn_rect, Consts.WHITE, false, 2)
		
		var b_data = buildings[str(b_id)]
		var symbol = b_data.get("symbol", "")
		if symbol:
			draw_string(ThemeDB.fallback_font, Vector2(btn_x + 10, btn_y + 30), symbol, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	# Next turn button
	var btn_next = Rect2(sidebar_x + 20, viewport_size.y - 80, 240, 50)
	draw_rect(btn_next, Consts.GREEN)
	draw_string(ThemeDB.fallback_font, Vector2(sidebar_x + 80, viewport_size.y - 50), "NEXT TURN", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Consts.BLACK)
	
	# Version number in bottom-left corner
	draw_string(ThemeDB.fallback_font, Vector2(10, viewport_size.y - 10), "v3.13", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.5, 0.5, 0.5))

func draw_building_popup():
	"""Draw popup for building actions (upgrade/sell)"""
	var pr = popup_coords.x
	var pc = popup_coords.y
	
	if pr < 0 or pc < 0 or pr >= Consts.GRID_SIZE or pc >= Consts.GRID_SIZE:
		return
	
	var b_id = grid[pr][pc]
	if b_id <= 0:
		return
	
	var b = buildings[str(b_id)]
	var viewport_size = get_viewport().get_visible_rect().size
	
	# Position popup near the building but keep it on screen
	var world_pos = Vector2(pc * Consts.TILE_SIZE, pr * Consts.TILE_SIZE)
	var screen_pos = (world_pos - cam_offset) * zoom_level
	var px = clampf(screen_pos.x + 20, 10, viewport_size.x - 310)
	var py = clampf(screen_pos.y, 10, viewport_size.y - 150)
	
	# Draw popup background
	var popup_rect = Rect2(px + 20, py, 140, 100)
	draw_rect(popup_rect, Color(0.05, 0.05, 0.08))
	draw_rect(popup_rect, Consts.WHITE, false, 2)
	
	var y_offset = py + 10
	
	# Upgrade button (if upgradeable)
	if b.get("upgrade_to"):
		var upgrade_cost = b.get("upgrade_cost", 0)
		var can_afford = money >= upgrade_cost
		var upgrade_rect = Rect2(px + 30, y_offset, 120, 25)
		var upgrade_color = Consts.CYAN if can_afford else Consts.RED
		
		draw_rect(upgrade_rect, Consts.DARK_GRAY)
		draw_rect(upgrade_rect, upgrade_color, false, 1)
		draw_string(ThemeDB.fallback_font, Vector2(px + 35, y_offset + 17), "Upgrade %d" % upgrade_cost, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, upgrade_color)
		y_offset += 30
	
	# Sell button
	var refund = int(get_building_total_cost(b_id) * 0.5)
	var sell_rect = Rect2(px + 30, y_offset, 120, 25)
	draw_rect(sell_rect, Consts.DARK_GRAY)
	draw_rect(sell_rect, Consts.WHITE, false, 1)
	draw_string(ThemeDB.fallback_font, Vector2(px + 35, y_offset + 17), "Sell +%d" % refund, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Consts.WHITE)
	y_offset += 30
	
	# Close button (X)
	var close_rect = Rect2(px + 135, py - 10, 20, 20)
	draw_rect(close_rect, Consts.RED)
	draw_string(ThemeDB.fallback_font, Vector2(px + 139, py - 3), "X", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Consts.WHITE)

func draw_popup_queue():
	if popup_queue.size() > 0:
		var popup = popup_queue[0]
		var viewport_size = get_viewport().get_visible_rect().size
		var popup_rect = Rect2(viewport_size.x/2 - 250, viewport_size.y/2 - 100, 500, 200)
		
		draw_rect(popup_rect, Color(0.1, 0.1, 0.15, 0.95))
		draw_rect(popup_rect, popup[2], false, 3)
		
		draw_string(ThemeDB.fallback_font, popup_rect.position + Vector2(20, 40), popup[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, popup[2])
		draw_string(ThemeDB.fallback_font, popup_rect.position + Vector2(20, 80), popup[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Consts.WHITE)
		draw_string(ThemeDB.fallback_font, popup_rect.position + Vector2(20, 160), "Click to continue...", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Consts.GRAY)

func draw_gameover():
	draw_rect(Rect2(Vector2.ZERO, get_viewport().get_visible_rect().size), Consts.UI_BG)
	
	var viewport_size = get_viewport().get_visible_rect().size
	var title = "VICTORY!" if win else "GAME OVER"
	var color = Consts.GOLD if win else Consts.RED
	
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 100, 100), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 48, color)
	
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 100, 200), "Final Money: $%d" % money, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 100, 240), "Population: %d" % population, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 100, 280), "Happiness: %d" % happiness, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	# Draw buttons
	var btn_restart = Rect2(viewport_size.x/2 - 100, 350, 200, 50)
	draw_rect(btn_restart, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 60, 380), "RESTART", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
	
	var btn_menu = Rect2(viewport_size.x/2 - 100, 420, 200, 50)
	draw_rect(btn_menu, Consts.DARK_GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(viewport_size.x/2 - 40, 450), "MENU", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Consts.WHITE)
