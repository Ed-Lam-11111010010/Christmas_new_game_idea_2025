import pygame
import sys
import random
import json
import os
from datetime import datetime

# --- Configuration & Constants ---
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 650
GRID_SIZE = 30
TILE_SIZE = 40
MAX_ROUNDS = 20
SAVE_FILE = "city_rogue_save.json"
SCORE_FILE = "city_rogue_scores.json"
DATA_FILE = "game_data.json"
SFX_DIR = "sfx"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
UI_BG = (30, 30, 35)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (220, 220, 50)
PINK = (220, 100, 180)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 200)
ORANGE = (220, 140, 30)
GOLD = (255, 215, 0)
RIVER_BLUE = (60, 100, 200)
ROAD_ACTIVE = (220, 220, 220)
ROAD_INACTIVE = (80, 80, 80)
BRIDGE_COL = (139, 69, 19)

STATE_MENU = 0
STATE_RELIC = 1
STATE_GAME = 2
STATE_SETTINGS = 3
STATE_GAMEOVER = 4

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Rogue v3.3: Island Economy")
        self.clock = pygame.time.Clock()
        
        self.load_game_data()
        
        try:
            self.font = pygame.font.SysFont("Segoe UI Emoji", 16)
            self.font_bold = pygame.font.SysFont("Segoe UI Emoji", 16, bold=True)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 24)
            self.font_ui = pygame.font.SysFont("Segoe UI Emoji", 18)
        except:
            self.font = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_icon = pygame.font.SysFont("Arial", 24)
            self.font_ui = pygame.font.SysFont("Arial", 18)

        self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 24)

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

        self.btn_pass = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70, 150, 50)
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
                print(f"Error loading data: {e}")
                sys.exit()
        else:
            print(f"CRITICAL: {DATA_FILE} not found!")
            sys.exit()

    def load_sound(self, name, filename):
        path = os.path.join(SFX_DIR, filename)
        if os.path.exists(path):
            try: self.sounds[name] = pygame.mixer.Sound(path)
            except: pass

    def play_sound(self, name):
        if name in self.sounds: self.sounds[name].play()

    def reset_game_data(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.island_map = {} # Maps (r,c) -> Island ID
        self.island_stats = {} # Maps ID -> {pop, jobs, buildings}
        self.active_road_tiles = set()
        self.unlocked_milestones = []
        self.generate_river()

        self.money = 500 if self.difficulty == "Normal" else 350
        self.actions = 3
        self.max_actions = 3
        self.energy = 10
        self.population = 0
        self.happiness = 60
        self.round = 1
        self.game_over = False
        self.win = False
        self.selected_building = 1
        self.relic = None
        
        self.active_events = []
        self.mods = { "cost_mult": 1.0, "pop_flat": 0, "money_mult": 1.0, "energy_flat": 0, "happy_flat": 0, "action_mod": 0 }
        
        self.popup_active = False
        self.popup_coords = (-1, -1)
        self.popup_rects = []
        
        self.logs = []
        self.log_scroll_offset = 0 
        self.max_log_lines = 5 
        self.log_rect = pygame.Rect(20, SCREEN_HEIGHT - 130, 450, 110)
        
        self.log("Welcome Mayor!", WHITE)
        self.recalc_stats()

    def generate_river(self):
        for _ in range(2):
            r, c = random.randint(0, GRID_SIZE-1), 0
            self.grid[r][c] = -1
            while c < GRID_SIZE - 1:
                move = random.choice([(0, 1), (0, 1), (-1, 0), (1, 0)]) 
                r += move[0]
                c += move[1]
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    self.grid[r][c] = -1
                else: break

    def load_scores(self):
        if not os.path.exists(SCORE_FILE): return []
        try:
            with open(SCORE_FILE, "r") as f: return json.load(f)
        except: return []

    def save_high_score(self):
        final_money = max(0, self.money)
        score = int(final_money + (self.population * 10) + (self.happiness * 5) + (self.round * 20))
        status = "Victory" if self.win else f"Round {self.round}"
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {"score": score, "status": status, "date": date_str}
        self.high_scores.append(entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:5]
        try:
            with open(SCORE_FILE, "w") as f: json.dump(self.high_scores, f)
        except Exception as e: print(e)

    def save_game(self):
        serializable_logs = []
        for text, col in self.logs: serializable_logs.append((text, list(col)))
        rid = self.relic["id"] if self.relic else None
        data = { "grid": self.grid, "money": self.money, "actions": self.actions, "max_actions": self.max_actions,
                 "energy": self.energy, "round": self.round, 
                 "difficulty": self.difficulty, "active_events": self.active_events, "mods": self.mods, 
                 "logs": serializable_logs, "relic_id": rid, "unlocked_milestones": self.unlocked_milestones }
        try:
            with open(SAVE_FILE, "w") as f: json.dump(data, f)
        except Exception as e: print(e)

    def load_game(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE, "r") as f: data = json.load(f)
            self.grid = data["grid"]
            self.money = data["money"]
            self.actions = data.get("actions", 3)
            self.max_actions = data.get("max_actions", 3)
            self.energy = data["energy"]
            self.round = data["round"]
            self.difficulty = data["difficulty"]
            self.active_events = data["active_events"]
            self.mods = data["mods"]
            self.logs = []
            for text, col in data["logs"]: self.logs.append((text, tuple(col)))
            rid = data.get("relic_id")
            if rid:
                for r in self.relics: 
                    if r["id"] == rid: self.relic = r
            self.unlocked_milestones = data.get("unlocked_milestones", [])
            self.recalc_stats()
            self.state = STATE_GAME
            self.log("Game Loaded.", GREEN)
        except Exception: self.reset_game_data()

    def delete_save(self):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)

    def log(self, text, color=WHITE):
        self.logs.append((text, color))
        if len(self.logs) > self.max_log_lines:
            self.log_scroll_offset = len(self.logs) - self.max_log_lines

    def handle_scroll(self, y_change):
        if len(self.logs) <= self.max_log_lines: return
        self.log_scroll_offset -= y_change
        max_offset = len(self.logs) - self.max_log_lines
        self.log_scroll_offset = max(0, min(self.log_scroll_offset, max_offset))

    # --- CAMERA HELPERS ---
    def screen_to_world(self, sx, sy):
        wx = (sx / self.zoom) + self.cam_x
        wy = (sy / self.zoom) + self.cam_y
        r = int(wy // TILE_SIZE)
        c = int(wx // TILE_SIZE)
        return r, c

    def world_to_screen(self, r, c):
        wx = c * TILE_SIZE
        wy = r * TILE_SIZE
        sx = (wx - self.cam_x) * self.zoom
        sy = (wy - self.cam_y) * self.zoom
        return sx, sy

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
        n = []
        for nr, nc in self.get_neighbors_coords(r, c):
            n.append(self.grid[nr][nc])
        return n

    # --- ISLAND CONNECTIVITY SYSTEM (v3.3) ---
    def update_islands(self):
        """
        Groups all connected non-empty tiles (Roads OR Buildings) into Islands.
        Each Island tracks its total Population and Jobs.
        """
        self.island_map = {} 
        self.island_stats = {} 
        self.active_road_tiles = set()
        
        visited = set()
        island_id = 1
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                # Anything not empty (0) and not river (-1) is part of the connectivity graph
                if b_id > 0 and (r,c) not in visited:
                    queue = [(r, c)]
                    visited.add((r, c))
                    self.island_map[(r, c)] = island_id
                    
                    while queue:
                        curr_r, curr_c = queue.pop(0)
                        
                        # Add stats for this tile immediately
                        tid = self.grid[curr_r][curr_c]
                        if island_id not in self.island_stats: 
                            self.island_stats[island_id] = {"pop": 0, "jobs": 0, "active": False}
                        
                        # Only add building stats ONCE per building (use root logic?)
                        # Simplified: We iterate all tiles, but we need to avoid double counting 2x2.
                        # Wait, we can't easily dedup 2x2 here without tracking "processed buildings".
                        # Better strategy: Just map IDs here. Stats calculated in Step 2.
                        
                        # Check neighbors
                        for nr, nc in self.get_neighbors_coords(curr_r, curr_c):
                            nid_val = self.grid[nr][nc]
                            if nid_val > 0 and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                self.island_map[(nr, nc)] = island_id
                                queue.append((nr, nc))
                    island_id += 1

        # 2. Calculate Island Stats (Pop/Jobs)
        processed_buildings = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed_buildings: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    # Get Island ID
                    iid = self.island_map.get((r,c))
                    if not iid: continue # Should not happen
                    
                    b = self.buildings[b_id]
                    w, h = b["size"]
                    for dr in range(h): 
                        for dc in range(w): processed_buildings.add((r+dr, c+dc))
                    
                    # Accumulate Stats
                    pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                    self.island_stats[iid]["pop"] += pop_gain
                    self.island_stats[iid]["jobs"] += b["work"]
                    
                    if pop_gain > 0 or b["work"] > 0:
                        self.island_stats[iid]["active"] = True

        # 3. Mark Valid Roads (White)
        for coord, iid in self.island_map.items():
            if self.grid[coord[0]][coord[1]] in [7, 8]: # Road/Bridge
                if self.island_stats[iid]["active"]:
                    self.active_road_tiles.add(coord)

    def get_building_island_id(self, r, c):
        return self.island_map.get((r,c))

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
        cost = self.get_cost(b_id)
        ap_cost = self.buildings[b_id].get("ap_cost", 0)
        
        if self.money < cost:
            self.play_sound("error"); self.log(f"Need ${cost}!", RED); return
        if self.actions < ap_cost:
            self.play_sound("error"); self.log("Not enough Actions!", RED); return

        self.money -= cost
        self.actions -= ap_cost
        
        w, h = self.buildings[b_id]["size"]
        for dr in range(h):
            for dc in range(w):
                self.grid[r+dr][c+dc] = b_id
        
        self.play_sound("build")
        self.log(f"Built {self.buildings[b_id]['name']}", GREEN)
        self.recalc_stats()

    def upgrade_building(self):
        r, c = self.popup_coords
        b_id = self.grid[r][c]
        b_data = self.buildings[b_id]
        if b_data["upgrade_to"]:
            up_id = b_data["upgrade_to"]
            up_cost = b_data["upgrade_cost"]
            if self.money >= up_cost:
                self.money -= up_cost
                w, h = b_data["size"]
                for dr in range(h):
                    for dc in range(w):
                        self.grid[r+dr][c+dc] = up_id
                self.play_sound("build")
                self.log(f"Upgraded!", CYAN)
                self.popup_active = False
                self.recalc_stats()

    def demolish_building(self):
        r, c = self.popup_coords
        b_id = self.grid[r][c]
        refund = int(self.get_cost(b_id) * 0.5)
        w, h = self.buildings[b_id]["size"]
        for dr in range(h):
            for dc in range(w):
                if b_id == 8: self.grid[r+dr][c+dc] = -1
                else: self.grid[r+dr][c+dc] = 0
        self.money += refund
        self.play_sound("money")
        self.log(f"Sold (+${refund})", GRAY)
        self.popup_active = False
        self.recalc_stats()

    def recalc_stats(self):
        self.update_islands()
        total_pop = 0
        raw_happy = 50 + self.mods["happy_flat"]
        if self.relic and self.relic["id"] == "ecotopia": raw_happy += 10
        
        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = self.buildings[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    # Logic: Is it in a valid island?
                    # A building is valid if it is in an island with Pop > 0 OR it provides Pop itself.
                    iid = self.get_building_island_id(r, c)
                    is_valid = False
                    
                    if iid:
                        istats = self.island_stats[iid]
                        if istats["pop"] > 0: is_valid = True
                        elif b["pop"] > 0: is_valid = True # I am the first house!
                    
                    if is_valid:
                        pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                        total_pop += pop_gain
                        
                    raw_happy += b["happy"]
                    if b["needs_road"] and not is_valid:
                        raw_happy -= 5

        self.population = total_pop
        self.happiness = max(0, min(100, raw_happy))

    def calculate_turn_income(self):
        money_change = 0
        energy_change = 0
        happy_mult = 1.0
        if self.happiness >= 80: happy_mult = 1.2
        elif self.happiness <= 30: happy_mult = 0.5

        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = self.buildings[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    iid = self.get_building_island_id(r, c)
                    if not iid: continue # Floating in void?

                    istats = self.island_stats[iid]
                    
                    # Labor Check: Needs workers in the same island
                    # If island has 0 pop, efficiency = 0 (unless the building provides pop, but houses don't work, they just exist)
                    
                    local_eff = 1.0
                    if b["work"] > 0:
                        if istats["pop"] > 0:
                            local_eff = min(1.0, istats["pop"] / istats["jobs"])
                        else:
                            local_eff = 0 # No workers in this island!

                    gain = b["money"]
                    if gain > 0: gain = gain * local_eff * happy_mult
                    money_change += gain
                    energy_change += b["energy"] * local_eff

        return int(money_change), int(energy_change)

    def predict_building_effects(self, r, c, b_id):
        effects = []
        b = self.buildings[b_id]
        
        ap_cost = b.get("ap_cost", 0)
        if self.actions < ap_cost: effects.append(f"⚠ Need {ap_cost} AP!")

        # Simplified Island Preview
        has_neighbor = False
        neighbors = []
        w, h = b["size"]
        for dr in range(h):
            for dc in range(w):
                for nr, nc in self.get_neighbors_coords(r+dr, c+dc):
                    if self.grid[nr][nc] > 0: has_neighbor = True
                    neighbors.append(self.grid[nr][nc])
        
        if b["needs_road"] and not has_neighbor: effects.append("⚠ Disconnected")

        if b_id == 6 and (1 in neighbors or 5 in neighbors): effects.append("Combo: +15💰 per Resident")
        if b_id == 2 and 4 in neighbors: effects.append("Scenic: +20%💰")
        if b_id in [1, 5] and 3 in neighbors: effects.append("⚠ NIMBY: -5😊")
        return effects

    def check_milestones(self, income):
        for m in self.milestones_data:
            mid = m["id"]
            # Strict one-time check
            if mid not in self.unlocked_milestones:
                fulfilled = False
                if m["cond"] == "income" and income >= m["val"]: fulfilled = True
                elif m["cond"] == "pop" and self.population >= m["val"]: fulfilled = True
                
                if fulfilled:
                    self.unlocked_milestones.append(mid)
                    self.log(f"🏆 MILESTONE: {m['name']}!", GOLD)
                    self.log(f"   Reward: {m['desc']}", GOLD)
                    self.play_sound("build")
                    if m["reward"] == "action_max":
                        self.max_actions += m["amt"]
                        self.actions += m["amt"]

    def next_turn(self):
        if self.game_over: return
        self.popup_active = False 
        self.play_sound("money")
        
        # Reset Actions (Max can be increased by milestones)
        self.actions = self.max_actions
        
        if self.round % 5 == 0 and self.round < MAX_ROUNDS:
            event = random.choice(self.events)
            self.active_events.append(event)
            if event["type"] == "cost": self.mods["cost_mult"] *= event["val"]
            elif event["type"] == "pop_mod": self.mods["pop_flat"] += event["val"]
            elif event["type"] == "money_mult": self.mods["money_mult"] *= event["val"]
            elif event["type"] == "energy_flat": self.mods["energy_flat"] += event["val"]
            elif event["type"] == "happy_flat": self.mods["happy_flat"] += event["val"]
            elif event["type"] == "action_mod":
                self.mods["action_mod"] += event["val"]
                # Note: Temporary event logic vs Permanent is tricky.
                # For now, we apply it to max_actions?
                # Actually, better to just apply to current actions or mods.
                # Let's keep it simple: Permanent change for this run.
                self.max_actions += int(event["val"])
            elif event["type"] == "mixed":
                if "happy" in event: self.mods["happy_flat"] += event["happy"]
                if "action" in event: 
                    self.max_actions += event["action"]
                    self.actions += event["action"]
                
            self.log(f"⚠ EVENT: {event['name']}", PURPLE)
            self.log(f"   {event['desc']}", PURPLE)

        self.recalc_stats()
        
        money_change, energy_change = self.calculate_turn_income()
        self.money += money_change
        self.energy = 10 + energy_change
        self.round += 1
        
        self.log(f"Round {self.round-1}: Income {money_change:+}💰 | En {energy_change:+}⚡", CYAN)
        
        self.check_milestones(money_change)

        if self.money < 0 or self.round > MAX_ROUNDS:
            self.game_over = True
            self.win = (self.money >= 0)
            self.save_high_score()
            self.delete_save()
            self.state = STATE_GAMEOVER
        else:
            self.save_game()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == STATE_GAME and not self.game_over: self.save_game()
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.state == STATE_MENU: self.handle_menu_click(mx, my)
                    elif self.state == STATE_RELIC: self.handle_relic_click(mx, my)
                    elif self.state == STATE_SETTINGS: self.handle_settings_click(mx, my)
                    elif self.state == STATE_GAMEOVER: self.handle_gameover_click(mx, my)
                    elif self.state == STATE_GAME: 
                        handled = False
                        if self.btn_pass.collidepoint(mx, my):
                            self.next_turn(); handled = True
                        if not handled and self.popup_active:
                            for rect, action in self.popup_rects:
                                if rect.collidepoint(mx, my):
                                    if action == "UPGRADE": self.upgrade_building()
                                    elif action == "SELL": self.demolish_building()
                                    elif action == "CLOSE": self.popup_active = False
                                    handled = True; break
                            if not handled: self.popup_active = False; handled = True
                        if not handled and mx > SCREEN_WIDTH - 280:
                            self.handle_sidebar_click(mx, my); handled = True
                        if not handled:
                            if event.button == 1:
                                r, c = self.screen_to_world(mx, my)
                                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                                    if self.grid[r][c] in [0, -1]:
                                        if self.can_place_building(r, c, self.selected_building): self.build(r, c)
                                        else: self.play_sound("error"); self.log("Invalid placement!", RED)
                                    else:
                                        b_id = self.grid[r][c]
                                        origin_r, origin_c = r, c
                                        if self.buildings[b_id]["size"] == [2,2]:
                                            if r > 0 and self.grid[r-1][c] == b_id: origin_r = r - 1
                                            if c > 0 and self.grid[r][c-1] == b_id: origin_c = c - 1
                                        self.popup_active = True
                                        self.popup_coords = (origin_r, origin_c)
                                        self.play_sound("select")
                            elif event.button == 3: self.dragging = True; self.last_mouse_pos = (mx, my)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3: self.dragging = False

                if event.type == pygame.MOUSEMOTION and self.state == STATE_GAME and self.dragging:
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - self.last_mouse_pos[0]
                    dy = my - self.last_mouse_pos[1]
                    self.cam_x -= dx / self.zoom
                    self.cam_y -= dy / self.zoom
                    self.last_mouse_pos = (mx, my)

                if event.type == pygame.MOUSEWHEEL and self.state == STATE_GAME:
                    self.zoom = max(0.5, min(2.0, self.zoom + event.y * 0.1))

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_GAME:
                        keys = {pygame.K_1:1, pygame.K_2:2, pygame.K_3:3, pygame.K_4:4, pygame.K_5:6, pygame.K_6:7, pygame.K_7:8}
                        if event.key in keys: self.selected_building = keys[event.key]
                        if event.key == pygame.K_SPACE:
                            if not self.popup_active: self.next_turn()
                        if event.key == pygame.K_ESCAPE: 
                            if not self.game_over: self.save_game()
                            self.state = STATE_MENU

            self.screen.fill(UI_BG)
            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_RELIC: self.draw_relic_screen()
            elif self.state == STATE_SETTINGS: self.draw_settings()
            elif self.state == STATE_GAME: self.draw_game()
            elif self.state == STATE_GAMEOVER: self.draw_gameover()

            pygame.display.flip()
            self.clock.tick(60)

    # --- DRAWING ---
    def handle_sidebar_click(self, mx, my):
        y = 300; tb_x = SCREEN_WIDTH - 250
        keys = [1, 2, 3, 4, 6, 7, 8]
        for i, b_id in enumerate(keys):
            rect = pygame.Rect(tb_x + (i%3)*60, y + (i//3)*60, 50, 50)
            if rect.collidepoint(mx, my): self.selected_building = b_id; self.play_sound("select")

    def draw_game(self):
        # 1. Map Pass
        map_rect = pygame.Rect(0, 0, SCREEN_WIDTH - 280, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (20,20,30), map_rect)
        self.screen.set_clip(map_rect)
        
        start_c = int(self.cam_x // TILE_SIZE); start_r = int(self.cam_y // TILE_SIZE)
        end_c = start_c + int((SCREEN_WIDTH-280)/(TILE_SIZE*self.zoom)) + 2
        end_r = start_r + int(SCREEN_HEIGHT/(TILE_SIZE*self.zoom)) + 2
        start_c = max(0, start_c-2); start_r = max(0, start_r-2)
        end_c = min(GRID_SIZE, end_c); end_r = min(GRID_SIZE, end_r)

        # Pass 1: Terrain
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                sx, sy = self.world_to_screen(r, c)
                size = TILE_SIZE * self.zoom
                rect = pygame.Rect(sx, sy, size, size)
                if self.grid[r][c] == -1: pygame.draw.rect(self.screen, RIVER_BLUE, rect)
                else: pygame.draw.rect(self.screen, (30,30,30), rect)
                pygame.draw.rect(self.screen, (50,50,50), rect, 1)

        # Pass 2: Buildings
        processed = set()
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = self.buildings[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    sx, sy = self.world_to_screen(r, c)
                    size = TILE_SIZE * self.zoom
                    b_rect = pygame.Rect(sx, sy, size*w, size*h)
                    
                    col = tuple(b["color"])
                    if b_id in [7, 8]:
                        if (r, c) in self.active_road_tiles:
                            col = ROAD_ACTIVE
                            if b_id == 8: col = BRIDGE_COL
                        else:
                            col = ROAD_INACTIVE
                    
                    pygame.draw.rect(self.screen, col, b_rect.inflate(-2,-2))
                    if self.zoom > 0.6:
                        txt = self.font_icon.render(b["symbol"], True, BLACK)
                        self.screen.blit(txt, txt.get_rect(center=b_rect.center))
                    
                    # Check validity for warning
                    # If building is NOT part of a valid island (and needs road), warn
                    iid = self.get_building_island_id(r,c)
                    is_valid = False
                    if iid and self.island_stats[iid]["active"]: is_valid = True
                    if not b["needs_road"]: is_valid = True
                    
                    if b["needs_road"] and not is_valid:
                        self.screen.blit(self.font.render("!", True, RED), b_rect.topleft)

        # Hover
        mx, my = pygame.mouse.get_pos()
        if map_rect.collidepoint(mx, my) and not self.popup_active:
            r, c = self.screen_to_world(mx, my)
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                sel = self.selected_building
                if self.can_place_building(r, c, sel):
                    w, h = self.buildings[sel]["size"]
                    sx, sy = self.world_to_screen(r, c)
                    ghost = pygame.Rect(sx, sy, TILE_SIZE*self.zoom*w, TILE_SIZE*self.zoom*h)
                    pygame.draw.rect(self.screen, WHITE, ghost, 2)

        self.screen.set_clip(None)
        self.draw_sidebar()
        
        if self.popup_active:
            pr, pc = self.popup_coords
            px, py = self.world_to_screen(pr, pc)
            px = min(max(px, 10), SCREEN_WIDTH - 200)
            py = min(max(py, 10), SCREEN_HEIGHT - 120)
            
            self.popup_rects = []
            bg = pygame.Rect(px+20, py, 140, 100)
            pygame.draw.rect(self.screen, BLACK, bg); pygame.draw.rect(self.screen, WHITE, bg, 2)
            
            b_data = self.buildings[self.grid[pr][pc]]
            urect = pygame.Rect(px+30, py+10, 120, 25)
            if b_data["upgrade_to"]:
                ucost = b_data["upgrade_cost"]
                col = CYAN if self.money >= ucost else RED
                pygame.draw.rect(self.screen, DARK_GRAY, urect)
                pygame.draw.rect(self.screen, col, urect, 1)
                self.screen.blit(self.font.render(f"Upgrade {ucost}", True, col), (px+35, py+12))
                self.popup_rects.append((urect, "UPGRADE"))
            
            srect = pygame.Rect(px+30, py+40, 120, 25)
            refund = int(self.get_cost(self.grid[pr][pc]) * 0.5)
            pygame.draw.rect(self.screen, DARK_GRAY, srect); pygame.draw.rect(self.screen, WHITE, srect, 1)
            self.screen.blit(self.font.render(f"Sell +{refund}", True, WHITE), (px+35, py+42))
            self.popup_rects.append((srect, "SELL"))
            
            crect = pygame.Rect(px+135, py-10, 20, 20)
            pygame.draw.rect(self.screen, RED, crect)
            self.screen.blit(self.font_bold.render("X", True, WHITE), (px+139, py-9))
            self.popup_rects.append((crect, "CLOSE"))

    def draw_gameover(self):
        over = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        over.fill((0, 0, 0, 200))
        self.screen.blit(over, (0,0))
        msg = "VICTORY!" if self.win else "BANKRUPT!"
        col = GREEN if self.win else RED
        cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
        self.screen.blit(self.font_title.render(msg, True, col), (cx-80, cy-80))
        info = f"Score: {self.money + self.population*10}"
        self.screen.blit(self.font_ui.render(info, True, WHITE), (cx-50, cy-20))
        self.btn_restart = pygame.Rect(cx-100, cy+40, 200, 50)
        self.btn_menu = pygame.Rect(cx-100, cy+110, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_restart); pygame.draw.rect(self.screen, WHITE, self.btn_restart, 2)
        self.screen.blit(self.font_menu.render("PLAY AGAIN", True, WHITE), (cx-60, cy+50))
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_menu); pygame.draw.rect(self.screen, WHITE, self.btn_menu, 2)
        self.screen.blit(self.font_menu.render("MAIN MENU", True, WHITE), (cx-60, cy+120))

    def handle_gameover_click(self, mx, my):
        if self.btn_restart.collidepoint(mx, my): self.reset_game_data(); self.state = STATE_RELIC
        elif self.btn_menu.collidepoint(mx, my): self.state = STATE_MENU

    def draw_sidebar(self):
        ui_bg = pygame.Rect(SCREEN_WIDTH - 280, 0, 280, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, UI_BG, ui_bg); pygame.draw.rect(self.screen, GRAY, (ui_bg.x, 0, 2, SCREEN_HEIGHT))
        
        ui_x = SCREEN_WIDTH - 260
        y = 30
        self.screen.blit(self.font_title.render(f"Round {min(self.round, MAX_ROUNDS)}", True, WHITE), (ui_x, y)); y+=50
        
        stats = [
            (f"💰 ${self.money}", GREEN),
            (f"⚡ {self.energy}", YELLOW),
            (f"👥 {self.population}", WHITE),
            (f"😊 {int(self.happiness)}%", PINK),
            (f"⭐ {self.actions}/{self.max_actions}", ORANGE)
        ]
        for s, c in stats: self.screen.blit(self.font_ui.render(s, True, c), (ui_x, y)); y+=30

        y = 300
        tb_x = SCREEN_WIDTH - 250
        self.screen.blit(self.font_bold.render("Construction:", True, WHITE), (ui_x, y-25))
        keys = [1, 2, 3, 4, 6, 7, 8]
        for i, b_id in enumerate(keys):
            rect = pygame.Rect(tb_x + (i%3)*60, y + (i//3)*60, 50, 50)
            is_sel = (self.selected_building == b_id)
            pygame.draw.rect(self.screen, tuple(self.buildings[b_id]["color"]) if is_sel else DARK_GRAY, rect)
            pygame.draw.rect(self.screen, WHITE if is_sel else GRAY, rect, 2)
            self.screen.blit(self.font_icon.render(self.buildings[b_id]["symbol"], True, BLACK), rect.inflate(-10,-10))

        # --- INFO BOX ---
        info_rect = pygame.Rect(ui_x, 480, 240, 80)
        pygame.draw.rect(self.screen, (40, 40, 50), info_rect)
        pygame.draw.rect(self.screen, GRAY, info_rect, 1)
        
        mx, my = pygame.mouse.get_pos()
        r, c = self.screen_to_world(mx, my)
        preview_txt = []
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.screen.get_clip() and self.screen.get_clip().collidepoint(mx, my):
             if self.can_place_building(r, c, self.selected_building):
                 cost = self.get_cost(self.selected_building)
                 ap_cost = self.buildings[self.selected_building].get("ap_cost", 0)
                 preview_txt.append((f"Cost: -${cost} | -{ap_cost}⭐", RED if self.mods['cost_mult']>1 else WHITE))
                 effects = self.predict_building_effects(r, c, self.selected_building)
                 for e in effects: preview_txt.append((e, GREEN if "Combo" in e or "Scenic" in e else RED))
        
        if not preview_txt:
            sel_b = self.buildings[self.selected_building]
            cost = self.get_cost(self.selected_building)
            ap_cost = sel_b.get("ap_cost", 0)
            preview_txt.append((f"{sel_b['name']} (${cost}) {ap_cost}⭐", tuple(sel_b["color"])))
            preview_txt.append((f"Pop: {sel_b['pop']} | Work: {sel_b['work']}", WHITE))
            if sel_b["needs_road"]: preview_txt.append(("⚠ Needs Road or Cluster", ORANGE))
            
        iy = info_rect.y + 5
        for txt, col in preview_txt:
            self.screen.blit(self.font.render(txt, True, col), (info_rect.x+5, iy)); iy += 20
            
        if self.active_events:
            evt = self.active_events[-1]
            self.screen.blit(self.font.render(f"Event: {evt['name']}", True, PURPLE), (info_rect.x, info_rect.bottom + 5))

        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_pass)
        pygame.draw.rect(self.screen, WHITE, self.btn_pass, 2)
        self.screen.blit(self.font_bold.render("PASS TURN", True, WHITE), (self.btn_pass.x + 35, self.btn_pass.y + 15))

        pygame.draw.rect(self.screen, BLACK, self.log_rect)
        pygame.draw.rect(self.screen, GRAY, self.log_rect, 1)
        visible_logs = self.logs[self.log_scroll_offset : self.log_scroll_offset + self.max_log_lines]
        ly = self.log_rect.y + 5
        for text, col in visible_logs:
            self.screen.blit(self.font.render(f"> {text}", True, col), (self.log_rect.x + 5, ly)); ly += 18

    # (Menu drawing is standard, preserved)
    def draw_menu(self):
        title = self.font_title.render("CITY ROGUE v3.3", True, WHITE)
        self.screen.blit(title, (50, 50))
        btn_x = 50; start_y = 150
        self.btn_start = pygame.Rect(btn_x, start_y, 200, 50)
        self.btn_load = pygame.Rect(btn_x, start_y+70, 200, 50)
        self.btn_settings = pygame.Rect(btn_x, start_y+140, 200, 50)
        self.btn_quit = pygame.Rect(btn_x, start_y+210, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_start); pygame.draw.rect(self.screen, WHITE, self.btn_start, 2)
        self.screen.blit(self.font_menu.render("NEW GAME", True, WHITE), (self.btn_start.x+40, self.btn_start.y+10))
        lcol = WHITE if os.path.exists(SAVE_FILE) else GRAY
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_load); pygame.draw.rect(self.screen, lcol, self.btn_load, 2)
        self.screen.blit(self.font_menu.render("LOAD GAME", True, lcol), (self.btn_load.x+35, self.btn_load.y+10))
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_settings); pygame.draw.rect(self.screen, WHITE, self.btn_settings, 2)
        self.screen.blit(self.font_menu.render("SETTINGS", True, WHITE), (self.btn_settings.x+45, self.btn_settings.y+10))
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_quit); pygame.draw.rect(self.screen, WHITE, self.btn_quit, 2)
        self.screen.blit(self.font_menu.render("QUIT", True, WHITE), (self.btn_quit.x+70, self.btn_quit.y+10))
        lb_x = 400; lb_y = 150
        self.screen.blit(self.font_title.render("TOP MAYORS", True, GOLD), (lb_x, 50))
        pygame.draw.rect(self.screen, (20, 20, 25), (lb_x, lb_y - 10, 400, 300))
        pygame.draw.rect(self.screen, GOLD, (lb_x, lb_y - 10, 400, 300), 2)
        if not self.high_scores:
            self.screen.blit(self.font_menu.render("No records yet.", True, GRAY), (lb_x + 20, lb_y + 20))
        else:
            dy = 0
            for i, score in enumerate(self.high_scores):
                color = GOLD if i == 0 else WHITE
                s_txt = f"{i+1}. {score['score']} pts - {score['status']}"
                d_txt = f"   {score['date']}"
                self.screen.blit(self.font_bold.render(s_txt, True, color), (lb_x + 20, lb_y + 20 + dy))
                self.screen.blit(self.font.render(d_txt, True, GRAY), (lb_x + 20, lb_y + 40 + dy))
                dy += 55

    def handle_menu_click(self, mx, my):
        if self.btn_start.collidepoint(mx, my): self.reset_game_data(); self.state = STATE_RELIC
        elif self.btn_load.collidepoint(mx, my): 
            if os.path.exists(SAVE_FILE): self.load_game()
        elif self.btn_settings.collidepoint(mx, my): self.state = STATE_SETTINGS
        elif self.btn_quit.collidepoint(mx, my): pygame.quit(); sys.exit()

    def draw_relic_screen(self):
        title = self.font_title.render("CHOOSE A RELIC", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.relic_rects = []
        y = 150
        for r in self.relics:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y, 400, 100)
            pygame.draw.rect(self.screen, DARK_GRAY, rect); pygame.draw.rect(self.screen, tuple(r["color"]), rect, 2)
            self.screen.blit(self.font_bold.render(r["name"], True, tuple(r["color"])), (rect.x+20, rect.y+20))
            self.screen.blit(self.font.render(r["desc"], True, WHITE), (rect.x+20, rect.y+50))
            self.relic_rects.append((rect, r))
            y += 120

    def handle_relic_click(self, mx, my):
        for rect, relic in self.relic_rects:
            if rect.collidepoint(mx, my):
                self.relic = relic
                if relic["id"] == "tycoon": self.money = 1000
                self.log(f"Relic: {relic['name']}", tuple(relic["color"]))
                self.recalc_stats()
                self.state = STATE_GAME

    def draw_settings(self):
        title = self.font_title.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.btn_diff = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 50)
        col = GREEN if self.difficulty == "Normal" else RED
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_diff); pygame.draw.rect(self.screen, col, self.btn_diff, 2)
        self.screen.blit(self.font_menu.render(f"Difficulty: {self.difficulty}", True, col), self.btn_diff.move(20,10))
        self.btn_back = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_back); pygame.draw.rect(self.screen, WHITE, self.btn_back, 2)
        self.screen.blit(self.font_menu.render("BACK", True, WHITE), self.btn_back.move(70,10))

    def handle_settings_click(self, mx, my):
        if self.btn_diff.collidepoint(mx, my): self.difficulty = "Hard" if self.difficulty == "Normal" else "Normal"
        elif self.btn_back.collidepoint(mx, my): self.state = STATE_MENU

if __name__ == "__main__":
    Game().run()