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

# --- Game Data ---
BUILDINGS = {
    1: { "name": "House", "symbol": "🏠", "color": GREEN,  "cost": 50,  "energy": -2, "money": 10,  "pop": 5, "work": 0, "happy": -2, "upgrade_to": 5, "upgrade_cost": 100, "needs_road": True, "size": (2,2) },
    2: { "name": "Office", "symbol": "🏢", "color": BLUE,   "cost": 100, "energy": -5, "money": 60,  "pop": 0, "work": 5, "happy": -2, "upgrade_to": None, "needs_road": True, "size": (2,2) },
    3: { "name": "Power",  "symbol": "⚡", "color": YELLOW, "cost": 150, "energy": 20, "money": -10, "pop": 0, "work": 2, "happy": -5, "upgrade_to": None, "needs_road": True, "size": (2,2) },
    4: { "name": "Park",   "symbol": "🌳", "color": PINK,   "cost": 80,  "energy": 0,  "money": 0,   "pop": 0, "work": 0, "happy": 10, "upgrade_to": None, "needs_road": False, "size": (2,2) },
    5: { "name": "Apt.",   "symbol": "🏙️", "color": CYAN,   "cost": 0,   "energy": -6, "money": 25,  "pop": 15, "work": 0, "happy": -5, "upgrade_to": None, "needs_road": True, "size": (2,2) },
    6: { "name": "Shop",   "symbol": "🏪", "color": ORANGE, "cost": 75,  "energy": -3, "money": 5,   "pop": 0, "work": 2, "happy": 2,  "upgrade_to": None, "needs_road": True, "size": (2,2) },
    7: { "name": "Road",   "symbol": "",   "color": ROAD_ACTIVE, "cost": 10, "energy": 0, "money": 0, "pop": 0, "work": 0, "happy": 0, "upgrade_to": None, "needs_road": False, "size": (1,1) },
    8: { "name": "Bridge", "symbol": "🌉", "color": BRIDGE_COL,  "cost": 30, "energy": 0, "money": 0, "pop": 0, "work": 0, "happy": 0, "upgrade_to": None, "needs_road": False, "size": (1,1) }
}

RELICS = [
    {"id": "industrialist", "name": "The Industrialist", "desc": "Power Plants cost $50. Pollution doubled.", "color": GRAY},
    {"id": "ecotopia",      "name": "Ecotopia",          "desc": "Parks give +20 Happy. Offices earn -20%.",  "color": GREEN},
    {"id": "tycoon",        "name": "Tycoon",            "desc": "Start with $1000. All buildings cost +20%.", "color": GOLD}
]

EVENTS = [
    {"id": "inflation", "name": "Hyper Inflation", "desc": "Costs +50%", "type": "cost", "val": 1.5},
    {"id": "plague",    "name": "Viral Outbreak",  "desc": "Houses Pop -2", "type": "pop_mod", "val": -2},
    {"id": "boom",      "name": "Tech Boom",       "desc": "Office $$ +20%", "type": "money_mult", "val": 1.2},
    {"id": "grid_rot",  "name": "Grid Decay",      "desc": "Power -5 Energy", "type": "energy_flat", "val": -5},
    {"id": "protest",   "name": "Civil Unrest",    "desc": "Happiness -10", "type": "happy_flat", "val": -10}
]

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
        pygame.display.set_caption("City Rogue v2.7: Complete")
        self.clock = pygame.time.Clock()
        
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

    def load_sound(self, name, filename):
        path = os.path.join(SFX_DIR, filename)
        if os.path.exists(path):
            try: self.sounds[name] = pygame.mixer.Sound(path)
            except: pass

    def play_sound(self, name):
        if name in self.sounds: self.sounds[name].play()

    def reset_game_data(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.network_map = {} 
        self.network_stats = {} 
        self.generate_river()

        self.money = 500 if self.difficulty == "Normal" else 350
        self.energy = 10
        self.population = 0
        self.happiness = 60
        self.round = 1
        self.game_over = False
        self.win = False
        self.selected_building = 1
        self.relic = None
        
        self.active_events = []
        self.mods = { "cost_mult": 1.0, "pop_flat": 0, "money_mult": 1.0, "energy_flat": 0, "happy_flat": 0 }
        
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
        data = { "grid": self.grid, "money": self.money, "energy": self.energy, "round": self.round, 
                 "difficulty": self.difficulty, "active_events": self.active_events, "mods": self.mods, 
                 "logs": serializable_logs, "relic_id": rid }
        try:
            with open(SAVE_FILE, "w") as f: json.dump(data, f)
        except Exception as e: print(e)

    def load_game(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE, "r") as f: data = json.load(f)
            self.grid = data["grid"]
            self.money = data["money"]
            self.energy = data["energy"]
            self.round = data["round"]
            self.difficulty = data["difficulty"]
            self.active_events = data["active_events"]
            self.mods = data["mods"]
            self.logs = []
            for text, col in data["logs"]: self.logs.append((text, tuple(col)))
            rid = data.get("relic_id")
            if rid:
                for r in RELICS: 
                    if r["id"] == rid: self.relic = r
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
        base = BUILDINGS[b_id]["cost"]
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

    def update_road_networks(self):
        self.network_map = {} 
        visited = set()
        nid = 1
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] in [7, 8] and (r,c) not in visited:
                    q = [(r, c)]
                    visited.add((r, c))
                    self.network_map[(r, c)] = nid
                    while q:
                        curr_r, curr_c = q.pop(0)
                        for nr, nc in self.get_neighbors_coords(curr_r, curr_c):
                            if self.grid[nr][nc] in [7, 8] and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                self.network_map[(nr, nc)] = nid
                                q.append((nr, nc))
                    nid += 1

    def get_building_network_id(self, r, c, b_id):
        w, h = BUILDINGS[b_id]["size"]
        if b_id in [7, 8]: return self.network_map.get((r,c))
        for dr in range(h):
            for dc in range(w):
                for tr, tc in self.get_neighbors_coords(r+dr, c+dc):
                    if (tr, tc) in self.network_map: return self.network_map[(tr, tc)]
        return None

    def can_place_building(self, r, c, b_id):
        w, h = BUILDINGS[b_id]["size"]
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
        if self.money >= cost:
            self.money -= cost
            w, h = BUILDINGS[b_id]["size"]
            for dr in range(h):
                for dc in range(w):
                    self.grid[r+dr][c+dc] = b_id
            self.play_sound("build")
            self.log(f"Built {BUILDINGS[b_id]['name']}", GREEN)
            self.recalc_stats()
        else:
            self.play_sound("error")
            self.log(f"Need ${cost}!", RED)

    def upgrade_building(self):
        r, c = self.popup_coords
        b_id = self.grid[r][c]
        b_data = BUILDINGS[b_id]
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
        w, h = BUILDINGS[b_id]["size"]
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
        self.update_road_networks()
        self.network_stats = {} 
        total_pop = 0
        raw_happy = 50 + self.mods["happy_flat"]
        if self.relic and self.relic["id"] == "ecotopia": raw_happy += 10
        
        processed = set()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r,c) in processed: continue
                b_id = self.grid[r][c]
                if b_id > 0:
                    b = BUILDINGS[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                    jobs_gain = b["work"]
                    total_pop += pop_gain
                    
                    net_id = self.get_building_network_id(r, c, b_id)
                    if net_id:
                        if net_id not in self.network_stats: self.network_stats[net_id] = {"pop": 0, "jobs": 0}
                        self.network_stats[net_id]["pop"] += pop_gain
                        self.network_stats[net_id]["jobs"] += jobs_gain
                    
                    raw_happy += b["happy"]
                    if b["needs_road"] and net_id is None:
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
                    b = BUILDINGS[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    net_id = self.get_building_network_id(r, c, b_id)
                    if b["needs_road"] and net_id is None: continue

                    local_eff = 1.0
                    if b["work"] > 0 and net_id:
                        stats = self.network_stats.get(net_id)
                        if stats and stats["jobs"] > 0:
                            local_eff = min(1.0, stats["pop"] / stats["jobs"])
                    elif b["work"] > 0: local_eff = 0 

                    gain = b["money"]
                    if gain > 0: gain = gain * local_eff
                    money_change += gain
                    energy_change += b["energy"] * local_eff

        return int(money_change), int(energy_change)

    def predict_building_effects(self, r, c, b_id):
        effects = []
        b = BUILDINGS[b_id]
        if b["needs_road"]:
            touches_road = False
            w, h = b["size"]
            for dr in range(h):
                for dc in range(w):
                    for nr, nc in self.get_neighbors_coords(r+dr, c+dc):
                        if self.grid[nr][nc] in [7, 8]: touches_road = True
            if not touches_road: effects.append("⚠ No Road Connection!")

        neighbors = []
        w, h = b["size"]
        for dr in range(h):
            for dc in range(w):
                neighbors.extend(self.get_neighbors(r+dr, c+dc))
        
        if b_id == 6 and (1 in neighbors or 5 in neighbors): effects.append("Combo: +15💰 per Resident")
        if b_id == 2 and 4 in neighbors: effects.append("Scenic: +20%💰")
        if b_id in [1, 5] and 3 in neighbors: effects.append("⚠ NIMBY: -5😊")
        return effects

    def next_turn(self):
        if self.game_over: return
        self.popup_active = False 
        self.play_sound("money")
        
        if self.round % 5 == 0 and self.round < MAX_ROUNDS:
            event = random.choice(EVENTS)
            self.active_events.append(event)
            if event["type"] == "cost": self.mods["cost_mult"] *= event["val"]
            elif event["type"] == "pop_mod": self.mods["pop_flat"] += event["val"]
            elif event["type"] == "money_mult": self.mods["money_mult"] *= event["val"]
            elif event["type"] == "energy_flat": self.mods["energy_flat"] += event["val"]
            elif event["type"] == "happy_flat": self.mods["happy_flat"] += event["val"]
            self.log(f"⚠ EVENT: {event['name']}", PURPLE)

        self.recalc_stats()
        money_change, energy_change = self.calculate_turn_income()
        self.money += money_change
        self.energy = 10 + energy_change
        self.round += 1
        self.log(f"--- Round {self.round-1} End ---", GRAY)

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
                                        if BUILDINGS[b_id]["size"] == (2,2):
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
                    b = BUILDINGS[b_id]
                    w, h = b["size"]
                    for dr in range(h):
                        for dc in range(w): processed.add((r+dr, c+dc))
                    
                    sx, sy = self.world_to_screen(r, c)
                    size = TILE_SIZE * self.zoom
                    b_rect = pygame.Rect(sx, sy, size*w, size*h)
                    
                    col = b["color"]
                    if b_id in [7, 8]:
                        net_id = self.get_building_network_id(r, c, b_id)
                        col = ROAD_ACTIVE if net_id else ROAD_INACTIVE
                        if b_id == 8: col = BRIDGE_COL
                    
                    pygame.draw.rect(self.screen, col, b_rect.inflate(-2,-2))
                    if self.zoom > 0.6:
                        txt = self.font_icon.render(b["symbol"], True, BLACK)
                        self.screen.blit(txt, txt.get_rect(center=b_rect.center))
                    
                    if b["needs_road"] and not self.get_building_network_id(r, c, b_id):
                        self.screen.blit(self.font.render("!", True, RED), b_rect.topleft)

        # Hover
        mx, my = pygame.mouse.get_pos()
        if map_rect.collidepoint(mx, my) and not self.popup_active:
            r, c = self.screen_to_world(mx, my)
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                sel = self.selected_building
                if self.can_place_building(r, c, sel):
                    w, h = BUILDINGS[sel]["size"]
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
            
            b_data = BUILDINGS[self.grid[pr][pc]]
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
        
        stats = [(f"💰 ${self.money}", GREEN), (f"⚡ {self.energy}", YELLOW), (f"👥 {self.population}", WHITE), (f"😊 {int(self.happiness)}%", PINK)]
        for s, c in stats: self.screen.blit(self.font_ui.render(s, True, c), (ui_x, y)); y+=30

        y = 300
        tb_x = SCREEN_WIDTH - 250
        self.screen.blit(self.font_bold.render("Construction:", True, WHITE), (ui_x, y-25))
        keys = [1, 2, 3, 4, 6, 7, 8]
        for i, b_id in enumerate(keys):
            rect = pygame.Rect(tb_x + (i%3)*60, y + (i//3)*60, 50, 50)
            is_sel = (self.selected_building == b_id)
            pygame.draw.rect(self.screen, BUILDINGS[b_id]["color"] if is_sel else DARK_GRAY, rect)
            pygame.draw.rect(self.screen, WHITE if is_sel else GRAY, rect, 2)
            self.screen.blit(self.font_icon.render(BUILDINGS[b_id]["symbol"], True, BLACK), rect.inflate(-10,-10))

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
                 preview_txt.append((f"Cost: -${cost}", RED if self.mods['cost_mult']>1 else WHITE))
                 effects = self.predict_building_effects(r, c, self.selected_building)
                 for e in effects: preview_txt.append((e, GREEN if "Combo" in e or "Scenic" in e else RED))
        
        if not preview_txt:
            sel_b = BUILDINGS[self.selected_building]
            cost = self.get_cost(self.selected_building)
            preview_txt.append((f"{sel_b['name']} (${cost})", sel_b["color"]))
            preview_txt.append((f"Pop: {sel_b['pop']} | Work: {sel_b['work']}", WHITE))
            if sel_b["needs_road"]: preview_txt.append(("⚠ Needs Road Access", ORANGE))
            
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

    def draw_menu(self):
        title = self.font_title.render("CITY ROGUE v2.7", True, WHITE)
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
        for r in RELICS:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y, 400, 100)
            pygame.draw.rect(self.screen, DARK_GRAY, rect); pygame.draw.rect(self.screen, r["color"], rect, 2)
            self.screen.blit(self.font_bold.render(r["name"], True, r["color"]), (rect.x+20, rect.y+20))
            self.screen.blit(self.font.render(r["desc"], True, WHITE), (rect.x+20, rect.y+50))
            self.relic_rects.append((rect, r))
            y += 120

    def handle_relic_click(self, mx, my):
        for rect, relic in self.relic_rects:
            if rect.collidepoint(mx, my):
                self.relic = relic
                if relic["id"] == "tycoon": self.money = 1000
                self.log(f"Relic: {relic['name']}", relic["color"])
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