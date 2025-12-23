import pygame
import sys
import random

# --- Configuration & Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

GRID_SIZE = 10
TILE_SIZE = 42
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 30
MAX_ROUNDS = 20

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

# --- Game Data ---
BUILDINGS = {
    1: { "name": "House", "symbol": "🏠", "color": GREEN,  "cost": 50,  "energy": -2, "money": 10,  "pop": 5, "work": 0, "happy": -2, "upgrade_to": 5, "upgrade_cost": 100 },
    2: { "name": "Office", "symbol": "🏢", "color": BLUE,   "cost": 100, "energy": -5, "money": 60,  "pop": 0, "work": 5, "happy": -2, "upgrade_to": None },
    3: { "name": "Power",  "symbol": "⚡", "color": YELLOW, "cost": 150, "energy": 20, "money": -10, "pop": 0, "work": 2, "happy": -5, "upgrade_to": None },
    4: { "name": "Park",   "symbol": "🌳", "color": PINK,   "cost": 80,  "energy": 0,  "money": 0,   "pop": 0, "work": 0, "happy": 10, "upgrade_to": None },
    5: { "name": "Apt.",   "symbol": "🏙️", "color": CYAN,   "cost": 0,   "energy": -6, "money": 25,  "pop": 15, "work": 0, "happy": -5, "upgrade_to": None } 
}

EVENTS = [
    {"id": "inflation", "name": "Hyper Inflation", "desc": "Building costs increased by 50%", "type": "cost", "val": 1.5},
    {"id": "plague",    "name": "Viral Outbreak",  "desc": "Houses capacity reduced by 2", "type": "pop_mod", "val": -2},
    {"id": "boom",      "name": "Tech Boom",       "desc": "Office income increased by 20%", "type": "money_mult", "val": 1.2},
    {"id": "grid_rot",  "name": "Grid Decay",      "desc": "Power Plants output -5 Energy", "type": "energy_flat", "val": -5},
    {"id": "protest",   "name": "Civil Unrest",    "desc": "Global Happiness dropped by 10", "type": "happy_flat", "val": -10}
]

STATE_MENU = 0
STATE_GAME = 1
STATE_SETTINGS = 2

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Rogue v0.9")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 15)
        self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 28)
        self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 24)

        self.state = STATE_MENU
        self.difficulty = "Normal"
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
        self.log(f"Difficulty: {self.difficulty}", GRAY)
        
        self.recalc_stats()

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
        return int(base * self.mods["cost_mult"])

    def handle_grid_click(self, r, c):
        if self.game_over: return
        
        if self.popup_active:
            if (r, c) != self.popup_coords: self.popup_active = False
            return

        b_id = self.grid[r][c]
        if b_id == 0:
            self.build(r, c)
        else:
            self.popup_active = True
            self.popup_coords = (r, c)

    def build(self, r, c):
        cost = self.get_cost(self.selected_building)
        if self.money >= cost:
            self.money -= cost
            self.grid[r][c] = self.selected_building
            name = BUILDINGS[self.selected_building]['name']
            self.log(f"Built {name} (-${cost})", GREEN)
            self.recalc_stats()
        else:
            self.log(f"Not enough funds! Need ${cost}", RED)

    def upgrade_building(self):
        r, c = self.popup_coords
        b_data = BUILDINGS[self.grid[r][c]]
        if b_data["upgrade_to"]:
            up_id = b_data["upgrade_to"]
            up_cost = b_data["upgrade_cost"]
            if self.money >= up_cost:
                self.money -= up_cost
                self.grid[r][c] = up_id
                self.log(f"Upgraded to {BUILDINGS[up_id]['name']}!", CYAN)
                self.popup_active = False
                self.recalc_stats()
            else:
                self.log(f"Need ${up_cost} to upgrade.", RED)

    def demolish_building(self):
        r, c = self.popup_coords
        b_id = self.grid[r][c]
        refund = int(self.get_cost(b_id) * 0.5)
        self.money += refund
        self.grid[r][c] = 0
        self.log(f"Demolished (+${refund})", GRAY)
        self.popup_active = False
        self.recalc_stats()

    def recalc_stats(self):
        total_pop = 0
        total_jobs = 0
        raw_happy = 50 + self.mods["happy_flat"]
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    b = BUILDINGS[b_id]
                    pop_gain = max(0, b["pop"] + (self.mods["pop_flat"] if b["pop"] > 0 else 0))
                    total_pop += pop_gain
                    total_jobs += b["work"]
                    raw_happy += b["happy"]

        self.population = total_pop
        self.jobs_needed = total_jobs
        
        if self.jobs_needed > 0:
            self.efficiency = min(1.0, self.population / self.jobs_needed)
        else:
            self.efficiency = 1.0

        self.happiness = max(0, min(100, raw_happy))

    def next_turn(self):
        if self.game_over: return
        self.popup_active = False 
        
        # 1. Random Event (Every 5 Rounds)
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

        # 2. Detailed Logs for Player Feedback (Before changing values)
        # Check Efficiency
        if self.efficiency < 1.0:
            eff_pct = int(self.efficiency * 100)
            self.log(f"⚠ Labor Shortage! Buildings at {eff_pct}% Eff", ORANGE)
        
        # Check Energy (Pre-calc)
        if self.energy < 0:
            self.log("⚡ Blackout! Happiness -15", RED)
        
        # Check Happiness
        if self.happiness >= 80:
            self.log("Happy Populace! Income +20%", PINK)
        elif self.happiness <= 30:
            self.log("Civil Unrest! Income -50%", RED)

        # 3. Apply Production
        money_change = 0
        energy_change = 0
        
        energy_penalty = -15 if self.energy < 0 else 0
        self.happiness = max(0, min(100, self.happiness + energy_penalty))
        
        happy_mult = 1.0
        if self.happiness >= 80: happy_mult = 1.2
        elif self.happiness <= 30: happy_mult = 0.5

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    b = BUILDINGS[b_id]
                    eff = self.efficiency if b["work"] > 0 else 1.0
                    
                    if b["money"] > 0:
                        gain = b["money"] * eff * happy_mult
                        if b["name"] == "Office": gain *= self.mods["money_mult"]
                        money_change += gain
                    else:
                        money_change += b["money"]

                    base_en = b["energy"]
                    if base_en > 0: energy_change += (base_en + self.mods["energy_flat"]) * eff
                    else: energy_change += base_en * eff

        self.money += int(money_change)
        self.energy = 10 + int(energy_change)
        self.round += 1
        
        # Final Round Log
        self.log(f"--- Round {self.round-1} Complete ---", GRAY)

        # Win/Loss Check
        if self.money < 0:
            self.game_over = True
            self.log("BANKRUPTCY! Game Over.", RED)
        elif self.round > MAX_ROUNDS:
            self.game_over = True
            self.win = True
            self.log("VICTORY! Simulation Complete.", GREEN)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.state == STATE_MENU:
                        self.handle_menu_click(mx, my)
                    elif self.state == STATE_SETTINGS:
                        self.handle_settings_click(mx, my)
                    elif self.state == STATE_GAME:
                        self.handle_game_click(mx, my, event.button)

                if event.type == pygame.MOUSEWHEEL and self.state == STATE_GAME:
                    mx, my = pygame.mouse.get_pos()
                    if self.log_rect.collidepoint(mx, my):
                        self.handle_scroll(event.y)

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_GAME:
                        if event.key == pygame.K_1: self.selected_building = 1
                        if event.key == pygame.K_2: self.selected_building = 2
                        if event.key == pygame.K_3: self.selected_building = 3
                        if event.key == pygame.K_4: self.selected_building = 4
                        if event.key == pygame.K_SPACE: self.next_turn()
                        if event.key == pygame.K_ESCAPE: self.state = STATE_MENU

            self.screen.fill(UI_BG)
            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_SETTINGS: self.draw_settings()
            elif self.state == STATE_GAME: self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

    def draw_menu(self):
        title = self.font_title.render("CITY ROGUE 2025", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.btn_start = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 50)
        self.btn_settings = pygame.Rect(SCREEN_WIDTH//2 - 100, 320, 200, 50)
        self.btn_quit = pygame.Rect(SCREEN_WIDTH//2 - 100, 390, 200, 50)
        for btn, text in [(self.btn_start, "START GAME"), (self.btn_settings, "SETTINGS"), (self.btn_quit, "QUIT")]:
            pygame.draw.rect(self.screen, DARK_GRAY, btn)
            pygame.draw.rect(self.screen, WHITE, btn, 2)
            txt_surf = self.font_menu.render(text, True, WHITE)
            self.screen.blit(txt_surf, txt_surf.get_rect(center=btn.center))

    def handle_menu_click(self, mx, my):
        if self.btn_start.collidepoint(mx, my):
            self.reset_game_data()
            self.state = STATE_GAME
        elif self.btn_settings.collidepoint(mx, my):
            self.state = STATE_SETTINGS
        elif self.btn_quit.collidepoint(mx, my):
            pygame.quit(); sys.exit()

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
            clicked_action = False
            for rect, action in self.popup_rects:
                if rect.collidepoint(mx, my):
                    if action == "UPGRADE": self.upgrade_building()
                    elif action == "SELL": self.demolish_building()
                    elif action == "CLOSE": self.popup_active = False
                    clicked_action = True
                    break
            if not clicked_action: self.popup_active = False
            return
        tb_start_x = 480; tb_y = 300 
        for i in range(1, 5):
            rect = pygame.Rect(tb_start_x + (i-1)*65, tb_y, 55, 55)
            if rect.collidepoint(mx, my):
                self.selected_building = i
                return
        gx = (mx - GRID_OFFSET_X) // TILE_SIZE
        gy = (my - GRID_OFFSET_Y) // TILE_SIZE
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            self.handle_grid_click(gy, gx)

    def draw_game(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + c*TILE_SIZE, GRID_OFFSET_Y + r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (20,20,20), rect)
                pygame.draw.rect(self.screen, (60,60,60), rect, 1)
                b_id = self.grid[r][c]
                if b_id != 0:
                    inner = rect.inflate(-4,-4)
                    pygame.draw.rect(self.screen, BUILDINGS[b_id]["color"], inner)
                    txt = self.font_icon.render(BUILDINGS[b_id]["symbol"], True, BLACK)
                    self.screen.blit(txt, txt.get_rect(center=rect.center))
        pygame.draw.rect(self.screen, BLACK, self.log_rect)
        pygame.draw.rect(self.screen, GRAY, self.log_rect, 1)
        visible_logs = self.logs[self.log_scroll_offset : self.log_scroll_offset + self.max_log_lines]
        ly = self.log_rect.y + 5
        for text, col in visible_logs:
            self.screen.blit(self.font.render(f"> {text}", True, col), (self.log_rect.x + 10, ly))
            ly += 18
        if len(self.logs) > self.max_log_lines:
            sb_h = max(20, (self.max_log_lines / len(self.logs)) * self.log_rect.height)
            progress = self.log_scroll_offset / (len(self.logs) - self.max_log_lines)
            sb_y = self.log_rect.y + (progress * (self.log_rect.height - sb_h))
            pygame.draw.rect(self.screen, DARK_GRAY, (self.log_rect.right - 5, sb_y, 4, sb_h))
        ui_x = 480; y = 30
        self.screen.blit(self.font_title.render(f"Round {min(self.round, MAX_ROUNDS)}", True, WHITE), (ui_x, y))
        y += 50
        stats = [
            (f"Money: ${self.money}", GREEN if self.money > 0 else RED),
            (f"Energy: {self.energy}", YELLOW if self.energy >= 0 else RED),
            (f"Pop: {self.population} / Jobs: {self.jobs_needed}", WHITE),
            (f"Happiness: {int(self.happiness)}%", PINK if self.happiness > 50 else RED)
        ]
        for s, col in stats:
            self.screen.blit(self.font_bold.render(s, True, col), (ui_x, y))
            y += 22
        y += 10
        self.screen.blit(self.font_bold.render("Active Modifiers:", True, PURPLE), (ui_x, y))
        y += 20
        if not self.active_events:
            self.screen.blit(self.font.render("None", True, GRAY), (ui_x, y))
        for evt in self.active_events:
            self.screen.blit(self.font.render(f"• {evt['name']}", True, PURPLE), (ui_x, y))
            y += 18
        tb_start_x = 480; tb_y = 300
        self.screen.blit(self.font_bold.render("Build:", True, WHITE), (ui_x, tb_y - 25))
        for i in range(1, 5):
            rect = pygame.Rect(tb_start_x + (i-1)*65, tb_y, 55, 55)
            b_id = i; is_sel = (self.selected_building == b_id)
            pygame.draw.rect(self.screen, BUILDINGS[b_id]["color"] if is_sel else DARK_GRAY, rect)
            pygame.draw.rect(self.screen, WHITE if is_sel else GRAY, rect, 2)
            icon = self.font_icon.render(BUILDINGS[b_id]["symbol"], True, WHITE if not is_sel else BLACK)
            self.screen.blit(icon, icon.get_rect(center=rect.center))
        desc_rect = pygame.Rect(ui_x, tb_y + 65, 350, 60)
        pygame.draw.rect(self.screen, (50, 50, 60), desc_rect)
        pygame.draw.rect(self.screen, GRAY, desc_rect, 1)
        sel_b = BUILDINGS[self.selected_building]
        cost_val = int(sel_b['cost'] * self.mods['cost_mult'])
        self.screen.blit(self.font_bold.render(f"{sel_b['name']} (${cost_val})", True, sel_b["color"]), (desc_rect.x+10, desc_rect.y+8))
        self.screen.blit(self.font.render(f"Pop: {sel_b['pop']} | Work: {sel_b['work']} | En: {sel_b['energy']:+}", True, WHITE), (desc_rect.x+10, desc_rect.y+30))
        if self.popup_active:
            self.popup_rects = []
            pr, pc = self.popup_coords
            px = GRID_OFFSET_X + pc * TILE_SIZE + 20
            py = GRID_OFFSET_Y + pr * TILE_SIZE - 20
            popup_bg = pygame.Rect(px, py, 140, 100)
            pygame.draw.rect(self.screen, BLACK, popup_bg)
            pygame.draw.rect(self.screen, WHITE, popup_bg, 2)
            b_data = BUILDINGS[self.grid[pr][pc]]
            up_rect = pygame.Rect(px+10, py+10, 120, 25)
            if b_data["upgrade_to"]:
                up_cost = b_data["upgrade_cost"]
                col = CYAN if self.money >= up_cost else RED
                pygame.draw.rect(self.screen, DARK_GRAY, up_rect)
                pygame.draw.rect(self.screen, col, up_rect, 1)
                self.screen.blit(self.font.render(f"Upgrade ${up_cost}", True, col), (px+15, py+14))
                self.popup_rects.append((up_rect, "UPGRADE"))
            else:
                pygame.draw.rect(self.screen, (30,30,30), up_rect)
                self.screen.blit(self.font.render("Max Level", True, GRAY), (px+15, py+14))
            sell_rect = pygame.Rect(px+10, py+40, 120, 25)
            pygame.draw.rect(self.screen, DARK_GRAY, sell_rect)
            pygame.draw.rect(self.screen, WHITE, sell_rect, 1)
            refund = int(self.get_cost(self.grid[pr][pc]) * 0.5)
            self.screen.blit(self.font.render(f"Sell (+${refund})", True, WHITE), (px+15, py+44))
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