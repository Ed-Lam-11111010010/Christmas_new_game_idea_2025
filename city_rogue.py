import pygame
import sys
import random
import json
import os
from datetime import datetime

# --- Configuration & Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
GRID_SIZE = 10
TILE_SIZE = 42
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 30
MAX_ROUNDS = 20
SAVE_FILE = "city_rogue_save.json"
SCORE_FILE = "city_rogue_scores.json"

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

# --- Game Data ---
BUILDINGS = {
    1: { "name": "House", "symbol": "🏠", "color": GREEN,  "cost": 50,  "energy": -2, "money": 10,  "pop": 5, "work": 0, "happy": -2, "upgrade_to": 5, "upgrade_cost": 100 },
    2: { "name": "Office", "symbol": "🏢", "color": BLUE,   "cost": 100, "energy": -5, "money": 60,  "pop": 0, "work": 5, "happy": -2, "upgrade_to": None },
    3: { "name": "Power",  "symbol": "⚡", "color": YELLOW, "cost": 150, "energy": 20, "money": -10, "pop": 0, "work": 2, "happy": -5, "upgrade_to": None },
    4: { "name": "Park",   "symbol": "🌳", "color": PINK,   "cost": 80,  "energy": 0,  "money": 0,   "pop": 0, "work": 0, "happy": 10, "upgrade_to": None },
    5: { "name": "Apt.",   "symbol": "🏙️", "color": CYAN,   "cost": 0,   "energy": -6, "money": 25,  "pop": 15, "work": 0, "happy": -5, "upgrade_to": None },
    6: { "name": "Shop",   "symbol": "🏪", "color": ORANGE, "cost": 75,  "energy": -3, "money": 5,   "pop": 0, "work": 2, "happy": 2,  "upgrade_to": None }
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Rogue v1.7: Font & UI Fixes")
        self.clock = pygame.time.Clock()
        
        # --- FONT FIX: Use Segoe UI Emoji for everything to support symbols ---
        # If this font isn't found, Pygame falls back to default, so emojis might still fail on non-Windows
        # But this fixes the specific issue seen in screenshots.
        self.font = pygame.font.SysFont("Segoe UI Emoji", 16)
        self.font_bold = pygame.font.SysFont("Segoe UI Emoji", 16, bold=True)
        self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 28)
        self.font_ui = pygame.font.SysFont("Segoe UI Emoji", 18)
        self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 24)

        self.state = STATE_MENU
        self.difficulty = "Normal"
        self.relic = None
        self.high_scores = self.load_scores()
        
        # Initialize Pass Button Rect (Positioned at bottom right)
        self.btn_pass = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 70, 130, 50)
        
        self.reset_game_data()

    def reset_game_data(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
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
        self.max_log_lines = 6     
        self.log_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y + (GRID_SIZE * TILE_SIZE) + 15, 420, 120)
        
        self.log("Welcome Mayor!", WHITE)
        self.recalc_stats()

    # --- SCORE SYSTEM ---
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

    # --- SAVE / LOAD ---
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

    # --- CORE LOGIC ---
    def log(self, text, color=WHITE):
        self.logs.append((text, color))
        if len(self.logs) > self.max_log_lines:
            self.log_scroll_offset = len(self.logs) - self.max_log_lines

    def handle_scroll(self, y_change):
        if len(self.logs) <= self.max_log_lines: return
        self.log_scroll_offset -= y_change
        max_offset = len(self.logs) - self.max_log_lines
        self.log_scroll_offset = max(0, min(self.log_scroll_offset, max_offset))

    def get_cost(self, b_id):
        base = BUILDINGS[b_id]["cost"]
        if base == 0: return 0
        if self.relic:
            if self.relic["id"] == "industrialist" and b_id == 3: return 50
            if self.relic["id"] == "tycoon": base = int(base * 1.2)
        return int(base * self.mods["cost_mult"])

    def get_neighbors(self, r, c):
        n = []
        if r > 0: n.append(self.grid[r-1][c])
        if r < GRID_SIZE-1: n.append(self.grid[r+1][c])
        if c > 0: n.append(self.grid[r][c-1])
        if c < GRID_SIZE-1: n.append(self.grid[r][c+1])
        return n

    def handle_grid_click(self, r, c):
        if self.game_over: return
        if self.popup_active:
            if (r, c) != self.popup_coords: self.popup_active = False
            return
        b_id = self.grid[r][c]
        if b_id == 0: self.build(r, c)
        else:
            self.popup_active = True
            self.popup_coords = (r, c)

    def build(self, r, c):
        cost = self.get_cost(self.selected_building)
        if self.money >= cost:
            self.money -= cost
            self.grid[r][c] = self.selected_building
            self.log(f"Built {BUILDINGS[self.selected_building]['name']}", GREEN)
            self.recalc_stats()
        else:
            self.log(f"Need ${cost}!", RED)

    def upgrade_building(self):
        r, c = self.popup_coords
        b_data = BUILDINGS[self.grid[r][c]]
        if b_data["upgrade_to"]:
            up_id = b_data["upgrade_to"]
            up_cost = b_data["upgrade_cost"]
            if self.money >= up_cost:
                self.money -= up_cost
                self.grid[r][c] = up_id
                self.log(f"Upgraded!", CYAN)
                self.popup_active = False
                self.recalc_stats()

    def demolish_building(self):
        r, c = self.popup_coords
        b_id = self.grid[r][c]
        refund = int(self.get_cost(b_id) * 0.5)
        self.money += refund
        self.grid[r][c] = 0
        self.log(f"Sold (+${refund})", GRAY)
        self.popup_active = False
        self.recalc_stats()

    def recalc_stats(self):
        total_pop = 0
        total_jobs = 0
        raw_happy = 50 + self.mods["happy_flat"]
        if self.relic and self.relic["id"] == "ecotopia": raw_happy += 10
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    b = BUILDINGS[b_id]
                    pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                    total_pop += pop_gain
                    total_jobs += b["work"]
                    
                    happy_effect = b["happy"]
                    neighbors = self.get_neighbors(r, c)
                    if b_id in [1, 5] and 3 in neighbors: 
                        happy_effect -= 5
                        if self.relic and self.relic["id"] == "industrialist": happy_effect -= 5
                    if b_id in [1, 5] and 4 in neighbors: happy_effect += 5
                    if self.relic and self.relic["id"] == "ecotopia" and b_id == 4: happy_effect += 10
                    raw_happy += happy_effect

        self.population = total_pop
        self.jobs_needed = total_jobs
        if self.jobs_needed > 0: self.efficiency = min(1.0, self.population / self.jobs_needed)
        else: self.efficiency = 1.0
        self.happiness = max(0, min(100, raw_happy))

    def calculate_turn_income(self):
        money_change = 0
        energy_change = 0
        happy_mult = 1.0
        if self.happiness >= 80: happy_mult = 1.2
        elif self.happiness <= 30: happy_mult = 0.5

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    b = BUILDINGS[b_id]
                    eff = self.efficiency if b["work"] > 0 else 1.0
                    neighbors = self.get_neighbors(r, c)
                    
                    base_money = b["money"]
                    if b_id == 6:
                        residents = neighbors.count(1) + neighbors.count(5)
                        base_money += (residents * 15)
                    if b_id == 6 and 2 in neighbors: base_money += 10
                    if b_id == 2 and 4 in neighbors: base_money = int(base_money * 1.2)
                    if self.relic and self.relic["id"] == "ecotopia" and b_id == 2:
                        base_money = int(base_money * 0.8)

                    if base_money > 0:
                        gain = base_money * eff * happy_mult
                        if b["name"] == "Office": gain *= self.mods["money_mult"]
                        money_change += gain
                    else:
                        money_change += base_money

                    base_en = b["energy"]
                    if base_en > 0: energy_change += (base_en + self.mods["energy_flat"]) * eff
                    else: energy_change += base_en * eff
                    
        return int(money_change), int(energy_change)

    def predict_building_effects(self, r, c, b_id):
        effects = []
        neighbors = self.get_neighbors(r, c)
        
        # Using Icons for preview
        if b_id == 6:
            residents = neighbors.count(1) + neighbors.count(5)
            if residents > 0: effects.append(f"Combo: +{residents*15}💰 (Residents)")
            if 2 in neighbors: effects.append(f"Combo: +10💰 (Lunch Rush)")
        if b_id == 2 and 4 in neighbors: effects.append("Scenic: +20%💰")
        if b_id in [1, 5]:
            if 3 in neighbors: effects.append("⚠ NIMBY: -5😊 (Pollution)")
            if 4 in neighbors: effects.append("Scenic: +5😊 (Park)")
        
        if b_id == 3:
            residents_hit = neighbors.count(1) + neighbors.count(5)
            if residents_hit > 0: effects.append(f"⚠ Angers Neighbors! (-{residents_hit*5}😊)")
        if b_id == 4:
            if 1 in neighbors or 5 in neighbors: effects.append("Boosts Neighbors! (+5😊)")
            if 2 in neighbors: effects.append("Boosts Office! (+20%💰)")
        if b_id == 2:
            if 6 in neighbors: effects.append("Boosts Shop! (+10💰)")
        if b_id in [1, 5]:
            if 6 in neighbors: effects.append("Boosts Shop! (+15💰)")
            
        return effects

    def next_turn(self):
        if self.game_over: return
        self.popup_active = False 
        
        if self.round % 5 == 0 and self.round < MAX_ROUNDS:
            event = random.choice(EVENTS)
            self.active_events.append(event)
            if event["type"] == "cost": self.mods["cost_mult"] *= event["val"]
            elif event["type"] == "pop_mod": self.mods["pop_flat"] += event["val"]
            elif event["type"] == "money_mult": self.mods["money_mult"] *= event["val"]
            elif event["type"] == "energy_flat": self.mods["energy_flat"] += event["val"]
            elif event["type"] == "happy_flat": self.mods["happy_flat"] += event["val"]
            
            self.log(f"⚠ EVENT: {event['name']}", PURPLE)
            self.log(f"   {event['desc']}", PURPLE)

        self.recalc_stats()
        
        energy_penalty = -15 if self.energy < 0 else 0
        self.happiness = max(0, min(100, self.happiness + energy_penalty))
        if self.efficiency < 1.0: self.log(f"Low Labor! {int(self.efficiency*100)}% Eff", ORANGE)
        if self.energy < 0: self.log("Blackout! -15😊", RED)
        
        m_gain, e_gain = self.calculate_turn_income()
        self.money += m_gain
        self.energy = 10 + e_gain
        self.round += 1
        self.log(f"--- Round {self.round-1} End ---", GRAY)

        if self.money < 0:
            self.game_over = True; self.win = False; 
            self.log("BANKRUPT!", RED); 
            self.save_high_score()
            self.delete_save()
        elif self.round > MAX_ROUNDS:
            self.game_over = True; self.win = True; 
            self.log("VICTORY!", GREEN); 
            self.save_high_score()
            self.delete_save()
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
                    elif self.state == STATE_GAME: self.handle_game_click(mx, my, event.button)

                if event.type == pygame.MOUSEWHEEL and self.state == STATE_GAME:
                    mx, my = pygame.mouse.get_pos()
                    if self.log_rect.collidepoint(mx, my): self.handle_scroll(event.y)

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_GAME:
                        if event.key == pygame.K_1: self.selected_building = 1
                        if event.key == pygame.K_2: self.selected_building = 2
                        if event.key == pygame.K_3: self.selected_building = 3
                        if event.key == pygame.K_4: self.selected_building = 4
                        if event.key == pygame.K_5: self.selected_building = 6 
                        if event.key == pygame.K_SPACE: self.next_turn()
                        if event.key == pygame.K_ESCAPE: 
                            if not self.game_over: self.save_game()
                            self.state = STATE_MENU

            self.screen.fill(UI_BG)
            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_RELIC: self.draw_relic_screen()
            elif self.state == STATE_SETTINGS: self.draw_settings()
            elif self.state == STATE_GAME: self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

    # --- DRAWING ---
    def draw_menu(self):
        title = self.font_title.render("CITY ROGUE v1.7", True, WHITE)
        self.screen.blit(title, (50, 50))
        
        btn_x = 50
        start_y = 150
        self.btn_start = pygame.Rect(btn_x, start_y, 200, 50)
        self.btn_load = pygame.Rect(btn_x, start_y + 70, 200, 50)
        self.btn_settings = pygame.Rect(btn_x, start_y + 140, 200, 50)
        self.btn_quit = pygame.Rect(btn_x, start_y + 210, 200, 50)
        
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_start); pygame.draw.rect(self.screen, WHITE, self.btn_start, 2)
        self.screen.blit(self.font_menu.render("NEW GAME", True, WHITE), (self.btn_start.x+40, self.btn_start.y+10))
        
        has_save = os.path.exists(SAVE_FILE)
        lcol = WHITE if has_save else GRAY
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_load); pygame.draw.rect(self.screen, lcol, self.btn_load, 2)
        self.screen.blit(self.font_menu.render("LOAD GAME", True, lcol), (self.btn_load.x+35, self.btn_load.y+10))
        
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_settings); pygame.draw.rect(self.screen, WHITE, self.btn_settings, 2)
        self.screen.blit(self.font_menu.render("SETTINGS", True, WHITE), (self.btn_settings.x+45, self.btn_settings.y+10))
        
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_quit); pygame.draw.rect(self.screen, WHITE, self.btn_quit, 2)
        self.screen.blit(self.font_menu.render("QUIT", True, WHITE), (self.btn_quit.x+70, self.btn_quit.y+10))

        lb_x = 400
        lb_y = 150
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
        if self.btn_start.collidepoint(mx, my):
            self.reset_game_data()
            self.state = STATE_RELIC
        elif self.btn_load.collidepoint(mx, my):
            if os.path.exists(SAVE_FILE): self.load_game()
        elif self.btn_settings.collidepoint(mx, my): 
            self.state = STATE_SETTINGS
        elif self.btn_quit.collidepoint(mx, my):
            pygame.quit(); sys.exit()

    def draw_relic_screen(self):
        title = self.font_title.render("CHOOSE A RELIC", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        self.relic_rects = []
        y = 150
        for r in RELICS:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y, 400, 100)
            pygame.draw.rect(self.screen, DARK_GRAY, rect)
            pygame.draw.rect(self.screen, r["color"], rect, 2)
            name = self.font_bold.render(r["name"], True, r["color"])
            desc = self.font.render(r["desc"], True, WHITE)
            self.screen.blit(name, (rect.x + 20, rect.y + 20))
            self.screen.blit(desc, (rect.x + 20, rect.y + 50))
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
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_diff)
        pygame.draw.rect(self.screen, col, self.btn_diff, 2)
        txt = self.font_menu.render(f"Difficulty: {self.difficulty}", True, col)
        self.screen.blit(txt, txt.get_rect(center=self.btn_diff.center))
        self.btn_back = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_back)
        pygame.draw.rect(self.screen, WHITE, self.btn_back, 2)
        txt = self.font_menu.render("BACK", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.btn_back.center))

    def handle_settings_click(self, mx, my):
        if self.btn_diff.collidepoint(mx, my):
            self.difficulty = "Hard" if self.difficulty == "Normal" else "Normal"
        elif self.btn_back.collidepoint(mx, my):
            self.state = STATE_MENU

    def handle_game_click(self, mx, my, btn):
        if self.popup_active:
            clicked = False
            for rect, action in self.popup_rects:
                if rect.collidepoint(mx, my):
                    if action == "UPGRADE": self.upgrade_building()
                    elif action == "SELL": self.demolish_building()
                    elif action == "CLOSE": self.popup_active = False
                    clicked = True
            if not clicked: self.popup_active = False
            return
        
        # Pass Button Logic
        if self.btn_pass.collidepoint(mx, my):
            self.next_turn()
            return
        
        tb_start_x = 480; tb_y = 300 
        for i, b_id in enumerate([1, 2, 3, 4, 6]):
            rect = pygame.Rect(tb_start_x + i*65, tb_y, 55, 55)
            if rect.collidepoint(mx, my):
                self.selected_building = b_id
                return
        gx = (mx - GRID_OFFSET_X) // TILE_SIZE
        gy = (my - GRID_OFFSET_Y) // TILE_SIZE
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            self.handle_grid_click(gy, gx)

    def draw_game(self):
        # Grid
        mx, my = pygame.mouse.get_pos()
        hover_gx = (mx - GRID_OFFSET_X) // TILE_SIZE
        hover_gy = (my - GRID_OFFSET_Y) // TILE_SIZE
        valid_hover = (0 <= hover_gx < GRID_SIZE and 0 <= hover_gy < GRID_SIZE and not self.popup_active)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + c*TILE_SIZE, GRID_OFFSET_Y + r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (20,20,20), rect)
                pygame.draw.rect(self.screen, (60,60,60), rect, 1)
                
                # Draw Highlight
                if valid_hover and r == hover_gy and c == hover_gx and self.grid[r][c] == 0:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 2)

                b_id = self.grid[r][c]
                if b_id != 0:
                    inner = rect.inflate(-4,-4)
                    pygame.draw.rect(self.screen, BUILDINGS[b_id]["color"], inner)
                    txt = self.font_icon.render(BUILDINGS[b_id]["symbol"], True, BLACK)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))
        
        # Log Box
        pygame.draw.rect(self.screen, BLACK, self.log_rect)
        pygame.draw.rect(self.screen, GRAY, self.log_rect, 1)
        visible_logs = self.logs[self.log_scroll_offset : self.log_scroll_offset + self.max_log_lines]
        ly = self.log_rect.y + 5
        for text, col in visible_logs:
            self.screen.blit(self.font.render(f"> {text}", True, col), (self.log_rect.x + 10, ly))
            ly += 18
            
        # UI Stats
        ui_x = 480; y = 30
        self.screen.blit(self.font_title.render(f"Round {min(self.round, MAX_ROUNDS)}", True, WHITE), (ui_x, y))
        y += 50
        stats = [
            (f"💰 Money: ${self.money}", GREEN if self.money > 0 else RED),
            (f"⚡ Energy: {self.energy}", YELLOW if self.energy >= 0 else RED),
            (f"👥 Pop: {self.population} / 💼 Jobs: {self.jobs_needed}", WHITE),
            (f"😊 Happy: {int(self.happiness)}%", PINK if self.happiness > 50 else RED)
        ]
        for s, col in stats:
            self.screen.blit(self.font_ui.render(s, True, col), (ui_x, y))
            y += 25
        
        if self.relic:
            y += 5
            self.screen.blit(self.font_bold.render(f"Relic: {self.relic['name']}", True, self.relic["color"]), (ui_x, y))
            y += 20
        
        # Toolbar
        tb_start_x = 480; tb_y = 300
        self.screen.blit(self.font_bold.render("Build:", True, WHITE), (ui_x, tb_y - 25))
        for i, b_id in enumerate([1, 2, 3, 4, 6]):
            rect = pygame.Rect(tb_start_x + i*65, tb_y, 55, 55)
            is_sel = (self.selected_building == b_id)
            pygame.draw.rect(self.screen, BUILDINGS[b_id]["color"] if is_sel else DARK_GRAY, rect)
            pygame.draw.rect(self.screen, WHITE if is_sel else GRAY, rect, 2)
            icon = self.font_icon.render(BUILDINGS[b_id]["symbol"], True, WHITE if not is_sel else BLACK)
            self.screen.blit(icon, icon.get_rect(center=rect.center))

        # PASS BUTTON
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_pass)
        pygame.draw.rect(self.screen, WHITE, self.btn_pass, 2)
        pass_txt1 = self.font_bold.render("PASS", True, WHITE)
        pass_txt2 = self.font.render("TURN", True, GRAY)
        self.screen.blit(pass_txt1, (self.btn_pass.x + 45, self.btn_pass.y + 8))
        self.screen.blit(pass_txt2, (self.btn_pass.x + 45, self.btn_pass.y + 28))

        # Predictive Info Box
        desc_rect = pygame.Rect(ui_x, tb_y + 65, 350, 90)
        pygame.draw.rect(self.screen, (40, 40, 50), desc_rect)
        pygame.draw.rect(self.screen, GRAY, desc_rect, 1)

        lines_to_draw = []
        sel = self.selected_building
        sel_b = BUILDINGS[sel]
        
        if valid_hover and self.grid[hover_gy][hover_gx] == 0:
            cost_val = self.get_cost(sel)
            effects = self.predict_building_effects(hover_gy, hover_gx, sel)
            cost_col = RED if self.mods['cost_mult'] > 1.0 else sel_b["color"]
            warn_str = "(Inflation)" if self.mods['cost_mult'] > 1.0 else ""
            lines_to_draw.append((f"PREVIEW: {sel_b['name']} -{cost_val}💰 {warn_str}", cost_col))
            if effects:
                for eff in effects:
                    col = RED if "⚠" in eff else GREEN
                    lines_to_draw.append((eff, col))
            else:
                lines_to_draw.append(("No adjacency bonuses here.", GRAY))
        else:
            cost_val = self.get_cost(sel)
            lines_to_draw.append((f"{sel_b['name']} ({cost_val}💰)", sel_b["color"]))
            lines_to_draw.append((f"👥 {sel_b['pop']} | 💼 {sel_b['work']} | ⚡ {sel_b['energy']:+}", WHITE))
            if sel == 6: lines_to_draw.append(("Tip: Place near Houses!", ORANGE))
            elif sel == 2: lines_to_draw.append(("Tip: Place near Parks!", BLUE))
            elif sel == 3: lines_to_draw.append(("Tip: Keep away from Houses!", RED))
            elif sel == 4: lines_to_draw.append(("Tip: Boosts neighbors!", PINK))

        dy = 8
        for txt, col in lines_to_draw:
            self.screen.blit(self.font.render(txt, True, col), (desc_rect.x+10, desc_rect.y+dy))
            dy += 20

        # Popups
        if self.popup_active:
            self.popup_rects = []
            pr, pc = self.popup_coords
            px = GRID_OFFSET_X + pc * TILE_SIZE + 20
            py = GRID_OFFSET_Y + pr * TILE_SIZE - 20
            popup_bg = pygame.Rect(px, py, 140, 100)
            pygame.draw.rect(self.screen, BLACK, popup_bg); pygame.draw.rect(self.screen, WHITE, popup_bg, 2)
            b_data = BUILDINGS[self.grid[pr][pc]]
            
            up_rect = pygame.Rect(px+10, py+10, 120, 25)
            if b_data["upgrade_to"]:
                up_cost = b_data["upgrade_cost"]
                col = CYAN if self.money >= up_cost else RED
                pygame.draw.rect(self.screen, DARK_GRAY, up_rect); pygame.draw.rect(self.screen, col, up_rect, 1)
                self.screen.blit(self.font.render(f"Upgrade {up_cost}💰", True, col), (px+15, py+14))
                self.popup_rects.append((up_rect, "UPGRADE"))
            else:
                pygame.draw.rect(self.screen, (30,30,30), up_rect)
                self.screen.blit(self.font.render("Max Level", True, GRAY), (px+15, py+14))
            
            sell_rect = pygame.Rect(px+10, py+40, 120, 25)
            pygame.draw.rect(self.screen, DARK_GRAY, sell_rect); pygame.draw.rect(self.screen, WHITE, sell_rect, 1)
            refund = int(self.get_cost(self.grid[pr][pc]) * 0.5)
            self.screen.blit(self.font.render(f"Sell (+{refund}💰)", True, WHITE), (px+15, py+44))
            self.popup_rects.append((sell_rect, "SELL"))
            
            close_rect = pygame.Rect(px+115, py-10, 20, 20)
            pygame.draw.rect(self.screen, RED, close_rect)
            self.screen.blit(self.font_bold.render("X", True, WHITE), (px+119, py-9))
            self.popup_rects.append((close_rect, "CLOSE"))
            
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0,0))
            msg = "VICTORY!" if self.win else "BANKRUPT"
            col = GREEN if self.win else RED
            txt = self.font_title.render(msg, True, col)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
            sub = self.font.render("Press ESC to Main Menu", True, WHITE)
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

if __name__ == "__main__":
    Game().run()