import pygame
from consts import *

class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        # Initialize Fonts
        try:
            self.font = pygame.font.SysFont("Segoe UI Emoji", 16)
            self.font_bold = pygame.font.SysFont("Segoe UI Emoji", 16, bold=True)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 32) # Big Icons
            self.font_ui = pygame.font.SysFont("Segoe UI Emoji", 18)
            self.font_title = pygame.font.SysFont("Segoe UI Emoji", 40, bold=True)
        except:
            self.font = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_icon = pygame.font.SysFont("Arial", 32)
            self.font_ui = pygame.font.SysFont("Arial", 18)
            self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 24)

    def world_to_screen(self, game, r, c):
        wx = c * TILE_SIZE
        wy = r * TILE_SIZE
        sx = (wx - game.cam_x) * game.zoom
        sy = (wy - game.cam_y) * game.zoom
        return sx, sy

    def draw_menu(self, game):
        self.screen.fill(UI_BG)
        w, h = self.screen.get_size()
        
        t = self.font_title.render(f"CITY ROGUE v3.12", True, WHITE)
        self.screen.blit(t, (50, 50))
        
        # Menu Buttons (Left Side)
        btn_w, btn_h = 200, 50
        base_y = 150
        gap = 70
        
        b_st = pygame.Rect(50, base_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, DARK_GRAY, b_st)
        self.screen.blit(self.font_menu.render("NEW GAME", True, WHITE), (70, base_y + 10))
        
        b_ld = pygame.Rect(50, base_y + gap, btn_w, btn_h)
        pygame.draw.rect(self.screen, DARK_GRAY, b_ld)
        self.screen.blit(self.font_menu.render("LOAD GAME", True, WHITE), (70, base_y + gap + 10))
        
        b_stg = pygame.Rect(50, base_y + gap*2, btn_w, btn_h)
        pygame.draw.rect(self.screen, DARK_GRAY, b_stg)
        self.screen.blit(self.font_menu.render("SETTINGS", True, WHITE), (70, base_y + gap*2 + 10))
        
        b_qt = pygame.Rect(50, base_y + gap*3, btn_w, btn_h)
        pygame.draw.rect(self.screen, DARK_GRAY, b_qt)
        self.screen.blit(self.font_menu.render("QUIT", True, WHITE), (90, base_y + gap*3 + 10))
        
        game.menu_buttons = [b_st, b_ld, b_stg, b_qt]
        
        # Leaderboard (Right Side with Frame) - Lower position aligned with buttons
        lb_x = 400
        lb_w = w - 450
        lb_h = 350
        lb_y = 150  # Align with buttons
        
        # Frame
        pygame.draw.rect(self.screen, (20, 20, 25), (lb_x, lb_y, lb_w, lb_h)) # Bg
        pygame.draw.rect(self.screen, GOLD, (lb_x, lb_y, lb_w, lb_h), 2) # Border
        
        header = self.font_title.render("TOP MAYORS", True, GOLD)
        self.screen.blit(header, (lb_x + 20, lb_y + 20))
        
        for i, s in enumerate(game.high_scores):
            txt = self.font.render(f"{i+1}. {s['score']} - {s['status']} ({s['date']})", True, WHITE)
            self.screen.blit(txt, (lb_x + 30, lb_y + 80 + i*40))

    def draw_relic_screen(self, game):
        w, h = self.screen.get_size()
        t = self.font_title.render("CHOOSE RELIC", True, WHITE)
        self.screen.blit(t, (w//2 - t.get_width()//2, 50))
        
        game.relic_rects = []
        start_y = 150
        for r in game.relics:
            rect = pygame.Rect(w//2 - 200, start_y, 400, 100)
            pygame.draw.rect(self.screen, DARK_GRAY, rect)
            pygame.draw.rect(self.screen, tuple(r["color"]), rect, 2)
            self.screen.blit(self.font_bold.render(r["name"], True, tuple(r["color"])), (rect.x+20, rect.y+20))
            self.screen.blit(self.font.render(r["desc"], True, WHITE), (rect.x+20, rect.y+50))
            game.relic_rects.append((rect, r))
            start_y += 120

    def draw_settings(self, game):
        self.screen.fill(UI_BG)
        w, h = self.screen.get_size()
        
        title = self.font_title.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (w//2 - title.get_width()//2, 50))
        
        # Difficulty
        game.btn_diff = pygame.Rect(w//2 - 100, 150, 200, 50)
        col = GREEN if game.difficulty == "Normal" else RED
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_diff)
        pygame.draw.rect(self.screen, col, game.btn_diff, 2)
        self.screen.blit(self.font_menu.render(f"Difficulty: {game.difficulty}", True, col), (game.btn_diff.x+20, game.btn_diff.y+10))

        # Resolution
        game.btn_res = pygame.Rect(w//2 - 125, 230, 250, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_res)
        pygame.draw.rect(self.screen, CYAN, game.btn_res, 2)
        res_txt = f"{game.resolutions[game.res_index][0]}x{game.resolutions[game.res_index][1]}"
        self.screen.blit(self.font_menu.render(f"Screen: {res_txt}", True, CYAN), (game.btn_res.x+30, game.btn_res.y+10))

        # Volume
        vol_width = 200
        vol_x = w//2 - 100
        vol_y = 330
        
        pygame.draw.rect(self.screen, GRAY, (vol_x, vol_y, vol_width, 10))
        pygame.draw.rect(self.screen, BLUE, (vol_x, vol_y, vol_width*game.volume, 10))
        self.screen.blit(self.font_menu.render(f"Volume: {int(game.volume*100)}%", True, WHITE), (vol_x, vol_y - 30))
        
        game.vol_dn = pygame.Rect(vol_x - 40, vol_y - 10, 30, 30)
        pygame.draw.rect(self.screen, DARK_GRAY, game.vol_dn)
        self.screen.blit(self.font.render("-",True,WHITE), (game.vol_dn.x+10, game.vol_dn.y+5))
        
        game.vol_up = pygame.Rect(vol_x + vol_width + 10, vol_y - 10, 30, 30)
        pygame.draw.rect(self.screen, DARK_GRAY, game.vol_up)
        self.screen.blit(self.font.render("+",True,WHITE), (game.vol_up.x+8, game.vol_up.y+5))
        
        game.s_back = pygame.Rect(w//2 - 100, 420, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, game.s_back)
        self.screen.blit(self.font_menu.render("BACK",True,WHITE), (game.s_back.x+70, game.s_back.y+10))

    def draw_game(self, game):
        w, h = self.screen.get_size()
        sidebar_w = 280
        map_w = w - sidebar_w
        
        # 1. Map Area
        self.screen.fill(BLACK)
        map_rect = pygame.Rect(0, 0, map_w, h)
        pygame.draw.rect(self.screen, (20,20,30), map_rect)
        self.screen.set_clip(map_rect)
        
        # Calculate viewport
        cols_visible = int(map_w / (TILE_SIZE * game.zoom)) + 2
        rows_visible = int(h / (TILE_SIZE * game.zoom)) + 2
        
        start_c = int(game.cam_x // TILE_SIZE) - 2
        start_r = int(game.cam_y // TILE_SIZE) - 2
        end_c = start_c + cols_visible
        end_r = start_r + rows_visible
        
        start_c = max(0, start_c); start_r = max(0, start_r)
        end_c = min(GRID_SIZE, end_c); end_r = min(GRID_SIZE, end_r)

        # Terrain
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                sx, sy = self.world_to_screen(game, r, c)
                size = TILE_SIZE * game.zoom
                rect = pygame.Rect(sx, sy, size, size)
                if game.grid[r][c] == -1: pygame.draw.rect(self.screen, RIVER_BLUE, rect)
                else: pygame.draw.rect(self.screen, (30,30,30), rect)
                pygame.draw.rect(self.screen, (50,50,50), rect, 1)

        # Buildings
        processed = set()
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                if (r,c) in processed: continue
                b_id = game.grid[r][c]
                if b_id > 0:
                    b = game.buildings[b_id]
                    bw, bh = b["size"]
                    for dr in range(bh): 
                        for dc in range(bw): processed.add((r+dr, c+dc))
                    
                    sx, sy = self.world_to_screen(game, r, c)
                    size = TILE_SIZE * game.zoom
                    b_rect = pygame.Rect(sx, sy, size*bw, size*bh)
                    
                    col = tuple(b["color"])
                    if b_id in [7, 8]: # Road/Bridge
                        if (r, c) in game.active_road_tiles:
                            col = ROAD_ACTIVE
                            if b_id == 8: col = BRIDGE_COL # Use Bridge Color
                        else:
                            col = ROAD_INACTIVE
                    
                    pygame.draw.rect(self.screen, col, b_rect.inflate(-2,-2))
                    if game.zoom > 0.6:
                        txt = self.font_icon.render(b["symbol"], True, BLACK)
                        self.screen.blit(txt, txt.get_rect(center=b_rect.center))
                    
                    iid = game.get_building_island_id(r,c)
                    is_valid = False
                    if iid and game.island_stats[iid]["active"]: is_valid = True
                    if not b["needs_road"]: is_valid = True
                    if b["needs_road"] and not is_valid:
                        self.screen.blit(self.font.render("!", True, RED), b_rect.topleft)

        # Hover Ghost
        mx, my = pygame.mouse.get_pos()
        if map_rect.collidepoint(mx, my) and not game.popup_active and not game.popup_queue:
            r, c = game.screen_to_world(mx, my)
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                sel = game.selected_building
                if game.can_place_building(r, c, sel):
                    bw, bh = game.buildings[sel]["size"]
                    sx, sy = self.world_to_screen(game, r, c)
                    ghost = pygame.Rect(sx, sy, TILE_SIZE*game.zoom*bw, TILE_SIZE*game.zoom*bh)
                    pygame.draw.rect(self.screen, WHITE, ghost, 2)

        self.screen.set_clip(None)
        self.draw_sidebar(game)
        
        # Popups
        cx, cy = w//2, h//2
        if game.popup_queue:
            ov = pygame.Surface((w, h), pygame.SRCALPHA)
            ov.fill((0,0,0,180))
            self.screen.blit(ov, (0,0))
            t, d, c = game.popup_queue[0]
            box = pygame.Rect(cx-200, cy-75, 400, 150)
            pygame.draw.rect(self.screen, UI_BG, box)
            pygame.draw.rect(self.screen, c, box, 2)
            self.screen.blit(self.font_title.render(t, True, c), (box.x+20, box.y+20))
            self.screen.blit(self.font.render(d, True, WHITE), (box.x+20, box.y+70))
            self.screen.blit(self.font_ui.render("[PRESS SPACE]", True, GRAY), (box.x+130, box.y+110))
        elif game.popup_active:
            pr, pc = game.popup_coords
            px, py = self.world_to_screen(game, pr, pc)
            px = min(max(px, 10), w - 300) # Ensure inside map
            py = min(max(py, 10), h - 150)
            
            game.popup_rects = []
            bg = pygame.Rect(px+20, py, 140, 100)
            pygame.draw.rect(self.screen, BLACK, bg)
            pygame.draw.rect(self.screen, WHITE, bg, 2)
            
            b = game.buildings[game.grid[pr][pc]]
            
            urect = pygame.Rect(px+30, py+10, 120, 25)
            if b["upgrade_to"]:
                col = CYAN if game.money >= b["upgrade_cost"] else RED
                pygame.draw.rect(self.screen, DARK_GRAY, urect)
                pygame.draw.rect(self.screen, col, urect, 1)
                self.screen.blit(self.font.render(f"Upgrade {b['upgrade_cost']}", True, col), (px+35, py+12))
                game.popup_rects.append((urect, "UPGRADE"))
            
            srect = pygame.Rect(px+30, py+40, 120, 25)
            ref = int(game.get_building_total_cost(game.grid[pr][pc]) * 0.5)
            pygame.draw.rect(self.screen, DARK_GRAY, srect)
            pygame.draw.rect(self.screen, WHITE, srect, 1)
            self.screen.blit(self.font.render(f"Sell +{ref}", True, WHITE), (px+35, py+42))
            game.popup_rects.append((srect, "SELL"))
            
            crect = pygame.Rect(px+135, py-10, 20, 20)
            pygame.draw.rect(self.screen, RED, crect)
            self.screen.blit(self.font_bold.render("X", True, WHITE), (px+139, py-9))
            game.popup_rects.append((crect, "CLOSE"))

    def draw_sidebar(self, game):
        w, h = self.screen.get_size()
        sidebar_w = 280
        ui_x = w - sidebar_w + 20
        
        ui_bg = pygame.Rect(w - sidebar_w, 0, sidebar_w, h)
        pygame.draw.rect(self.screen, UI_BG, ui_bg)
        pygame.draw.rect(self.screen, GRAY, (ui_bg.x, 0, 2, h))
        
        self.screen.blit(self.font_title.render(f"Round {min(game.round, MAX_ROUNDS)}", True, WHITE), (ui_x, 30))
        
        h_icon = "😐"; h_col = YELLOW
        if game.happiness >= 80: h_icon="🙂"; h_col=GREEN
        if game.happiness <= 40: h_icon="🤬"; h_col=RED
        
        y = 80
        self.screen.blit(self.font_ui.render(f"💰 ${game.money}", True, GREEN), (ui_x, y)); y+=30
        self.screen.blit(self.font_ui.render(f"⚡ {game.energy}", True, YELLOW), (ui_x, y)); y+=30
        self.screen.blit(self.font_ui.render(f"👥 {game.population} / 💼 {game.jobs_total}", True, WHITE), (ui_x, y)); y+=30
        self.screen.blit(self.font_ui.render(f"{h_icon} {int(game.happiness)}%", True, h_col), (ui_x, y)); y+=30
        self.screen.blit(self.font_ui.render(f"⭐ {game.actions}/{game.max_actions}", True, ORANGE), (ui_x, y))

        y = 250
        tb_x = ui_x + 10
        self.screen.blit(self.font_bold.render("Construction:", True, WHITE), (ui_x, y-25))
        keys = [1, 2, 3, 4, 6, 9, 10, 7, 8] # Sorted IDs
        for i, b_id in enumerate(keys):
            rect = pygame.Rect(tb_x + (i%4)*60, y + (i//4)*60, 50, 50)
            is_sel = (game.selected_building == b_id)
            pygame.draw.rect(self.screen, tuple(game.buildings[b_id]["color"]) if is_sel else DARK_GRAY, rect)
            pygame.draw.rect(self.screen, WHITE if is_sel else GRAY, rect, 2)
            self.screen.blit(self.font_icon.render(game.buildings[b_id]["symbol"], True, BLACK), rect.inflate(-10,-10))

        # Dynamic Rects Update
        game.btn_pass = pygame.Rect(w - 200, h - 70, 150, 50)
        game.log_rect = pygame.Rect(20, h - 120, w - sidebar_w - 60, 100)
        game.btn_log_up = pygame.Rect(game.log_rect.right + 5, game.log_rect.y, 20, 50)
        game.btn_log_down = pygame.Rect(game.log_rect.right + 5, game.log_rect.y + 50, 20, 50)

        # Info Box
        info_rect = pygame.Rect(ui_x, 430, 240, 100)
        pygame.draw.rect(self.screen, (40, 40, 50), info_rect)
        pygame.draw.rect(self.screen, GRAY, info_rect, 1)
        
        mx, my = pygame.mouse.get_pos()
        preview_txt = []
        if mx < w - sidebar_w and not game.popup_queue:
            r, c = game.screen_to_world(mx, my)
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                if game.can_place_building(r, c, game.selected_building):
                    cst = game.get_cost(game.selected_building)
                    ap = game.buildings[game.selected_building].get("ap_cost", 0)
                    preview_txt.append((f"Cost: -${cst} | -{ap}⭐", WHITE))
                    for e in game.predict_building_effects(r, c, game.selected_building): 
                        preview_txt.append((e, GREEN if "Combo" in e else RED))
        
        if not preview_txt:
            b = game.buildings[game.selected_building]
            preview_txt.append((f"{b['name']} ${game.get_cost(game.selected_building)}", tuple(b["color"])))
            preview_txt.append((f"Pop: {b['pop']} | Jobs: {b['work']}", WHITE))
            preview_txt.append((f"Energy: {b['energy']:+} | Happy: {b['happy']:+}", YELLOW))
            if b["needs_road"]: preview_txt.append(("⚠ Needs Road Access", ORANGE))

        iy = info_rect.y + 5
        for t, c in preview_txt: 
            self.screen.blit(self.font.render(t, True, c), (info_rect.x+5, iy)); iy+=20

        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_pass)
        pygame.draw.rect(self.screen, WHITE, game.btn_pass, 2)
        self.screen.blit(self.font_bold.render("PASS TURN", True, WHITE), (game.btn_pass.x+35, game.btn_pass.y+15))

        pygame.draw.rect(self.screen, BLACK, game.log_rect)
        pygame.draw.rect(self.screen, GRAY, game.log_rect, 1)
        
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_log_up)
        self.screen.blit(self.font.render("▲",True,WHITE), (game.btn_log_up.x+5, game.btn_log_up.y+10))
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_log_down)
        self.screen.blit(self.font.render("▼",True,WHITE), (game.btn_log_down.x+5, game.btn_log_down.y+10))
        
        visible_logs = game.event_log.get_visible_logs()
        ly = game.log_rect.y + 5
        for t, c in visible_logs: 
            self.screen.blit(self.font.render(f"> {t}", True, c), (game.log_rect.x+5, ly)); ly+=18

    def draw_gameover(self, game):
        w, h = self.screen.get_size()
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0,0))
        
        msg = "VICTORY!" if game.win else "BANKRUPT!"
        col = GREEN if game.win else RED
        
        title_surf = self.font_title.render(msg, True, col)
        self.screen.blit(title_surf, (w//2 - title_surf.get_width()//2, h//2 - 80))
        
        info = f"Score: {game.money + game.population*10}"
        info_surf = self.font_ui.render(info, True, WHITE)
        self.screen.blit(info_surf, (w//2 - info_surf.get_width()//2, h//2 - 20))
        
        game.btn_restart = pygame.Rect(w//2 - 100, h//2 + 40, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_restart)
        pygame.draw.rect(self.screen, WHITE, game.btn_restart, 2)
        self.screen.blit(self.font_menu.render("PLAY AGAIN", True, WHITE), (game.btn_restart.x + 35, game.btn_restart.y + 10))
        
        game.btn_menu = pygame.Rect(w//2 - 100, h//2 + 110, 200, 50)
        pygame.draw.rect(self.screen, DARK_GRAY, game.btn_menu)
        pygame.draw.rect(self.screen, WHITE, game.btn_menu, 2)
        self.screen.blit(self.font_menu.render("MAIN MENU", True, WHITE), (game.btn_menu.x + 35, game.btn_menu.y + 10))