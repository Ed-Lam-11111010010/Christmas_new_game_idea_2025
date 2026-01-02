import pygame
import sys
import random
import json
import os
from datetime import datetime
from consts import *
from renderer import GameRenderer

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.load_settings() # Load res first
        
        self.screen = pygame.display.set_mode(self.current_res)
        pygame.display.set_caption("City Rogue v3.11: Dynamic")
        self.clock = pygame.time.Clock()
        
        self.renderer = GameRenderer(self.screen)
        
        self.load_game_data()
        self.state = STATE_MENU
        self.difficulty = "Normal"
        self.relic = None
        self.high_scores = self.load_scores()
        
        self.cam_x = 0
        self.cam_y = 0
        self.zoom = 1.0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
        self.sounds = {}
        self.load_sound("build", "build.wav")
        self.load_sound("money", "money.wav")
        self.load_sound("select", "select.wav")
        self.load_sound("error", "error.wav")

        self.popup_queue = [] 
        self.reset_game_data()

    def load_game_data(self):
        self.buildings = {}
        self.relics = []
        self.events = []
        self.milestones_data = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.buildings = {int(k): v for k, v in data["buildings"].items()}
                    self.relics = data["relics"]
                    self.events = data["events"]
                    self.milestones_data = data.get("milestones", [])
            except Exception as e:
                print(f"Error loading data: {e}"); sys.exit()
        else:
            print(f"CRITICAL: {DATA_FILE} not found!"); sys.exit()

    def load_settings(self):
        self.resolutions = [(950, 650), (1280, 720), (1600, 900)]
        self.res_index = 0
        self.volume = 0.5
        self.current_res = self.resolutions[0]
        
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.volume = data.get("volume", 0.5)
                    self.res_index = data.get("res_index", 0)
                    if self.res_index < len(self.resolutions):
                        self.current_res = self.resolutions[self.res_index]
            except: pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f: 
                json.dump({"volume": self.volume, "res_index": self.res_index}, f)
        except: pass

    def update_resolution(self):
        self.res_index = (self.res_index + 1) % len(self.resolutions)
        self.current_res = self.resolutions[self.res_index]
        self.screen = pygame.display.set_mode(self.current_res)
        self.renderer = GameRenderer(self.screen) # Re-init fonts/surfaces
        self.save_settings()

    def load_sound(self, name, filename):
        path = os.path.join(SFX_DIR, filename)
        if os.path.exists(path):
            try: 
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(self.volume)
            except: pass

    def play_sound(self, name):
        if name in self.sounds: 
            self.sounds[name].set_volume(self.volume)
            self.sounds[name].play()

    def load_scores(self):
        if not os.path.exists(SCORE_FILE): return []
        try:
            with open(SCORE_FILE, "r") as f: return json.load(f)
        except: return []

    def save_high_score(self):
        score = int(max(0, self.money) + (self.population * 10) + (self.happiness * 5) + (self.round * 20))
        entry = {"score": score, "status": "Victory" if self.win else f"Round {self.round}", "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
        self.high_scores.append(entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:5]
        try:
            with open(SCORE_FILE, "w") as f: json.dump(self.high_scores, f)
        except: pass

    def save_game(self):
        serial_logs = [(t, list(c)) for t, c in self.logs]
        rid = self.relic["id"] if self.relic else None
        data = { "grid": self.grid, "money": self.money, "actions": self.actions, "max_actions": self.max_actions,
                 "energy": self.energy, "round": self.round, "difficulty": self.difficulty, 
                 "active_events": self.active_events, "mods": self.mods, "logs": serial_logs, 
                 "relic_id": rid, "unlocked_milestones": self.unlocked_milestones, "drawn_event_ids": self.drawn_event_ids }
        try:
            with open(SAVE_FILE, "w") as f: json.dump(data, f)
        except: pass

    def load_game(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE, "r") as f: data = json.load(f)
            self.grid = data["grid"]; self.money = data["money"]
            self.actions = data.get("actions", 3); self.max_actions = data.get("max_actions", 3)
            self.energy = data["energy"]; self.round = data["round"]; self.difficulty = data["difficulty"]
            self.active_events = data["active_events"]; self.mods = data["mods"]
            self.logs = [(t, tuple(c)) for t, c in data["logs"]]
            rid = data.get("relic_id")
            if rid:
                for r in self.relics: 
                    if r["id"] == rid: self.relic = r
            self.unlocked_milestones = data.get("unlocked_milestones", [])
            self.drawn_event_ids = data.get("drawn_event_ids", [])
            self.recalc_stats(); self.state = STATE_GAME; self.log("Game Loaded.", GREEN)
        except: self.reset_game_data()

    def delete_save(self):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)

    def reset_game_data(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.network_map = {}; self.island_stats = {}; self.active_road_tiles = set(); self.active_buildings = set()
        self.unlocked_milestones = []; self.drawn_event_ids = []
        self.generate_river()
        self.money = 500 if self.difficulty == "Normal" else 350
        self.actions = 3; self.max_actions = 3
        self.energy = 10; self.population = 0; self.jobs_total = 0; self.happiness = 60
        self.round = 1; self.game_over = False; self.win = False
        self.selected_building = 1; self.relic = None
        self.popup_queue = []; self.active_events = []
        self.mods = { "cost_mult": 1.0, "pop_flat": 0, "money_mult": 1.0, "energy_flat": 0, "happy_flat": 0, "action_mod": 0 }
        self.popup_active = False; self.popup_coords = (-1, -1); self.popup_rects = []
        self.logs = []; self.log_scroll_offset = 0; self.max_log_lines = 5
        self.prev_pop = 0; self.prev_happy = 60; self.prev_energy = 10
        self.log("Welcome Mayor!", WHITE)
        self.recalc_stats()

    # --- LOGIC HELPERS ---
    def generate_river(self):
        for _ in range(2):
            r, c = random.randint(0, GRID_SIZE-1), 0
            self.grid[r][c] = -1
            while c < GRID_SIZE - 1:
                move = random.choice([(0, 1), (0, 1), (-1, 0), (1, 0)]) 
                r += move[0]; c += move[1]
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE: self.grid[r][c] = -1
                else: break

    def log(self, text, color=WHITE):
        self.logs.append((text, color))
        if len(self.logs) > self.max_log_lines: self.log_scroll_offset = len(self.logs) - self.max_log_lines

    def handle_scroll(self, y_change):
        if len(self.logs) <= self.max_log_lines: return
        self.log_scroll_offset -= y_change
        max_offset = len(self.logs) - self.max_log_lines
        self.log_scroll_offset = max(0, min(self.log_scroll_offset, max_offset))

    def screen_to_world(self, sx, sy):
        return int(((sy / self.zoom) + self.cam_y) // TILE_SIZE), int(((sx / self.zoom) + self.cam_x) // TILE_SIZE)

    def get_cost(self, b_id):
        base = self.buildings[b_id]["cost"]
        if base == 0: return 0
        if self.relic:
            if self.relic["id"] == "industrialist" and b_id == 3: return 50
            if self.relic["id"] == "tycoon": base = int(base * 1.2)
        return int(base * self.mods["cost_mult"])

    def get_neighbors_coords(self, r, c):
        n = []
        if r > 0: n.append((r-1, c))
        if r < GRID_SIZE-1: n.append((r+1, c))
        if c > 0: n.append((r, c-1))
        if c < GRID_SIZE-1: n.append((r, c+1))
        return n

    def get_neighbors(self, r, c):
        return [self.grid[nr][nc] for nr, nc in self.get_neighbors_coords(r, c)]

    def update_road_networks(self):
        self.network_map = {} 
        self.island_stats = {}
        self.active_road_tiles = set()
        self.active_buildings = set()
        visited = set()
        nid = 1
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] > 0 and (r,c) not in visited:
                    q = [(r, c)]; visited.add((r, c)); self.network_map[(r, c)] = nid
                    while q:
                        curr_r, curr_c = q.pop(0)
                        for nr, nc in self.get_neighbors_coords(curr_r, curr_c):
                            if self.grid[nr][nc] > 0 and (nr, nc) not in visited:
                                visited.add((nr, nc)); self.network_map[(nr, nc)] = nid; q.append((nr, nc))
                    nid += 1
        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    iid = self.network_map.get((r,c))
                    if not iid: continue
                    if iid not in self.island_stats: self.island_stats[iid] = {"pop": 0, "jobs": 0, "active": False}
                    b = self.buildings[b_id]; w, h = b["size"]
                    for dr in range(h): 
                        for dc in range(w): processed.add((r+dr, c+dc))
                    pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                    self.island_stats[iid]["pop"] += pop_gain; self.island_stats[iid]["jobs"] += b["work"]
                    if pop_gain > 0 or b["work"] > 0: self.island_stats[iid]["active"] = True
        for coord, iid in self.network_map.items():
            if self.grid[coord[0]][coord[1]] in [7, 8]:
                if self.island_stats[iid]["active"]: self.active_road_tiles.add(coord)
            else: self.active_buildings.add(coord)

    def get_building_island_id(self, r, c):
        return self.network_map.get((r,c))

    def can_place_building(self, r, c, b_id):
        w, h = self.buildings[b_id]["size"]
        if r + h > GRID_SIZE or c + w > GRID_SIZE: return False
        for dr in range(h):
            for dc in range(w):
                tile = self.grid[r+dr][c+dc]
                if b_id == 8: 
                    if tile != -1: return False
                else:
                    if tile != 0: return False
        return True

    def build(self, r, c):
        b_id = self.selected_building
        cost = self.get_cost(b_id); ap_cost = self.buildings[b_id].get("ap_cost", 0)
        if self.money < cost: self.play_sound("error"); self.log(f"Need ${cost}!", RED); return
        if self.actions < ap_cost: self.play_sound("error"); self.log("Not enough Actions!", RED); return
        self.money -= cost; self.actions -= ap_cost
        self.force_build(r, c, b_id); self.play_sound("build"); self.log(f"Built {self.buildings[b_id]['name']}", GREEN)

    def force_build(self, r, c, b_id):
        w, h = self.buildings[b_id]["size"]
        for dr in range(h):
            for dc in range(w): self.grid[r+dr][c+dc] = b_id
        self.recalc_stats()

    def upgrade_building(self):
        r, c = self.popup_coords; b_id = self.grid[r][c]; b_data = self.buildings[b_id]
        if b_data["upgrade_to"]:
            up_id = b_data["upgrade_to"]; up_cost = b_data["upgrade_cost"]
            if self.money >= up_cost:
                self.money -= up_cost; self.force_build(r, c, up_id)
                self.play_sound("build"); self.log(f"Upgraded!", CYAN); self.popup_active = False

    def demolish_building(self):
        r, c = self.popup_coords; b_id = self.grid[r][c]
        refund = int(self.get_cost(b_id) * 0.5); w, h = self.buildings[b_id]["size"]
        for dr in range(h):
            for dc in range(w):
                if b_id == 8: self.grid[r+dr][c+dc] = -1
                else: self.grid[r+dr][c+dc] = 0
        self.money += refund; self.play_sound("money"); self.log(f"Sold (+${refund})", GRAY); self.popup_active = False; self.recalc_stats()

    def recalc_stats(self):
        self.update_road_networks()
        total_pop = 0; total_jobs = 0; raw_happy = 50 + self.mods["happy_flat"]
        if self.relic and self.relic["id"] == "ecotopia": raw_happy += 10
        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = self.buildings[b_id]; w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    iid = self.network_map.get((r,c))
                    is_valid = False
                    if iid and self.island_stats[iid]["pop"] > 0: is_valid = True
                    elif b["pop"] > 0: is_valid = True
                    if is_valid:
                        total_pop += max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                        total_jobs += b["work"]
                    raw_happy += b["happy"]
                    if b["needs_road"] and not is_valid: raw_happy -= 5
                    neighbors = []
                    for dr in range(h):
                        for dc in range(w): neighbors.extend(self.get_neighbors(r+dr, c+dc))
                    if b_id == 11 and (1 in neighbors or 5 in neighbors): raw_happy += 5
        self.population = total_pop; self.jobs_total = total_jobs; self.happiness = max(0, min(100, raw_happy))

    def calculate_turn_income(self):
        money_change = 0; energy_change = 0
        happy_mult = 1.0 if 30 < self.happiness < 80 else (1.2 if self.happiness >= 80 else 0.5)
        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = self.buildings[b_id]; w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    iid = self.network_map.get((r,c))
                    if not iid: continue
                    istats = self.island_stats[iid]
                    local_eff = 1.0
                    if b["work"] > 0:
                        local_eff = min(1.0, istats["pop"] / istats["jobs"]) if istats["pop"] > 0 else 0
                    gain = b["money"]
                    if gain > 0: gain = gain * local_eff * happy_mult
                    money_change += gain; energy_change += b["energy"] * local_eff
        return int(money_change), int(energy_change)

    def predict_building_effects(self, r, c, b_id):
        effects = []; b = self.buildings[b_id]; ap_cost = b.get("ap_cost", 0)
        if self.actions < ap_cost: effects.append(f"⚠ Need {ap_cost} AP!")
        has_neighbor = False; neighbors = []
        w, h = b["size"]
        for dr in range(h):
            for dc in range(w):
                for nr, nc in self.get_neighbors_coords(r+dr, c+dc):
                    if self.grid[nr][nc] > 0: has_neighbor = True
                    neighbors.append(self.grid[nr][nc])
        if b["needs_road"] and not has_neighbor: effects.append("⚠ Disconnected")
        if b_id == 6 and (1 in neighbors or 5 in neighbors): effects.append("Combo: +15💰")
        return effects

    def check_milestones(self, income):
        for m in self.milestones_data:
            mid = m["id"]
            if mid not in self.unlocked_milestones:
                fulfilled = False
                if m["cond"] == "income" and income >= m["val"]: fulfilled = True
                elif m["cond"] == "pop" and self.population >= m["val"]: fulfilled = True
                elif m["cond"] == "happy" and self.happiness >= m["val"]: fulfilled = True
                if fulfilled:
                    self.unlocked_milestones.append(mid)
                    self.popup_queue.append((f"🏆 {m['name']}!", f"Reward: {m['desc']}", GOLD))
                    self.play_sound("build")
                    if m["reward"] == "action_max": self.max_actions += m["amt"]; self.actions += m["amt"]

    def next_turn(self):
        if self.game_over: return
        self.popup_active = False; self.play_sound("money"); self.actions = self.max_actions
        if self.round % 5 == 0 and self.round < MAX_ROUNDS:
            pool = [e for e in self.events if e["id"] not in self.drawn_event_ids]
            if pool:
                event = random.choice(pool); self.drawn_event_ids.append(event["id"]); self.active_events.append(event)
                if event["type"] == "cost": self.mods["cost_mult"] *= event["val"]
                elif event["type"] == "pop_mod": self.mods["pop_flat"] += event["val"]
                elif event["type"] == "money_mult": self.mods["money_mult"] *= event["val"]
                elif event["type"] == "energy_flat": self.mods["energy_flat"] += event["val"]
                elif event["type"] == "happy_flat": self.mods["happy_flat"] += event["val"]
                elif event["type"] == "action_mod": self.mods["action_mod"] += event["val"]; self.max_actions += int(event["val"])
                self.popup_queue.append((f"⚠ {event['name']}", event['desc'], PURPLE))
                self.log(f"⚠ EVENT: {event['name']}", PURPLE)
        self.recalc_stats()
        money_change, energy_change = self.calculate_turn_income()
        self.money += money_change; self.energy = 10 + energy_change; self.round += 1
        d_pop = self.population - self.prev_pop; d_happy = self.happiness - self.prev_happy
        
        # FIXED: Always show deltas
        self.log(f"Round {self.round-1}: {money_change:+}💰 | En: {energy_change:+}⚡", CYAN)
        self.log(f"Pop: {d_pop:+}👥 | Happy: {d_happy:+}😊", WHITE)
        
        if self.happiness < 40: self.log("⚠ Citizens Unhappy!", RED)
        if self.energy < 0: self.log("⚠ Power Shortage!", RED)
        self.prev_pop = self.population; self.prev_happy = self.happiness
        self.check_milestones(money_change)
        if self.money < 0 or self.round > MAX_ROUNDS:
            self.game_over = True; self.win = (self.money >= 0)
            self.save_high_score(); self.delete_save(); self.state = STATE_GAMEOVER
        else: self.save_game()

    # --- MAIN LOOP ---
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == STATE_GAME and not self.game_over: self.save_game()
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN: self.handle_mouse_down()
                if event.type == pygame.MOUSEBUTTONUP: 
                    if event.button == 3: self.dragging = False
                if event.type == pygame.MOUSEMOTION: self.handle_mouse_move()
                if event.type == pygame.MOUSEWHEEL and self.state == STATE_GAME:
                    self.zoom = max(0.5, min(2.0, self.zoom + event.y * 0.1))
                if event.type == pygame.KEYDOWN: self.handle_keys(event)

            self.screen.fill(UI_BG)
            if self.state == STATE_MENU: self.renderer.draw_menu(self)
            elif self.state == STATE_RELIC: self.renderer.draw_relic_screen(self)
            elif self.state == STATE_SETTINGS: self.renderer.draw_settings(self)
            elif self.state == STATE_GAME: self.renderer.draw_game(self)
            elif self.state == STATE_GAMEOVER: self.renderer.draw_gameover(self)
            pygame.display.flip(); self.clock.tick(60)

    def handle_mouse_down(self):
        mx, my = pygame.mouse.get_pos()
        if self.state == STATE_MENU: self.handle_menu_click(mx, my)
        elif self.state == STATE_RELIC: self.handle_relic_click(mx, my)
        elif self.state == STATE_SETTINGS: self.handle_settings_click(mx, my)
        elif self.state == STATE_GAMEOVER: self.handle_gameover_click(mx, my)
        elif self.state == STATE_GAME: self.handle_game_click(mx, my)

    def handle_mouse_move(self):
        if self.state == STATE_GAME and self.dragging:
            mx, my = pygame.mouse.get_pos()
            dx = mx - self.last_mouse_pos[0]; dy = my - self.last_mouse_pos[1]
            self.cam_x -= dx / self.zoom; self.cam_y -= dy / self.zoom
            self.last_mouse_pos = (mx, my)

    def handle_keys(self, event):
        if self.state == STATE_GAME:
            if self.popup_queue: self.popup_queue.pop(0); return
            keys = {
                pygame.K_1:1, pygame.K_2:2, pygame.K_3:3, pygame.K_4:4, pygame.K_5:6, pygame.K_6:9, pygame.K_7:10, 
                pygame.K_8:7, pygame.K_9:8
            }
            if event.key in keys: self.selected_building = keys[event.key]; self.play_sound("select")
            if event.key == pygame.K_SPACE and not self.popup_active: self.next_turn()
            if event.key == pygame.K_ESCAPE: 
                if not self.game_over: self.save_game()
                self.state = STATE_MENU

    def handle_game_click(self, mx, my):
        if hasattr(self, 'btn_pass') and self.btn_pass.collidepoint(mx, my): self.next_turn(); return
        if self.popup_queue: self.popup_queue.pop(0); return
        # Pass click handling to renderer logic if needed, but logic is here:
        if hasattr(self, 'btn_log_up') and self.btn_log_up.collidepoint(mx, my): self.handle_scroll(1); return
        if hasattr(self, 'btn_log_down') and self.btn_log_down.collidepoint(mx, my): self.handle_scroll(-1); return
        
        if self.popup_active:
            for rect, action in self.popup_rects:
                if rect.collidepoint(mx, my):
                    if action == "UPGRADE": self.upgrade_building()
                    elif action == "SELL": self.demolish_building()
                    self.popup_active = False; return
            self.popup_active = False; return
        
        # Sidebar click check (simplified: if x > width - sidebar_w)
        w, h = self.screen.get_size()
        if mx > w - 280: self.handle_sidebar_click(mx, my); return
        if self.log_rect.collidepoint(mx, my): return
        
        # Map Click
        r, c = self.screen_to_world(mx, my)
        if pygame.mouse.get_pressed()[2]: self.dragging = True; self.last_mouse_pos = (mx, my); return
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            if pygame.mouse.get_pressed()[0]:
                if self.grid[r][c] in [0, -1]:
                    if self.can_place_building(r, c, self.selected_building): self.build(r, c)
                    else: self.play_sound("error"); self.log("Invalid placement!", RED)
                else:
                    self.popup_active = True; self.popup_coords = (r, c)
                    if self.buildings[self.grid[r][c]]["size"] == [2,2]:
                        if r > 0 and self.grid[r-1][c] == self.grid[r][c]: self.popup_coords = (r-1, c)
                        if c > 0 and self.grid[r][c-1] == self.grid[r][c]: self.popup_coords = (r, c-1)
                        if r > 0 and c > 0 and self.grid[r-1][c-1] == self.grid[r][c]: self.popup_coords = (r-1, c-1)
                    self.play_sound("select")

    def handle_sidebar_click(self, mx, my):
        # We need to recalculate where buttons are based on screen size
        w, h = self.screen.get_size()
        tb_x = w - 280 + 20
        y = 250
        keys = [1, 2, 3, 4, 6, 9, 10, 7, 8]
        for i, b_id in enumerate(keys):
            rect = pygame.Rect(tb_x + (i%4)*60, y + (i//4)*60, 50, 50)
            if rect.collidepoint(mx, my): self.selected_building = b_id; self.play_sound("select")

    def handle_menu_click(self, mx, my):
        if hasattr(self, 'menu_buttons') and self.menu_buttons:
            if self.menu_buttons[0].collidepoint(mx, my): self.reset_game_data(); self.state = STATE_RELIC
            elif self.menu_buttons[1].collidepoint(mx, my): self.load_game()
            elif self.menu_buttons[2].collidepoint(mx, my): self.state = STATE_SETTINGS
            elif self.menu_buttons[3].collidepoint(mx, my): pygame.quit(); sys.exit()

    def handle_relic_click(self, mx, my):
        for rect, relic in self.relic_rects:
            if rect.collidepoint(mx, my):
                self.relic = relic; self.money = 500
                if relic["id"] == "tycoon": self.money = 1000
                if relic["id"] == "planner": 
                    self.money = 600
                    self.force_build(17, 14, 7); self.force_build(17, 15, 7)
                    self.force_build(17, 16, 7); self.force_build(17, 17, 7)
                    self.force_build(16, 12, 1); self.force_build(16, 18, 1)
                self.log(f"Relic: {relic['name']}", tuple(relic["color"])); self.recalc_stats(); self.state = STATE_GAME

    def handle_settings_click(self, mx, my):
        if hasattr(self, 'btn_diff') and self.btn_diff.collidepoint(mx, my): self.difficulty = "Hard" if self.difficulty == "Normal" else "Normal"
        elif hasattr(self, 'btn_res') and self.btn_res.collidepoint(mx, my): self.update_resolution()
        elif hasattr(self, 'vol_up') and self.vol_up.collidepoint(mx, my): self.volume = min(1.0, self.volume + 0.1); self.save_settings()
        elif hasattr(self, 'vol_dn') and self.vol_dn.collidepoint(mx, my): self.volume = max(0.0, self.volume - 0.1); self.save_settings()
        elif hasattr(self, 's_back') and self.s_back.collidepoint(mx, my): self.state = STATE_MENU

    def handle_gameover_click(self, mx, my):
        if hasattr(self, 'btn_restart') and self.btn_restart.collidepoint(mx, my): self.reset_game_data(); self.state = STATE_RELIC
        elif hasattr(self, 'btn_menu') and self.btn_menu.collidepoint(mx, my): self.state = STATE_MENU

if __name__ == "__main__":
    Game().run()