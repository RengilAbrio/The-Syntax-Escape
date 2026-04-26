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
PAUSED  = 4

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
GOLD   = (255, 215, 0)

# --- FIX 3 & 4: Acceleration-based physics with asymmetric gravity ---
#
#   Old code:  dx = ±MOVE_SPEED  (binary ON/OFF, instant top speed)
#   New code:  vel_x accelerates toward PLAYER_MAX_SPEED, bleeds off via FRICTION
#
#   Old gravity: same force going up and down  → "floaty balloon" arc
#   New gravity: 2× stronger on the way down   → short snappy arc, authoritative landing
#
PLAYER_ACCEL     = 1.2    # speed added per frame while key held
PLAYER_FRICTION  = 0.70   # velocity multiplier per frame when no key held (lower = snappier stop)
PLAYER_MAX_SPEED = 7      # px/frame horizontal cap
PLAYER_JUMP      = -17    # initial upward velocity
PLAYER_GRAV_UP   = 1.2    # gravity while rising
PLAYER_GRAV_DOWN = 2.6    # gravity while falling  (makes landing feel heavy and decisive)
PLAYER_MAX_FALL  = 22     # terminal velocity


# =============================================================================
# WORLD DATA
# =============================================================================

# fmt: off
WORLD_DATA = [
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
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,2,2,2,2,2,2,2],  # enemy
    [2,2,2,2,0,0,0,0,3,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
# fmt: on

SLIME_SPAWN_POSITIONS = [
    (col * TILE_SIZE, row * TILE_SIZE)
    for row, tiles in enumerate(WORLD_DATA)
    for col, tile  in enumerate(tiles)
    if tile == TILE_ENEMY
]


# =============================================================================
# HELPERS
# =============================================================================

def load_scaled_image(path: str, size: tuple) -> pygame.Surface:
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)


# =============================================================================
# GATE
# =============================================================================

class Gate(pygame.sprite.Sprite):
    FRAME_COLS   = 4
    ANIM_SPEED   = 0.08
    DISPLAY_SIZE = (80, 80)

    def __init__(self, x: int, y: int):
        super().__init__()
        self.frames      = self._load_frames()
        self.frame_index = 0.0
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect(bottomleft=(x, y + TILE_SIZE))
        self.hitbox      = self.rect.inflate(-20, -10)
        self.is_opening  = False
        self.is_open     = False

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

    def trigger(self) -> None:
        if not self.is_opening and not self.is_open:
            self.is_opening = True

    def reset(self) -> None:
        self.is_opening  = False
        self.is_open     = False
        self.frame_index = 0.0
        self.image       = self.frames[0]

    def update(self) -> None:
        if not self.is_opening:
            return
        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.frame_index = len(self.frames) - 1
            self.is_opening  = False
            self.is_open     = True
        self.image = self.frames[int(self.frame_index)]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


# =============================================================================
# BACKGROUND MANAGER
# =============================================================================

class BackgroundManager:
    SWITCH_INTERVAL = 10_000
    LAYER_SPEEDS    = [0.1, 0.2, 0.3, 0.4, 0.5]

    def __init__(self):
        self.day_images   = []
        self.night_images = []

        for i in range(1, 6):
            try:
                self.day_images.append(
                    load_scaled_image(f"GRAPHICS/BACKGROUND/1/Day/{i}.png",   (SCREEN_WIDTH, SCREEN_HEIGHT))
                )
                self.night_images.append(
                    load_scaled_image(f"GRAPHICS/BACKGROUND/1/Night/{i}.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
                )
            except FileNotFoundError:
                pass

        self.is_day      = True
        self.last_switch = pygame.time.get_ticks()
        self.scroll      = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_switch > self.SWITCH_INTERVAL:
            self.is_day      = not self.is_day
            self.last_switch = now

        layers        = self.day_images if self.is_day else self.night_images
        self.scroll  += 2.0

        for img, speed in zip(layers, self.LAYER_SPEEDS):
            # FIX 7: round to int — eliminates sub-pixel shimmer on background layers
            x_offset = round((self.scroll * speed) % SCREEN_WIDTH)
            screen.blit(img, (-x_offset, 0))
            screen.blit(img, (SCREEN_WIDTH - x_offset, 0))


# =============================================================================
# PLAYER
# =============================================================================

class Player(pygame.sprite.Sprite):
    """
    Smooth, professional-feeling platformer character.

    FIX 3: Horizontal movement uses acceleration + friction instead of binary on/off.
    FIX 4: Asymmetric gravity — lighter on the way up, heavy on the way down.
    FIX 7: Float positions tracked internally; rect is always integer-snapped.
    """

    ANIMATION_SPEED  = 0.10
    IDLE_WAIT_MS     = 5_000
    DEATH_DELAY_MS   = 1_000
    RESPAWN_GRACE_MS = 1_000

    def __init__(self, x: int, y: int):
        super().__init__()

        self.animations   = {"IDLE": [], "RUN": [], "JUMP": []}
        self.status       = "STAND"
        self.frame_index  = 0.0
        self.facing_right = True

        self._load_animations()

        self.image  = self.animations["IDLE"][0] if self.animations["IDLE"] else pygame.Surface((64, 64))
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-20, -10)

        # FIX 7: float sub-pixel positions — rect is derived from these, never the other way
        self.pos_x = float(x)
        self.pos_y = float(y)

        # FIX 3: velocity replaces instant dx
        self.vel_x     = 0.0
        self.vel_y     = 0.0
        self.jumped    = False
        self.on_ground = False

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
                        self.animations[name].append(pygame.transform.scale(img, (64, 64)))
            except FileNotFoundError:
                print(f"[Player] Animation folder not found: {folder}")

    # ------------------------------------------------------------------
    def _animate(self) -> None:
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
                self.is_playing_idle  = False
                self.status           = "STAND"
                self.frame_index      = 0.0
                self.last_action_time = pygame.time.get_ticks()
            else:
                self.frame_index = 0.0

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ------------------------------------------------------------------
    def _get_input(self) -> bool:
        """
        FIX 3: Accelerate toward max speed while a key is held; bleed speed
        via friction when no key is held.  Returns True if any action taken.
        """
        keys         = pygame.key.get_pressed()
        action_taken = False

        if keys[pygame.K_LEFT]:
            self.vel_x        = max(self.vel_x - PLAYER_ACCEL, -PLAYER_MAX_SPEED)
            self.facing_right = False
            action_taken      = True
        elif keys[pygame.K_RIGHT]:
            self.vel_x        = min(self.vel_x + PLAYER_ACCEL,  PLAYER_MAX_SPEED)
            self.facing_right = True
            action_taken      = True
        else:
            # Friction — bleed horizontal speed to zero
            self.vel_x *= PLAYER_FRICTION
            if abs(self.vel_x) < 0.15:
                self.vel_x = 0.0

        # Update run/stand status based on speed
        if abs(self.vel_x) > 0.5 and self.on_ground:
            self.status  = "RUN"
            action_taken = True

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground and not self.jumped:
            self.vel_y   = PLAYER_JUMP
            self.jumped  = True
            self.status  = "JUMP"
            action_taken = True

        if not keys[pygame.K_SPACE]:
            self.jumped = False

        return action_taken

    # ------------------------------------------------------------------
    def _apply_physics(self, world) -> None:
        """
        FIX 4: Apply asymmetric gravity — 2× stronger force on the way down.
        FIX 7: Accumulate movement in floats; snap rect to integers before collision.
        """
        # FIX 4: asymmetric gravity
        grav        = PLAYER_GRAV_UP if self.vel_y < 0 else PLAYER_GRAV_DOWN
        self.vel_y  = min(self.vel_y + grav, PLAYER_MAX_FALL)
        self.on_ground = False

        # --- Horizontal ---
        self.pos_x  += self.vel_x
        self.rect.x  = round(self.pos_x)   # FIX 7: integer snap
        self.hitbox.center = self.rect.center

        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.vel_x > 0:
                    self.rect.right = tile_rect.left
                elif self.vel_x < 0:
                    self.rect.left  = tile_rect.right
                self.pos_x = float(self.rect.x)
                self.vel_x = 0.0

        # --- Vertical ---
        self.pos_y  += self.vel_y
        self.rect.y  = round(self.pos_y)   # FIX 7
        self.hitbox.center = self.rect.center

        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.vel_y < 0:
                    self.rect.top  = tile_rect.bottom
                    self.pos_y     = float(self.rect.y)
                    self.vel_y     = 0.0
                else:
                    self.rect.bottom = tile_rect.top
                    self.pos_y       = float(self.rect.y)
                    self.vel_y       = 0.0
                    self.on_ground   = True
                    self.jumped      = False
                    if abs(self.vel_x) < 0.5:
                        self.status = "STAND"

        self.hitbox.center = self.rect.center

    # ------------------------------------------------------------------
    def update(self, world, game_over: int, slime_group) -> int:
        if game_over != 0:
            self._animate()
            return game_over

        if self.is_dying:
            if pygame.time.get_ticks() - self.death_time > self.DEATH_DELAY_MS:
                return -1
            self._animate()
            return game_over

        now          = pygame.time.get_ticks()
        in_grace     = (now - self.respawn_time) < self.RESPAWN_GRACE_MS
        action_taken = self._get_input()

        if not action_taken and self.on_ground:
            if self.is_playing_idle:
                self.status = "IDLE"
            elif now - self.last_action_time > self.IDLE_WAIT_MS:
                self.is_playing_idle = True
                self.frame_index     = 0.0
                self.status          = "IDLE"
        elif action_taken:
            self.last_action_time = now
            self.is_playing_idle  = False

        self._apply_physics(world)

        if not in_grace:
            for slime in slime_group:
                if self.hitbox.colliderect(slime.hitbox):
                    self.is_dying   = True
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
    TILE_IMAGES = {
        TILE_BLOCK: "GRAPHICS/TILES/Tile_02.png",
        TILE_GRASS: "GRAPHICS/TILES/Tile_01.png",
        TILE_ROCK:  "GRAPHICS/TILES/Tile_03.png",
    }

    def __init__(self, data: list[list[int]], difficulty: int, slime_group: pygame.sprite.Group):
        self.tile_list  = []
        self.gate_group = pygame.sprite.Group()
        self.difficulty = difficulty

        tile_surfaces = {
            tid: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )
            for tid, path in self.TILE_IMAGES.items()
        }

        for row_idx, row in enumerate(data):
            for col_idx, tile_id in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if tile_id in tile_surfaces:
                    img = tile_surfaces[tile_id]
                    self.tile_list.append((img, img.get_rect(topleft=(x, y))))
                elif tile_id == TILE_ENEMY:
                    for _ in range(difficulty):
                        slime_group.add(Enemy(x, y))
                elif tile_id == TILE_GATE:
                    self.gate_group.add(Gate(x, y))

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
    MOVE_SPEED      = 1.5
    PATROL_WIDTH    = 100
    ANIM_SPEED      = 0.15
    GRAVITY         = 1
    MAX_FALL_SPEED  = 10
    WALK_DURATION   = 5 * FPS
    IDLE_DURATION   = 3 * FPS
    SCALE_FACTOR    = 1.5
    VISUAL_OFFSET_Y = 35

    def __init__(self, x: int, y: int):
        super().__init__()
        self.idle_frames = self._load_sheet("GRAPHICS/Enemies/Slime1.png", cols=6, row=2)
        self.walk_frames = self._load_sheet("GRAPHICS/Enemies/Slime2.png", cols=8, row=2)

        self.state     = "WALKING"
        self.direction = 1
        self.pos_x     = float(x)
        self.center_x  = float(x)
        self.vel_y     = 0
        self.timer     = 0

        self.state_durations = {"WALKING": self.WALK_DURATION, "IDLE": self.IDLE_DURATION}

        self.current_frame = 0.0
        self.image  = self.walk_frames[0]
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-60, -60)

    def _load_sheet(self, path: str, cols: int, row: int) -> list[pygame.Surface]:
        sheet   = pygame.image.load(path).convert_alpha()
        frame_w = sheet.get_width()  // cols
        frame_h = sheet.get_height() // 4
        new_w   = int(frame_w * self.SCALE_FACTOR)
        new_h   = int(frame_h * self.SCALE_FACTOR)
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, row * frame_h, frame_w, frame_h)),
                (new_w, new_h),
            )
            for i in range(cols)
        ]

    def update(self, world) -> None:
        self.vel_y  = min(self.vel_y + self.GRAVITY, self.MAX_FALL_SPEED)
        self.rect.y += self.vel_y

        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile_rect.top
                elif self.vel_y < 0:
                    self.rect.top = tile_rect.bottom
                self.vel_y = 0

        self.timer += 1
        if self.timer >= self.state_durations[self.state]:
            self.timer = 0
            self.state = "IDLE" if self.state == "WALKING" else "WALKING"

        if self.state == "WALKING":
            self.pos_x += self.MOVE_SPEED * self.direction
            left  = self.center_x - self.PATROL_WIDTH / 2
            right = self.center_x + self.PATROL_WIDTH / 2
            if self.pos_x >= right:
                self.pos_x, self.direction = right, -1
            elif self.pos_x <= left:
                self.pos_x, self.direction = left,  1

        self.rect.x        = round(self.pos_x)   # FIX 7
        self.hitbox.center = (self.rect.centerx, self.rect.centery + self.VISUAL_OFFSET_Y)

        frames             = self.walk_frames if self.state == "WALKING" else self.idle_frames
        self.current_frame = (self.current_frame + self.ANIM_SPEED) % len(frames)
        raw                = frames[int(self.current_frame)]
        self.image         = pygame.transform.flip(raw, True, False) if self.direction == 1 else raw

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y + self.VISUAL_OFFSET_Y))


# =============================================================================
# PIXEL FONT
# =============================================================================

class PixelFont:
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

    def _get_glyph(self, char: str) -> pygame.Surface | None:
        char = char.upper()
        if char not in self.CHAR_MAP:
            return None
        if char not in self._cache:
            path = self.LETTER_DIR + self.CHAR_MAP[char] + ".png"
            try:
                img = pygame.image.load(path).convert()
                img.set_colorkey((255, 255, 255))
                self._cache[char] = pygame.transform.scale(img, (self.glyph_size, self.glyph_size))
            except FileNotFoundError:
                return None
        return self._cache[char]

    def render(self, text: str, screen: pygame.Surface, x: int, y: int) -> int:
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

    def text_width(self, text: str) -> int:
        width = 0
        for char in text.upper():
            if char == ' ':
                width += self.glyph_size // 2 + self.spacing
            elif char in self.CHAR_MAP:
                width += self.glyph_size + self.spacing
        return width


# =============================================================================
# MENU BASE  — shared button logic for WinMenu and PauseMenu
# =============================================================================

class _ButtonMenu:
    """
    FIX 1: All buttons rendered at the same uniform width (widest label + padding).
            No more "floaty" mismatched boxes on every option.

    FIX 2: Clicking a button triggers a 150 ms bright flash — immediate tactile feedback.
    """

    CLICK_FLASH_MS = 150
    BTN_STEP       = 60
    BTN_PADDING    = 40   # horizontal padding added on each side of the widest label

    # Subclasses must define: OPTIONS, BTN_Y

    def __init__(self, glyph_size: int = 28):
        self.font = PixelFont(glyph_size)

        self._click_idx : int | None = None
        self._click_time: int        = 0

        # FIX 1: single shared width = widest label + padding
        self._btn_w = max(self.font.text_width(o) for o in self.OPTIONS) + self.BTN_PADDING * 2

    # ------------------------------------------------------------------
    def _button_rect(self, index: int) -> pygame.Rect:
        """Every button is the same width."""
        return pygame.Rect(
            SCREEN_WIDTH // 2 - self._btn_w // 2,
            self.BTN_Y + index * self.BTN_STEP,
            self._btn_w,
            self.font.glyph_size + 16,
        )

    # ------------------------------------------------------------------
    def _draw_buttons(
        self,
        screen     : pygame.Surface,
        mouse_pos  : tuple[int, int],
        hover_color: tuple,
        flash_color: tuple,
    ) -> None:
        now = pygame.time.get_ticks()

        for i, option in enumerate(self.OPTIONS):
            rect        = self._button_rect(i)
            is_hovered  = rect.collidepoint(mouse_pos)
            # FIX 2: flash takes visual priority over plain hover
            is_flashing = (
                i == self._click_idx
                and now - self._click_time < self.CLICK_FLASH_MS
            )

            if is_flashing:
                # Filled flash + coloured border
                flash_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                flash_surf.fill((*flash_color, 70))
                screen.blit(flash_surf, rect.topleft)
                pygame.draw.rect(screen, flash_color, rect, 4)
            elif is_hovered:
                pygame.draw.rect(screen, hover_color, rect, 4)

            # Centred label text
            tw = self.font.text_width(option)
            tx = SCREEN_WIDTH // 2 - tw // 2
            ty = rect.y + rect.height // 2 - self.font.glyph_size // 2
            self.font.render(option, screen, tx, ty)

    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> int | None:
        for i in range(len(self.OPTIONS)):
            if self._button_rect(i).collidepoint(pos):
                # FIX 2: start the click flash
                self._click_idx  = i
                self._click_time = pygame.time.get_ticks()
                return i
        return None


# =============================================================================
# MENU  (Language Selection)
# =============================================================================

class Menu:
    """
    FIX 1: Uniform button widths — all language buttons share the same width.
    FIX 2: Click flash feedback on selection.
    """

    LANGUAGES   = ["Python", "Java", "JavaScript", "HTML", "CSS"]
    BTN_Y_START = 480
    BTN_STEP    = 70
    GLYPH_SIZE  = 28
    TITLE_GLYPH = 36
    BTN_PADDING = 40
    FLASH_MS    = 150

    def __init__(self):
        self.font       = PixelFont(self.GLYPH_SIZE)
        self.title_font = PixelFont(self.TITLE_GLYPH)
        self.hovered    = -1
        self.logo       = self._load_logo()
        self.arrow      = self._load_arrow()

        # FIX 1: one shared width for all language buttons
        self._btn_w      = max(self.font.text_width(l) for l in self.LANGUAGES) + self.BTN_PADDING * 2
        self._click_idx  : int | None = None
        self._click_time : int        = 0

    def _load_logo(self) -> pygame.Surface | None:
        try:
            return pygame.transform.scale(
                pygame.image.load("GRAPHICS/UI/Logo.png").convert_alpha(), (700, 120)
            )
        except FileNotFoundError:
            return None

    def _load_arrow(self) -> pygame.Surface | None:
        try:
            return pygame.transform.scale(
                pygame.image.load("GRAPHICS/UI/Arrow.png").convert_alpha(), (36, 36)
            )
        except FileNotFoundError:
            return None

    def _button_rect(self, index: int) -> pygame.Rect:
        # FIX 1: uniform width
        return pygame.Rect(
            SCREEN_WIDTH // 2 - self._btn_w // 2,
            self.BTN_Y_START + index * self.BTN_STEP,
            self._btn_w,
            self.GLYPH_SIZE + 16,
        )

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        screen.fill(DARK)

        # Title
        title_text = "THE SYNTAX ESCAPE"
        if self.logo:
            logo_x = SCREEN_WIDTH // 2 - self.logo.get_width() // 2
            logo_y = 80
            screen.blit(self.logo, (logo_x, logo_y))
            tw = self.title_font.text_width(title_text)
            tx = SCREEN_WIDTH // 2 - tw // 2
            ty = logo_y + self.logo.get_height() // 2 - self.TITLE_GLYPH // 2 - 16
            self.title_font.render(title_text, screen, tx, ty)
        else:
            tw = self.title_font.text_width(title_text)
            self.title_font.render(title_text, screen, SCREEN_WIDTH // 2 - tw // 2, 100)

        sub = "SELECT LANGUAGE"
        sw  = self.font.text_width(sub)
        self.font.render(sub, screen, SCREEN_WIDTH // 2 - sw // 2, 390)

        # Detect hovered button
        self.hovered = -1
        for i in range(len(self.LANGUAGES)):
            if self._button_rect(i).collidepoint(mouse_pos):
                self.hovered = i

        now = pygame.time.get_ticks()

        for i, lang in enumerate(self.LANGUAGES):
            rect        = self._button_rect(i)
            is_hovered  = (i == self.hovered)
            # FIX 2: flash after click
            is_flashing = (i == self._click_idx and now - self._click_time < self.FLASH_MS)

            if is_flashing:
                flash_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                flash_surf.fill((255, 215, 0, 80))
                screen.blit(flash_surf, rect.topleft)
                pygame.draw.rect(screen, GOLD, rect, 4)
            elif is_hovered:
                highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 25))
                screen.blit(highlight, rect.topleft)

            lw = self.font.text_width(lang)
            lx = SCREEN_WIDTH // 2 - lw // 2
            ly = rect.y + rect.height // 2 - self.GLYPH_SIZE // 2

            if is_hovered and self.arrow:
                ax = rect.left + 8
                ay = ly + self.GLYPH_SIZE // 2 - self.arrow.get_height() // 2
                screen.blit(self.arrow, (ax, ay))

            if is_hovered or is_flashing:
                # Gold tint on hover / flash
                tmp  = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                self.font.render(lang, tmp, 0, 0)
                tint = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                tint.fill((255, 215, 0, 120))
                tmp.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (lx, ly))
            else:
                self.font.render(lang, screen, lx, ly)

        # Custom arrow cursor
        if self.arrow:
            screen.blit(self.arrow, mouse_pos)

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        for i, lang in enumerate(self.LANGUAGES):
            if self._button_rect(i).collidepoint(pos):
                # FIX 2: start flash
                self._click_idx  = i
                self._click_time = pygame.time.get_ticks()
                return lang
        return None


# =============================================================================
# WIN MENU
# =============================================================================

class WinMenu(_ButtonMenu):
    OPTIONS  = ["MAIN MENU", "RESTART", "NEXT LEVEL"]
    BTN_Y    = 450
    BTN_STEP = 60

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        self._draw_buttons(screen, mouse_pos, hover_color=GOLD, flash_color=WHITE)


# =============================================================================
# PAUSE MENU
# =============================================================================

class PauseMenu(_ButtonMenu):
    OPTIONS  = ["CONTINUE", "MAIN MENU", "RESET"]
    BTN_Y    = 400
    BTN_STEP = 60

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # FIX: "PAUSED" properly centred (was hardcoded x=450)
        label = "PAUSED"
        pw    = self.font.text_width(label)
        self.font.render(label, screen, SCREEN_WIDTH // 2 - pw // 2, 250)

        self._draw_buttons(screen, mouse_pos, hover_color=GREEN, flash_color=WHITE)


# =============================================================================
# GAME HELPERS
# =============================================================================

def spawn_slimes(slime_group: pygame.sprite.Group) -> None:
    slime_group.empty()
    for x, y in SLIME_SPAWN_POSITIONS:
        slime_group.add(Enemy(x, y))


def reset_game(player: Player, slime_group: pygame.sprite.Group, world) -> None:
    player.pos_x            = -5.0
    player.pos_y            = float(SCREEN_HEIGHT - 350)
    player.rect.x           = -5
    player.rect.y           = SCREEN_HEIGHT - 350
    player.hitbox.center    = player.rect.center
    player.vel_x            = 0.0
    player.vel_y            = 0.0
    player.jumped           = False
    player.on_ground        = False
    player.is_dying         = False
    player.is_playing_idle  = False
    player.status           = "STAND"
    player.frame_index      = 0.0
    player.respawn_time     = pygame.time.get_ticks()
    player.last_action_time = pygame.time.get_ticks()

    spawn_slimes(slime_group)

    for gate in world.gate_group:
        gate.reset()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    bg_manager  = BackgroundManager()
    menu        = Menu()
    player      = Player(-5, SCREEN_HEIGHT - 350)
    player.respawn_time = pygame.time.get_ticks()
    slime_group = pygame.sprite.Group()
    world       = None
    game_over   = 0
    game_state  = MENU
    selected_language = None
    selected_level    = 1
    win_menu    = None
    pause_menu  = PauseMenu()
    paused      = False
    needs_reset = False

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
                    world      = World(WORLD_DATA, selected_level, slime_group)
                    game_state = PLAYING
                    pygame.mouse.set_visible(True)
                    if needs_reset:
                        reset_game(player, slime_group, world)
                        needs_reset = False
                    print(f"Started {selected_language} – Level {selected_level}")

            elif game_state in (PLAYING, WIN) or paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and game_state == PLAYING:
                        paused = not paused
                    elif event.key == pygame.K_r and game_over == -1:
                        game_over = 0
                        reset_game(player, slime_group, world)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_state == WIN and win_menu:
                        choice = win_menu.handle_click(pygame.mouse.get_pos())
                        if choice == 0:    # MAIN MENU
                            game_state  = MENU
                            win_menu    = None
                            game_over   = 0
                            paused      = False
                            needs_reset = True
                            pygame.mouse.set_visible(False)
                        elif choice == 1:  # RESTART
                            game_over  = 0
                            game_state = PLAYING
                            reset_game(player, slime_group, world)
                        elif choice == 2:  # NEXT LEVEL
                            print("Next level!")

                    elif paused and game_state == PLAYING:
                        choice = pause_menu.handle_click(pygame.mouse.get_pos())
                        if choice == 0:    # CONTINUE
                            paused = False
                        elif choice == 1:  # MAIN MENU
                            game_state = MENU
                            paused     = False
                            pygame.mouse.set_visible(False)
                        elif choice == 2:  # RESET
                            game_over = 0
                            paused    = False
                            reset_game(player, slime_group, world)

        # -----------------------------------------------------------------
        # UPDATE
        # -----------------------------------------------------------------
        if game_state == PLAYING and game_over == 0 and not paused:
            game_over = player.update(world, game_over, slime_group)

            if not player.is_dying:
                slime_group.update(world)

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
                screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))

            if paused:
                pause_menu.draw(screen, pygame.mouse.get_pos())
                pygame.mouse.set_visible(True)

        elif game_state == WIN:
            bg_manager.draw(screen)
            world.draw(screen)
            for enemy in slime_group:
                enemy.draw(screen)
            player.draw(screen)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            win_msg = win_font.render("YOU ESCAPED!", True, GOLD)
            screen.blit(win_msg, (SCREEN_WIDTH // 2 - win_msg.get_width() // 2, 200))

            if win_menu is None:
                win_menu = WinMenu()
            win_menu.draw(screen, pygame.mouse.get_pos())
            pygame.mouse.set_visible(True)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()