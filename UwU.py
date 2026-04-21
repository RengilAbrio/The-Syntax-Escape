import os
import pygame
from pygame.locals import *


# =============================================================================
# CONSTANTS
# =============================================================================

# --- Screen ---
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 1000
FPS           = 60
TITLE         = "THE-SYNTAX-ESCAPE"

# --- World ---
TILE_SIZE = 40

# --- Game States ---
MENU    = 0
PLAYING = 1
QUIZ    = 2
WIN     = 3

# --- Tile IDs ---
TILE_BLOCK = 1
TILE_GRASS = 2
TILE_ROCK  = 3
TILE_ENEMY = 4
TILE_GATE  = 5

# --- Colours ---
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   255, 0)
DARK   = (20,  20,  20)


# =============================================================================
# WORLD DATA
# =============================================================================

# fmt: off
WORLD_DATA = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # rows 0-18 are empty
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2],  # row 19 – gate at col 24
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,2,2,2,2,2,2,2],  # row 20 – enemies
    [2,2,2,2,0,0,0,0,3,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1],  # row 21
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # row 22
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # row 23
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # row 24
]
# fmt: on

# Pre-compute enemy spawn positions so resets don't re-scan the grid each time.
SLIME_SPAWN_POSITIONS = [
    (col * TILE_SIZE, row * TILE_SIZE)
    for row, tiles in enumerate(WORLD_DATA)
    for col, tile in enumerate(tiles)
    if tile == TILE_ENEMY
]


# =============================================================================
# HELPERS
# =============================================================================

def load_scaled_image(path: str, size: tuple) -> pygame.Surface:
    """Load an image and scale it to *size* in one call."""
    return pygame.transform.scale(
        pygame.image.load(path).convert_alpha(), size
    )


# =============================================================================
# GATE  (Win Condition)
# =============================================================================

class Gate(pygame.sprite.Sprite):
    """Exit gate — static when closed, plays open animation once when triggered."""

    FRAME_COLS   = 4
    ANIM_SPEED   = 0.08     # speed of the opening animation
    DISPLAY_SIZE = (80, 80)

    def __init__(self, x: int, y: int):
        super().__init__()
        self.frames      = self._load_frames()
        self.frame_index = 0.0
        self.image       = self.frames[0]   # start closed
        self.rect        = self.image.get_rect(bottomleft=(x, y + TILE_SIZE))
        self.hitbox      = self.rect.inflate(-20, -10)
        self.is_opening  = False  # triggered by player contact
        self.is_open     = False  # True once animation finishes → win

    # ------------------------------------------------------------------
    def _load_frames(self) -> list[pygame.Surface]:
        sheet   = pygame.image.load("GRAPHICS/OTHERS/GATE.png").convert_alpha()
        frame_w = sheet.get_width() // self.FRAME_COLS
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                self.DISPLAY_SIZE,
            )
            for i in range(self.FRAME_COLS)
        ]

    # ------------------------------------------------------------------
    def trigger(self) -> None:
        """Call this when the player touches the gate to start opening it."""
        if not self.is_opening and not self.is_open:
            self.is_opening = True

    # ------------------------------------------------------------------
    def update(self) -> None:
        """Only advances frames while the gate is opening."""
        if not self.is_opening:
            return  # stay on frame 0 (closed)

        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.frame_index = len(self.frames) - 1  # hold on last frame
            self.is_opening  = False
            self.is_open     = True                   # animation done → trigger win

        self.image = self.frames[int(self.frame_index)]

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


# =============================================================================
# BACKGROUND MANAGER
# =============================================================================

class BackgroundManager:
    """Handles parallax scrolling and day/night cycling."""

    SWITCH_INTERVAL = 10_000  # milliseconds between day ↔ night transitions
    LAYER_SPEEDS    = [0.1, 0.2, 0.3, 0.4, 0.5]

    def __init__(self):
        self.day_images   = []
        self.night_images = []

        for i in range(1, 6):
            try:
                self.day_images.append(
                    load_scaled_image(
                        f"GRAPHICS/BACKGROUND/1/Day/{i}.png",
                        (SCREEN_WIDTH, SCREEN_HEIGHT),
                    )
                )
                self.night_images.append(
                    load_scaled_image(
                        f"GRAPHICS/BACKGROUND/1/Night/{i}.png",
                        (SCREEN_WIDTH, SCREEN_HEIGHT),
                    )
                )
            except FileNotFoundError:
                pass  # Fewer than 5 layers is fine

        self.is_day         = True
        self.last_switch    = pygame.time.get_ticks()
        self.scroll         = 0

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all parallax layers and advance the scroll offset."""
        now = pygame.time.get_ticks()
        if now - self.last_switch > self.SWITCH_INTERVAL:
            self.is_day      = not self.is_day
            self.last_switch = now

        layers = self.day_images if self.is_day else self.night_images
        self.scroll += 2

        for img, speed in zip(layers, self.LAYER_SPEEDS):
            x_offset = (self.scroll * speed) % SCREEN_WIDTH
            screen.blit(img, (-x_offset, 0))
            screen.blit(img, (SCREEN_WIDTH - x_offset, 0))


# =============================================================================
# PLAYER
# =============================================================================

class Player(pygame.sprite.Sprite):
    """Player character with animation, physics, and enemy-collision logic."""

    ANIMATION_SPEED   = 0.10
    MOVE_SPEED        = 5
    JUMP_FORCE        = -15
    GRAVITY           = 1
    MAX_FALL_SPEED    = 10
    IDLE_WAIT_MS      = 5_000   # how long before the idle animation plays
    DEATH_DELAY_MS    = 1_000   # visual delay before game-over triggers
    RESPAWN_GRACE_MS  = 1_000   # invincibility window after respawn

    def __init__(self, x: int, y: int):
        super().__init__()

        self.animations   = {"IDLE": [], "RUN": [], "JUMP": []}
        self.status       = "STAND"
        self.frame_index  = 0.0
        self.facing_right = True

        self._load_animations()

        # Initial image – fall back to blank surface if assets are missing.
        self.image = self.animations["IDLE"][0] if self.animations["IDLE"] else pygame.Surface((64, 64))
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -10)

        # Physics
        self.vel_y     = 0
        self.jumped    = False
        self.on_ground = False

        # State flags
        self.is_dying         = False
        self.death_time       = 0
        self.respawn_time     = 0
        self.last_action_time = pygame.time.get_ticks()
        self.is_playing_idle  = False

    # ------------------------------------------------------------------
    def _load_animations(self) -> None:
        base = "GRAPHICS/PLAYER/"
        for name in self.animations:
            folder = os.path.join(base, name)
            try:
                for filename in sorted(os.listdir(folder)):
                    if filename.lower().endswith(".png"):
                        img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                        self.animations[name].append(
                            pygame.transform.scale(img, (64, 64))
                        )
            except FileNotFoundError:
                print(f"[Player] Animation folder not found: {folder}")

    # ------------------------------------------------------------------
    def _animate(self) -> None:
        """Advance the current animation and update self.image."""
        if self.status == "STAND":
            if self.animations["IDLE"]:
                self.image = self.animations["IDLE"][0]
            return

        frames = self.animations.get(self.status, [])
        if not frames:
            self.image = pygame.Surface((64, 64))
            return

        self.frame_index += self.ANIMATION_SPEED
        if self.frame_index >= len(frames):
            if self.status == "IDLE":
                self.is_playing_idle = False
                self.status          = "STAND"
                self.frame_index     = 0.0
                self.last_action_time = pygame.time.get_ticks()
            else:
                self.frame_index = 0.0

        self.image = frames[int(self.frame_index)]

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ------------------------------------------------------------------
    def _get_input(self) -> tuple[int, int, bool]:
        """Read keyboard state; return (dx, dy, action_taken)."""
        dx, dy       = 0, 0
        action_taken = False
        keys         = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.on_ground and not self.jumped:
            self.vel_y   = self.JUMP_FORCE
            self.jumped  = True
            self.status  = "JUMP"
            action_taken = True

        if not keys[pygame.K_SPACE]:
            self.jumped = False

        if keys[pygame.K_LEFT]:
            dx            -= self.MOVE_SPEED
            self.facing_right = False
            self.status       = "RUN"
            action_taken      = True

        if keys[pygame.K_RIGHT]:
            dx           += self.MOVE_SPEED
            self.facing_right = True
            self.status       = "RUN"
            action_taken      = True

        return dx, dy, action_taken

    # ------------------------------------------------------------------
    def _apply_physics(self, dx: int, dy: int, world) -> tuple[int, int]:
        """Apply gravity and tile collisions; return adjusted (dx, dy)."""
        self.vel_y = min(self.vel_y + self.GRAVITY, self.MAX_FALL_SPEED)
        dy += self.vel_y
        self.on_ground = False

        for _, tile_rect in world.tile_list:
            # Horizontal
            if tile_rect.colliderect(self.rect.x + dx, self.rect.y, 63, 63):
                dx = 0
            # Vertical
            if tile_rect.colliderect(self.rect.x, self.rect.y + dy, 63, 63):
                if self.vel_y < 0:  # hit ceiling
                    self.rect.top = tile_rect.bottom
                    self.vel_y    = 0
                else:               # land on ground
                    self.rect.bottom = tile_rect.top
                    self.vel_y       = 0
                    self.on_ground   = True
                    self.jumped      = False
                    self.status      = "RUN" if abs(dx) > 0 else "STAND"
                dy = 0

        return dx, dy

    # ------------------------------------------------------------------
    def update(self, world, game_over: int, slime_group) -> int:
        """Update player each frame.  Returns -1 on death, else game_over."""
        if game_over != 0:
            self._animate()
            return game_over

        # --- Death animation delay ---
        if self.is_dying:
            if pygame.time.get_ticks() - self.death_time > self.DEATH_DELAY_MS:
                return -1
            self._animate()
            return game_over

        # --- Normal update ---
        dx, dy, action_taken = self._get_input()
        now           = pygame.time.get_ticks()
        in_grace      = (now - self.respawn_time) < self.RESPAWN_GRACE_MS

        # Idle animation trigger
        if not action_taken and self.on_ground:
            if self.is_playing_idle:
                self.status = "IDLE"
            elif now - self.last_action_time > self.IDLE_WAIT_MS:
                self.is_playing_idle = True
                self.frame_index     = 0.0
                self.status          = "IDLE"
        else:
            self.last_action_time = now
            self.is_playing_idle  = False

        dx, dy = self._apply_physics(dx, dy, world)

        self.rect.x    += dx
        self.rect.y    += dy
        self.hitbox.center = self.rect.center

        # Enemy collision (skip during grace period)
        if not in_grace:
            for slime in slime_group:
                if self.hitbox.colliderect(slime.hitbox):
                    self.is_dying  = True
                    self.death_time = pygame.time.get_ticks()
                    break

        self._animate()
        return game_over

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y + 10))


# =============================================================================
# WORLD
# =============================================================================

class World:
    """Builds the tile map and spawns enemies from a 2-D data array."""

    TILE_IMAGES = {
        TILE_BLOCK: "GRAPHICS/TILES/Tile_02.png",
        TILE_GRASS: "GRAPHICS/TILES/Tile_01.png",
        TILE_ROCK:  "GRAPHICS/TILES/Tile_03.png",
    }

    def __init__(self, data: list[list[int]], difficulty: int, slime_group: pygame.sprite.Group):
        self.tile_list  = []
        self.gate_group = pygame.sprite.Group()
        self.difficulty = difficulty

        # Cache scaled tile images
        tile_surfaces = {
            tid: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for tid, path in self.TILE_IMAGES.items()
        }

        for row_idx, row in enumerate(data):
            for col_idx, tile_id in enumerate(row):
                if tile_id in tile_surfaces:
                    img      = tile_surfaces[tile_id]
                    img_rect = img.get_rect(
                        topleft=(col_idx * TILE_SIZE, row_idx * TILE_SIZE)
                    )
                    self.tile_list.append((img, img_rect))

                elif tile_id == TILE_ENEMY:
                    x = col_idx * TILE_SIZE
                    y = row_idx * TILE_SIZE
                    for _ in range(difficulty):
                        slime_group.add(Enemy(x, y))

                elif tile_id == TILE_GATE:
                    x = col_idx * TILE_SIZE
                    y = row_idx * TILE_SIZE
                    self.gate_group.add(Gate(x, y))

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        for img, rect in self.tile_list:
            screen.blit(img, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
        for gate in self.gate_group:
            gate.draw(screen)


# =============================================================================
# ENEMY  (Slime)
# =============================================================================

class Enemy(pygame.sprite.Sprite):
    """Patrolling slime enemy with idle / walk animation states."""

    MOVE_SPEED     = 1.5
    PATROL_WIDTH   = 100
    ANIM_SPEED     = 0.15
    GRAVITY        = 1
    MAX_FALL_SPEED = 10
    WALK_DURATION  = 5 * FPS   # frames
    IDLE_DURATION  = 3 * FPS
    SCALE_FACTOR   = 1.5
    VISUAL_OFFSET_Y = 35

    def __init__(self, x: int, y: int):
        super().__init__()

        self.idle_frames = self._load_sheet("GRAPHICS/Enemies/Slime1.png", cols=6, row=2)
        self.walk_frames = self._load_sheet("GRAPHICS/Enemies/Slime2.png", cols=8, row=2)

        # Movement / state
        self.state     = "WALKING"
        self.direction = 1          # 1 = right, -1 = left
        self.pos_x     = float(x)
        self.center_x  = float(x)
        self.vel_y     = 0
        self.timer     = 0

        self.state_durations = {
            "WALKING": self.WALK_DURATION,
            "IDLE":    self.IDLE_DURATION,
        }

        # Animation
        self.current_frame = 0.0

        # Rects
        self.image  = self.walk_frames[0]
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -20)

    # ------------------------------------------------------------------
    def _load_sheet(self, path: str, cols: int, row: int) -> list[pygame.Surface]:
        """Slice a sprite sheet and return a list of scaled frames."""
        sheet        = pygame.image.load(path).convert_alpha()
        frame_w      = sheet.get_width()  // cols
        frame_h      = sheet.get_height() // 4
        new_w        = int(frame_w * self.SCALE_FACTOR)
        new_h        = int(frame_h * self.SCALE_FACTOR)

        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, row * frame_h, frame_w, frame_h)),
                (new_w, new_h),
            )
            for i in range(cols)
        ]

    # ------------------------------------------------------------------
    def update(self, world) -> None:
        # Gravity + tile collision
        self.vel_y = min(self.vel_y + self.GRAVITY, self.MAX_FALL_SPEED)
        self.rect.y += self.vel_y

        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile_rect.top
                elif self.vel_y < 0:
                    self.rect.top = tile_rect.bottom
                self.vel_y = 0

        # State timer
        self.timer += 1
        if self.timer >= self.state_durations[self.state]:
            self.timer = 0
            self.state = "IDLE" if self.state == "WALKING" else "WALKING"

        # Patrol movement
        if self.state == "WALKING":
            self.pos_x += self.MOVE_SPEED * self.direction
            left  = self.center_x - self.PATROL_WIDTH / 2
            right = self.center_x + self.PATROL_WIDTH / 2

            if self.pos_x >= right:
                self.pos_x = right
                self.direction = -1
            elif self.pos_x <= left:
                self.pos_x = left
                self.direction = 1

        self.rect.x        = int(self.pos_x)
        # Offset hitbox downward to match the visual draw position (drawn at rect.y + VISUAL_OFFSET_Y)
        self.hitbox.center = (self.rect.centerx + 30, self.rect.centery + self.VISUAL_OFFSET_Y + 30)

        # Animation
        frames = self.walk_frames if self.state == "WALKING" else self.idle_frames
        self.current_frame = (self.current_frame + self.ANIM_SPEED) % len(frames)

        raw = frames[int(self.current_frame)]
        # Flip so the slime faces its movement direction
        self.image = pygame.transform.flip(raw, True, False) if self.direction == 1 else raw

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y + self.VISUAL_OFFSET_Y))


# =============================================================================
# MENU
# =============================================================================

class Menu:
    """Language & level selection screen."""

    LANGUAGES   = ["Python", "Java", "JavaScript", "HTML", "CSS"]
    BTN_X       = 100
    BTN_Y_START = 150
    BTN_STEP    = 60
    BTN_W, BTN_H = 200, 50

    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 30)

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(DARK)
        title = self.font.render("SELECT LANGUAGE & LEVEL", True, WHITE)
        screen.blit(title, (300, 50))

        for i, lang in enumerate(self.LANGUAGES):
            rect = self._button_rect(i)
            pygame.draw.rect(screen, GREEN, rect, 2)
            screen.blit(self.font.render(lang, True, WHITE), (rect.x + 10, rect.y + 10))

    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Return the selected language name, or None if no button was hit."""
        for i, lang in enumerate(self.LANGUAGES):
            if self._button_rect(i).collidepoint(pos):
                return lang
        return None

    # ------------------------------------------------------------------
    def _button_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(
            self.BTN_X,
            self.BTN_Y_START + index * self.BTN_STEP,
            self.BTN_W,
            self.BTN_H,
        )


# =============================================================================
# GAME HELPERS
# =============================================================================

def spawn_slimes(slime_group: pygame.sprite.Group) -> None:
    """Clear and repopulate the slime group from the fixed spawn positions."""
    slime_group.empty()
    for x, y in SLIME_SPAWN_POSITIONS:
        slime_group.add(Enemy(x, y))


def reset_game(player: Player, slime_group: pygame.sprite.Group) -> None:
    """Reset player position and re-spawn all enemies."""
    player.rect.x      = -5
    player.rect.y      = SCREEN_HEIGHT - 350
    player.respawn_time = pygame.time.get_ticks()
    player.is_dying    = False
    spawn_slimes(slime_group)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # --- Core objects ---
    bg_manager  = BackgroundManager()
    menu        = Menu()
    player      = Player(-5, SCREEN_HEIGHT - 350)
    slime_group = pygame.sprite.Group()
    world       = None          # Created after language selection
    game_over   = 0
    game_state  = MENU
    selected_language = None
    selected_level    = 1

    game_over_font = pygame.font.SysFont("Arial", 40)
    win_font       = pygame.font.SysFont("Arial", 60)

    running = True
    while running:
        clock.tick(FPS)

        # -----------------------------------------------------------------
        # EVENT HANDLING
        # -----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
                chosen = menu.handle_click(pygame.mouse.get_pos())
                if chosen:
                    selected_language = chosen
                    slime_group.empty()
                    world = World(WORLD_DATA, selected_level, slime_group)
                    game_state = PLAYING
                    print(f"Started {selected_language} – Level {selected_level}")

            elif game_state == PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over != 0:
                    game_over = 0
                    reset_game(player, slime_group)

            elif game_state == WIN and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_over  = 0
                    game_state = MENU
                    reset_game(player, slime_group)

        # -----------------------------------------------------------------
        # UPDATE
        # -----------------------------------------------------------------
        if game_state == PLAYING and game_over == 0:
            game_over = player.update(world, game_over, slime_group)
            if not player.is_dying:
                slime_group.update(world)
            # Update gate animation; trigger on player contact, win when fully open
            world.gate_group.update()
            for gate in world.gate_group:
                if player.hitbox.colliderect(gate.hitbox):
                    gate.trigger()
                if gate.is_open:
                    game_state = WIN

        # -----------------------------------------------------------------
        # DRAW
        # -----------------------------------------------------------------
        screen.fill(BLACK)

        if game_state == MENU:
            menu.draw(screen)

        elif game_state == PLAYING:
            bg_manager.draw(screen)
            world.draw(screen)

            for enemy in slime_group:
                enemy.draw(screen)

            player.draw(screen)

            if game_over == -1:
                msg = game_over_font.render("GAME OVER — Press R to Restart", True, WHITE)
                screen.blit(msg, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2))

        elif game_state == WIN:
            bg_manager.draw(screen)
            world.draw(screen)
            player.draw(screen)
            # Overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            win_msg  = win_font.render("YOU ESCAPED!", True, (255, 215, 0))
            sub_msg  = game_over_font.render("Press R to Play Again", True, WHITE)
            screen.blit(win_msg, (SCREEN_WIDTH // 2 - win_msg.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(sub_msg, (SCREEN_WIDTH // 2 - sub_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()