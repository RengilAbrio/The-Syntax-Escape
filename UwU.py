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
        """Apply gravity and tile collisions; return adjusted (dx, dy).
        Never modifies self.rect directly — the caller applies the final dx/dy.
        """
        self.vel_y = min(self.vel_y + self.GRAVITY, self.MAX_FALL_SPEED)
        dy += self.vel_y
        self.on_ground = False

        for _, tile_rect in world.tile_list:
            # --- Horizontal collision ---
            if tile_rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0

            # --- Vertical collision ---
            if tile_rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:  # hit ceiling — push down to tile bottom
                    dy         = tile_rect.bottom - self.rect.top
                    self.vel_y = 0
                else:               # hit floor — push up to tile top
                    dy             = tile_rect.top - self.rect.bottom
                    self.vel_y     = 0
                    self.on_ground = True
                    self.jumped    = False
                    self.status    = "RUN" if abs(dx) > 0 else "STAND"

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
        self.hitbox = self.rect.inflate(-60, -60)

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
        
        self.rect.x = int(self.pos_x)
        self.hitbox.center = self.rect.center

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

        self.rect.x = int(self.pos_x)
        # Offset hitbox downward to match the visual draw position (drawn at rect.y + VISUAL_OFFSET_Y)
        self.hitbox.center = (self.rect.centerx , self.rect.centery + self.VISUAL_OFFSET_Y)

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
# PIXEL FONT
# =============================================================================

class PixelFont:
    """Renders text using individual letter images from GRAPHICS/UI/LETTERS/."""

    # Map each character to its filename index (1_XX.png)
    CHAR_MAP = {
        'A':'1_01','B':'1_02','C':'1_03','D':'1_04','E':'1_05','F':'1_06',
        'G':'1_07','H':'1_08','I':'1_09','J':'1_10','K':'1_11','L':'1_12',
        'M':'1_13','N':'1_14','O':'1_15','P':'1_16','Q':'1_17','R':'1_18',
        'S':'1_19','T':'1_20','U':'1_21','V':'1_22','W':'1_23','X':'1_24',
        'Y':'1_25','Z':'1_26',
        '0':'1_27','1':'1_28','2':'1_29','3':'1_30','4':'1_31','5':'1_32',
        '6':'1_33','7':'1_34','8':'1_35','9':'1_36',
        '.':'1_37',':':'1_38',',':'1_39','+':'1_40','-':'1_41','=':'1_42',
        ';':'1_43',"'":'1_44','#':'1_45','|':'1_46','\\':'1_47','/':'1_48',
        '(':'1_49',')':'1_50','[':'1_51',']':'1_52','{':'1_53','}':'1_54',
        '!':'1_55','<':'1_56','>':'1_57','?':'1_58','%':'1_60',
    }
    LETTER_DIR = "GRAPHICS/UI/LETTERS/"

    def __init__(self, glyph_size: int = 24, spacing: int = 2):
        self.glyph_size = glyph_size
        self.spacing    = spacing
        self._cache: dict[str, pygame.Surface] = {}

    # ------------------------------------------------------------------
    def _get_glyph(self, char: str) -> pygame.Surface | None:
        """Return a scaled glyph surface, loading and caching on first use."""
        char = char.upper()
        if char not in self.CHAR_MAP:
            return None
        if char not in self._cache:
            path = self.LETTER_DIR + self.CHAR_MAP[char] + ".png"
            try:
                img = pygame.image.load(path).convert()
                img.set_colorkey((255, 255, 255))
                self._cache[char] = pygame.transform.scale(
                    img, (self.glyph_size, self.glyph_size)
                )
            except FileNotFoundError:
                return None
        return self._cache[char]

    # ------------------------------------------------------------------
    def render(self, text: str, screen: pygame.Surface, x: int, y: int) -> int:
        """Draw *text* at (x, y); returns the total pixel width drawn."""
        cursor_x = x
        for char in text.upper():
            if char == ' ':
                cursor_x += self.glyph_size // 2 + self.spacing
                continue
            glyph = self._get_glyph(char)
            if glyph:
                screen.blit(glyph, (cursor_x, y))
                cursor_x += self.glyph_size + self.spacing
        return cursor_x - x

    # ------------------------------------------------------------------
    def text_width(self, text: str) -> int:
        """Calculate the pixel width of *text* without drawing."""
        width = 0
        for char in text.upper():
            if char == ' ':
                width += self.glyph_size // 2 + self.spacing
            elif char.upper() in self.CHAR_MAP:
                width += self.glyph_size + self.spacing
        return width


# =============================================================================
# MENU
# =============================================================================

class Menu:
    """Custom-asset main menu with pixel font, logo frame, and arrow cursor."""

    LANGUAGES    = ["Python", "Java", "JavaScript", "HTML", "CSS"]
    BTN_X        = 350          # left edge of the button column
    BTN_Y_START  = 480          # y of first button label
    BTN_STEP     = 70           # vertical gap between buttons
    GLYPH_SIZE   = 28           # letter size for buttons
    TITLE_GLYPH  = 36           # letter size for the title

    def __init__(self):
        self.font        = PixelFont(self.GLYPH_SIZE)
        self.title_font  = PixelFont(self.TITLE_GLYPH)
        self.hovered     = -1   # index of button under cursor (-1 = none)

        # --- Load UI assets ---
        self.logo  = self._load_logo()
        self.arrow = self._load_arrow()

    # ------------------------------------------------------------------
    def _load_logo(self) -> pygame.Surface | None:
        try:
            img = pygame.image.load("GRAPHICS/UI/Logo.png").convert_alpha()
            # Scale to span most of the screen width as a title frame
            return pygame.transform.scale(img, (700, 120))
        except FileNotFoundError:
            return None

    # ------------------------------------------------------------------
    def _load_arrow(self) -> pygame.Surface | None:
        try:
            img = pygame.image.load("GRAPHICS/UI/Arrow.png").convert_alpha()
            return pygame.transform.scale(img, (36, 36))
        except FileNotFoundError:
            return None

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        screen.fill(DARK)

        # --- Title frame (Logo.png) ---
        title_text = "THE SYNTAX ESCAPE"
        if self.logo:
            logo_x = SCREEN_WIDTH // 2 - self.logo.get_width() // 2
            logo_y = 80
            screen.blit(self.logo, (logo_x, logo_y))
            
            vertical_offset = -16
            # Centre the title text inside the logo frame
            tw = self.title_font.text_width(title_text)
            tx = SCREEN_WIDTH // 2 - tw // 2
            ty = (logo_y + self.logo.get_height() // 2 - self.TITLE_GLYPH // 2) + vertical_offset
            self.title_font.render(title_text, screen, tx, ty)
        else:
            # Fallback if logo is missing
            tw = self.title_font.text_width(title_text)
            self.title_font.render(title_text, screen, SCREEN_WIDTH // 2 - tw // 2, 100)

        # --- Sub-heading ---
        sub = "SELECT LANGUAGE"
        sw  = self.font.text_width(sub)
        self.font.render(sub, screen, SCREEN_WIDTH // 2 - sw // 2, 390)

        # --- Detect hovered button ---
        self.hovered = -1
        for i, lang in enumerate(self.LANGUAGES):
            if self._button_rect(i).collidepoint(mouse_pos):
                self.hovered = i

        # --- Draw language buttons ---
        for i, lang in enumerate(self.LANGUAGES):
            rect      = self._button_rect(i)
            is_hovered = (i == self.hovered)
            colour    = (255, 215, 0) if is_hovered else WHITE

            # Highlight bar behind hovered item
            if is_hovered:
                highlight = pygame.Surface((rect.width + 20, rect.height), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 25))
                screen.blit(highlight, (rect.x - 10, rect.y))

            lw = self.font.text_width(lang)
            lx = SCREEN_WIDTH // 2 - lw // 2
            ly = rect.y + rect.height // 2 - self.GLYPH_SIZE // 2

            # Draw arrow to the left of hovered item
            if is_hovered and self.arrow:
                ax = lx - self.arrow.get_width() - 12
                ay = ly + self.GLYPH_SIZE // 2 - self.arrow.get_height() // 2
                screen.blit(self.arrow, (ax, ay))

            # Temporarily tint glyphs gold on hover by drawing with a colour overlay
            if is_hovered:
                # Render to temp surface so we can tint it
                tmp = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                self.font.render(lang, tmp, 0, 0)
                tint = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                tint.fill((255, 215, 0, 120))
                tmp.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (lx, ly))
            else:
                self.font.render(lang, screen, lx, ly)

        # --- Custom arrow cursor ---
        if self.arrow:
            screen.blit(self.arrow, mouse_pos)

    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Return the selected language name, or None if no button was hit."""
        for i, lang in enumerate(self.LANGUAGES):
            if self._button_rect(i).collidepoint(pos):
                return lang
        return None

    # ------------------------------------------------------------------
    def _button_rect(self, index: int) -> pygame.Rect:
        lw = self.font.text_width(self.LANGUAGES[index])
        return pygame.Rect(
            SCREEN_WIDTH // 2 - lw // 2 - 20,
            self.BTN_Y_START + index * self.BTN_STEP,
            lw + 40,
            self.GLYPH_SIZE + 16,
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
    """Reset player position, physics, and re-spawn all enemies."""
    player.rect.x         = -5
    player.rect.y         = SCREEN_HEIGHT - 350
    player.hitbox.center  = player.rect.center   # sync hitbox immediately
    player.vel_y          = 0                    # clear any leftover fall speed
    player.jumped         = False
    player.on_ground      = False
    player.is_dying       = False
    player.is_playing_idle = False
    player.status         = "STAND"
    player.frame_index    = 0.0
    player.respawn_time   = pygame.time.get_ticks()
    player.last_action_time = pygame.time.get_ticks()
    spawn_slimes(slime_group)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(False)   # replaced by Arrow.png cursor
    clock = pygame.time.Clock()

    # --- Core objects ---
    bg_manager  = BackgroundManager()
    menu        = Menu()
    player      = Player(-5, SCREEN_HEIGHT - 350)
    player.respawn_time = pygame.time.get_ticks()  # grace period from the very start
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
                    pygame.mouse.set_visible(True)   # restore cursor in game
                    print(f"Started {selected_language} – Level {selected_level}")

            elif game_state == PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over != 0:
                    game_over = 0
                    reset_game(player, slime_group)

            elif game_state == WIN and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_over  = 0
                    game_state = MENU
                    pygame.mouse.set_visible(False)
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
            menu.draw(screen, pygame.mouse.get_pos())

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