import pygame
import sys

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 10
TILE_SIZE = 40
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50
MAX_ROUNDS = 20

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)  # House
BLUE = (50, 50, 200)  # Office
YELLOW = (200, 200, 50)  # Power Plant
DARK_GRAY = (50, 50, 50)

# Building Definitions
# ID 0 is empty
BUILDINGS = {
    1: {"name": "House", "color": GREEN, "cost": 50, "energy": -2, "money": 10, "pop": 5},
    2: {"name": "Office", "color": BLUE, "cost": 100, "energy": -5, "money": 30, "pop": 0},
    3: {"name": "Power Plant", "color": YELLOW, "cost": 150, "energy": 15, "money": -10, "pop": 0}
}


class GameState:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.money = 200
        self.energy = 10
        self.population = 0
        self.round = 1
        self.game_over = False
        self.win = False
        self.message = "Welcome! Keys: 1=House, 2=Office, 3=Power. SPACE=Next Turn."

        # Current selected building type (1, 2, or 3)
        self.selected_building = 1

    def place_building(self, r, c):
        if self.game_over: return

        # Check if tile is empty
        if self.grid[r][c] != 0:
            self.message = "Tile occupied!"
            return

        building = BUILDINGS[self.selected_building]

        # Check affordability
        if self.money >= building["cost"]:
            self.money -= building["cost"]
            self.grid[r][c] = self.selected_building
            self.message = f"Built {building['name']}."
            self.recalc_stats()  # Update instant stats like Pop
        else:
            self.message = "Not enough money!"

    def recalc_stats(self):
        """Recalculate static stats (like total population) based on grid."""
        total_pop = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    total_pop += BUILDINGS[b_id]["pop"]
        self.population = total_pop

    def next_turn(self):
        if self.game_over: return

        # 1. Calculate Production / Consumption
        money_change = 0
        energy_change = 0

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                b_id = self.grid[r][c]
                if b_id in BUILDINGS:
                    b_data = BUILDINGS[b_id]
                    money_change += b_data["money"]
                    energy_change += b_data["energy"]

        # 2. Apply Changes
        self.money += money_change

        # Energy is usually a capacity check, but for this simple version
        # we can treat it as a resource or a status.
        # Let's treat it as "Available Energy":
        # Reset energy to base, then apply +/- from buildings (Capacity style)
        # OR Accumulate it (Battery style).
        # Let's go with the Prompt's style: Sum of productions.
        # If Sum < 0, penalty.
        self.energy = 10 + energy_change  # Base 10 + grid effects

        # 3. Penalties
        if self.energy < 0:
            penalty = 50
            self.money -= penalty
            self.message = f"Round {self.round} ended. Low Energy! -${penalty} penalty."
        else:
            self.message = f"Round {self.round} complete. Money: {money_change:+}"

        # 4. Check Win/Loss
        if self.money < 0:
            self.game_over = True
            self.message = "GAME OVER: Bankruptcy!"
        elif self.round >= MAX_ROUNDS:
            self.game_over = True
            self.win = True
            self.message = "VICTORY: City Survived 20 Rounds!"
        else:
            self.round += 1


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cyber City Roguelike v0.1")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)
    title_font = pygame.font.SysFont("Arial", 24, bold=True)

    game = GameState()

    while True:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: game.selected_building = 1
                if event.key == pygame.K_2: game.selected_building = 2
                if event.key == pygame.K_3: game.selected_building = 3
                if event.key == pygame.K_SPACE: game.next_turn()

                # Restart Key
                if event.key == pygame.K_r and game.game_over:
                    game = GameState()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Convert mouse to grid coordinates
                gx = (mx - GRID_OFFSET_X) // TILE_SIZE
                gy = (my - GRID_OFFSET_Y) // TILE_SIZE

                if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                    game.place_building(gy, gx)  # Row is Y, Col is X

        # --- Drawing ---
        screen.fill(DARK_GRAY)

        # 1. Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(
                    GRID_OFFSET_X + c * TILE_SIZE,
                    GRID_OFFSET_Y + r * TILE_SIZE,
                    TILE_SIZE - 2, TILE_SIZE - 2
                )

                b_id = game.grid[r][c]
                color = GRAY  # Default empty
                if b_id in BUILDINGS:
                    color = BUILDINGS[b_id]["color"]

                pygame.draw.rect(screen, color, rect)

        # 2. Draw UI / HUD
        ui_x = 500
        y_offset = 50

        # Title
        title_surf = title_font.render(f"Round: {game.round} / {MAX_ROUNDS}", True, WHITE)
        screen.blit(title_surf, (ui_x, y_offset))
        y_offset += 40

        # Stats
        stats = [
            f"Money: ${game.money}",
            f"Energy: {game.energy}",
            f"Population: {game.population}",
        ]

        for stat in stats:
            surf = font.render(stat, True, WHITE)
            screen.blit(surf, (ui_x, y_offset))
            y_offset += 30

        y_offset += 20
        # Building Selection
        sel_msg = font.render("Select Building (Keys 1-3):", True, WHITE)
        screen.blit(sel_msg, (ui_x, y_offset))
        y_offset += 30

        for b_id, b_data in BUILDINGS.items():
            prefix = "> " if game.selected_building == b_id else "  "
            txt = f"{prefix}{b_id}. {b_data['name']} (${b_data['cost']})"
            col = b_data['color']
            surf = font.render(txt, True, col)
            screen.blit(surf, (ui_x, y_offset))
            y_offset += 25

        # Controls info
        y_offset += 40
        controls = "SPACE: End Turn"
        if game.game_over:
            controls = "R: Restart Game"

        ctrl_surf = font.render(controls, True, WHITE)
        screen.blit(ctrl_surf, (ui_x, y_offset))

        # Message Log
        msg_surf = font.render(game.message, True, (255, 200, 200))
        screen.blit(msg_surf, (50, 500))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()