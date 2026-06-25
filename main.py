import pygame
import random
import asyncio
import os

pygame.init()

# ==========================================
# SETTINGS
# ==========================================

WIDTH = 800
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying Piggy Bank")

clock = pygame.time.Clock()

# ==========================================
# LOAD ASSETS
# ==========================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Desktop:
# main.py
# assets/background.png
#
# Pygbag:
# assets/main.py
# assets/assets/background.png

POSSIBLE_ASSET_DIRS = [
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, "assets", "assets"),
    BASE_DIR
]

ASSET_DIR = None

for folder in POSSIBLE_ASSET_DIRS:

    if os.path.exists(
        os.path.join(folder, "background.png")
    ):
        ASSET_DIR = folder
        break

if ASSET_DIR is None:
    raise FileNotFoundError(
        "Asset folder not found."
    )

print("ASSET_DIR =", ASSET_DIR)

background = pygame.image.load(
    os.path.join(ASSET_DIR, "background.png")
).convert()

background = pygame.transform.scale(
    background,
    (WIDTH, HEIGHT)
)

pig_img = pygame.image.load(
    os.path.join(ASSET_DIR, "piggybank.png")
).convert_alpha()

coin_img = pygame.image.load(
    os.path.join(ASSET_DIR, "coin.png")
).convert_alpha()

building_top_img = pygame.image.load(
    os.path.join(ASSET_DIR, "building_top.png")
).convert_alpha()

building_bottom_img = pygame.image.load(
    os.path.join(ASSET_DIR, "building_bottom.png")
).convert_alpha()

gameover_img = pygame.image.load(
    os.path.join(ASSET_DIR, "gameover.png")
).convert_alpha()
# ==========================================
# GAME SETTINGS
# ==========================================

GRAVITY = 0.5
JUMP_POWER = -9

BUILDING_SPEED = 4
BUILDING_GAP = 200

FONT = pygame.font.SysFont("arial", 32)
BIG_FONT = pygame.font.SysFont("arial", 50)

# ==========================================
# PLAYER
# ==========================================

class PiggyBank:

    def __init__(self):

        self.image = pygame.transform.scale(
            pig_img,
            (80, 80)
        )

        self.rect = self.image.get_rect(
            center=(150, HEIGHT // 2)
        )

        self.velocity = 0

    def jump(self):
        self.velocity = JUMP_POWER

    def update(self):

        self.velocity += GRAVITY
        self.rect.y += self.velocity

    def draw(self):

        screen.blit(self.image, self.rect)

# ==========================================
# BUILDING
# ==========================================

class Building:

    WIDTH = 100

    def __init__(self):

        self.x = WIDTH

        self.gap_y = random.randint(170, 430)

        self.top_height = self.gap_y - BUILDING_GAP // 2
        self.bottom_y = self.gap_y + BUILDING_GAP // 2

        self.passed = False

        self.top_img = pygame.transform.scale(
            building_top_img,
            (self.WIDTH, self.top_height)
        )

        self.bottom_img = pygame.transform.scale(
            building_bottom_img,
            (self.WIDTH, HEIGHT - self.bottom_y)
        )

        self.top_rect = pygame.Rect(
            self.x,
            0,
            self.WIDTH,
            self.top_height
        )

        self.bottom_rect = pygame.Rect(
            self.x,
            self.bottom_y,
            self.WIDTH,
            HEIGHT - self.bottom_y
        )

    def update(self):

        self.x -= BUILDING_SPEED

        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self):

        screen.blit(self.top_img, (self.x, 0))
        screen.blit(self.bottom_img, (self.x, self.bottom_y))

    def offscreen(self):

        return self.x < -self.WIDTH

# ==========================================
# COIN
# ==========================================

class Coin:

    def __init__(self, x, gap_y):

        self.image = pygame.transform.scale(
            coin_img,
            (40, 40)
        )

        self.rect = self.image.get_rect()

        self.rect.x = x + 30
        self.rect.y = gap_y - 20

        self.collected = False

    def update(self):

        self.rect.x -= BUILDING_SPEED

    def draw(self):

        if not self.collected:
            screen.blit(self.image, self.rect)

# ==========================================
# GAME
# ==========================================

class Game:

    def __init__(self):

        self.highscore = 0
        self.reset()

    def reset(self):

        self.player = PiggyBank()

        self.buildings = []
        self.coins = []

        self.score = 0

        self.spawn_timer = 0

        self.game_over = False

    def spawn_building(self):

        building = Building()

        self.buildings.append(building)

        self.coins.append(
            Coin(building.x, building.gap_y)
        )

    def update(self):

        if self.game_over:
            return

        self.player.update()

        self.spawn_timer += 1

        if self.spawn_timer >= 90:

            self.spawn_building()
            self.spawn_timer = 0

        for building in self.buildings:
            building.update()

        self.buildings = [
            b for b in self.buildings
            if not b.offscreen()
        ]

        for coin in self.coins:
            coin.update()

        self.coins = [
            c for c in self.coins
            if c.rect.right > 0
        ]

        self.check_collisions()

    def check_collisions(self):

        if self.player.rect.top < 0:
            self.end_game()

        if self.player.rect.bottom > HEIGHT:
            self.end_game()

        for building in self.buildings:

            if self.player.rect.colliderect(building.top_rect):
                self.end_game()

            if self.player.rect.colliderect(building.bottom_rect):
                self.end_game()

            if (
                not building.passed
                and building.x + building.WIDTH < self.player.rect.x
            ):
                building.passed = True
                self.score += 1

        for coin in self.coins:

            if (
                not coin.collected
                and self.player.rect.colliderect(coin.rect)
            ):
                coin.collected = True
                self.score += 5

    def end_game(self):

        self.game_over = True

        if self.score > self.highscore:
            self.highscore = self.score

    def draw(self):

        screen.blit(background, (0, 0))

        for building in self.buildings:
            building.draw()

        for coin in self.coins:
            coin.draw()

        self.player.draw()

        score_text = FONT.render(
            f"Score : {self.score}",
            True,
            (0, 0, 0)
        )

        best_text = FONT.render(
            f"Best : {self.highscore}",
            True,
            (0, 0, 0)
        )

        screen.blit(score_text, (20, 20))
        screen.blit(best_text, (20, 60))

        if self.game_over:

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((255, 255, 255))

            screen.blit(overlay, (0, 0))

            title = BIG_FONT.render(
                "GAME OVER",
                True,
                (200, 0, 0)
            )

            screen.blit(
                title,
                (
                    WIDTH//2 - title.get_width()//2,
                    180
                )
            )

            final_text = FONT.render(
                f"Final Score : {self.score}",
                True,
                (0, 0, 0)
            )

            restart_text = FONT.render(
                "Press R or Click",
                True,
                (0, 0, 0)
            )

            screen.blit(
                final_text,
                (
                    WIDTH//2 - final_text.get_width()//2,
                    280
                )
            )

            screen.blit(
                restart_text,
                (
                    WIDTH//2 - restart_text.get_width()//2,
                    340
                )
            )

# ==========================================
# MAIN LOOP
# ==========================================

async def main():

    game = Game()

    running = True

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE:

                    if not game.game_over:
                        game.player.jump()

                if event.key == pygame.K_r:

                    if game.game_over:
                        game.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if game.game_over:
                    game.reset()
                else:
                    game.player.jump()

        game.update()
        game.draw()

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())