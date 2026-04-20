import pygame
from pygame.locals import *
import os

# Game States
MENU = 0
PLAYING = 1
QUIZ = 2

game_state = MENU
selected_language = None
selected_level = 1

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('THE-SYNTAX-ESCAPE')


# --- DEFINE GAME VARIABLES ---
tile_size = 40
game_over = 0 

bg_images = []
for i in range (1,6):
    bg_image = pygame.image.load(f'GRAPHICS/BACKGROUND/1/Day/{i}.png').convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
    bg_images.append(bg_image)


class BackgroundManager:
    def __init__(self):
        self.day_images = []
        self.night_images = []

        for i in range(1, 6):
            try:
                img_day = pygame.image.load(f"GRAPHICS/BACKGROUND/1/Day/{i}.png").convert_alpha()
                self.day_images.append(pygame.transform.scale(img_day, (screen_width, screen_height)))
                
                img_night = pygame.image.load(f"GRAPHICS/BACKGROUND/1/Night/{i}.png").convert_alpha()
                self.night_images.append(pygame.transform.scale(img_night, (screen_width, screen_height)))
            except:
                pass # Suppressing print spam if missing

        self.current_mode = "day" 
        self.last_switch_time = pygame.time.get_ticks()
        self.switch_interval = 10000 
        self.scroll = 0
        self.speeds = [0.1, 0.2, 0.3, 0.4, 0.5]

    def draw_bg(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_switch_time > self.switch_interval:
            self.current_mode = "night" if self.current_mode == "day" else "day"
            self.last_switch_time = now

        active_images = self.day_images if self.current_mode == "day" else self.night_images
        self.scroll += 2  

        for i, bg in enumerate(active_images):
            speed = self.speeds[i]
            x_offset = (self.scroll * speed) % screen_width
            screen.blit(bg, (-x_offset, 0))
            screen.blit(bg, (screen_width - x_offset, 0))

class Player(pygame.sprite.Sprite):  # ← ADD THIS
    def __init__(self, x, y):
        super().__init__()  # ← ADD THIS
        self.animations = {'IDLE': [], 'RUN': [], 'JUMP': []}
        self.status = 'STAND'
        self.frame_index = 0
        self.animation_speed = 0.10
        self.index = 0
        self.counter = 0
        self.facing_right = True
        
        
        self.last_action_time = pygame.time.get_ticks()
        self.is_playing_idle = False
        
        self.import_assets()  # This method MUST exist
        
        # Set initial image
        if len(self.animations['IDLE']) > 0:
            self.image = self.animations['IDLE'][0]
        else:
            self.image = pygame.Surface((180, 180))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.hitbox = self.rect.inflate(-20, -10)
        
        # FIXED PHYSICS
        self.vel_y = 0
        self.jumped = False
        self.on_ground = False
        self.direction = 0
        
        self.is_dying = False
        self.death_time = 0
        self.respawn_time = 0 # Track when we reset
        
    def import_assets(self):  # ← THIS WAS MISSING!
        path = 'GRAPHICS/PLAYER/'
        
        for animation in self.animations.keys():
            full_path = path + animation
            try:
                img_files = sorted(os.listdir(full_path))
                for image_name in img_files:
                    if image_name.endswith('.png') or image_name.endswith('.PNG'):
                        img_path = full_path + '/' + image_name
                        img = pygame.image.load(img_path).convert_alpha()
                        scaled_img = pygame.transform.scale(img, (64, 64))
                        self.animations[animation].append(scaled_img)
            except FileNotFoundError:
                print(f"Folder not found: {full_path}")
                
    def animate(self):
        # Handle STAND state (static first frame of IDLE)
        if self.status == 'STAND':
            if len(self.animations['IDLE']) > 0:
                self.image = self.animations['IDLE'][0]
            return
            
        # Handle other animations (IDLE, RUN, JUMP)
        animation = self.animations.get(self.status, [])
        if len(animation) > 0:
            self.frame_index += self.animation_speed
            
            # Check if animation loop has finished
            if self.frame_index >= len(animation):
                if self.status == 'IDLE':
                    # Stop playing idle, go back to standing
                    self.is_playing_idle = False
                    self.status = 'STAND'
                    self.frame_index = 0
                    self.last_action_time = pygame.time.get_ticks()
                else:
                    # Loop other animations
                    self.frame_index = 0
                    
            self.image = animation[int(self.frame_index)]
        else:
            # Fallback if no animation frames
            self.image = pygame.Surface((64, 64))
                
        # Flip the image if facing left
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def get_input(self):
        """Handle input and return movement values"""
        dx = 0
        dy = 0
        action_taken = False

        key = pygame.key.get_pressed()
        
        # FIXED JUMPING - Only jump if on ground
        if key[pygame.K_SPACE] and self.on_ground and not self.jumped:
            self.vel_y = -15
            self.jumped = True
            self.status = 'JUMP'
            action_taken = True
            
        if not key[pygame.K_SPACE]:
            self.jumped = False

        # Horizontal movement
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
            self.facing_right = False
            self.status = 'RUN'
            action_taken = True
            
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
            self.facing_right = True
            self.status = 'RUN'
            action_taken = True

        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.counter = 0
            self.index = 0

        return dx, dy, action_taken

    def update(self, world, game_over):
        if game_over == 0:
            # If we are in the middle of dying, don't take input
            if self.is_dying:
                # Check if 1000ms (1 second) has passed
                if pygame.time.get_ticks() - self.death_time > 1000:
                    return -1 # Finally trigger game over
                return 0 # Still in delay, stay alive for a moment longer
            else:
            # Get input (only if NOT dying)
                dx, dy, action_taken = self.get_input()
                
                # Idle animation logic
                current_time = pygame.time.get_ticks()
                is_grace_period = (current_time - self.respawn_time) < 1000
                if not action_taken and self.on_ground:
                    if self.is_playing_idle:
                        self.status = 'IDLE'
                    else:
                        self.status = 'STAND'
                        if current_time - self.last_action_time > 5000:
                            self.is_playing_idle = True
                            self.frame_index = 0
                            self.status = 'IDLE'
                else:
                    self.last_action_time = current_time
                    self.is_playing_idle = False

                # Apply gravity
                self.vel_y += 1
                if self.vel_y > 10:
                    self.vel_y = 10
                dy += self.vel_y
                
                # Collision detection with world tiles
                self.on_ground = False
                
                for tile in world.tile_list:
                    # Horizontal collision
                    if tile[1].colliderect(self.rect.x + dx, self.rect.y, 63, 63):
                        dx = 0

                    # Vertical collision
                    if tile[1].colliderect(self.rect.x, self.rect.y + dy, 63, 63):
                        if self.vel_y < 0:  # Ceiling
                            self.rect.top = tile[1].bottom
                            self.vel_y = 0
                        elif self.vel_y >= 0:  # Ground
                            self.rect.bottom = tile[1].top
                            self.vel_y = 0
                            self.on_ground = True
                            self.jumped = False
                            if abs(dx) > 0:
                                self.status = 'RUN'
                            else:
                                self.status = 'STAND'
                                    
            if not self.is_dying and not is_grace_period:
                for slime in slime_group:
                    if self.hitbox.colliderect(slime.hitbox):
                        self.is_dying = True
                        self.death_time = pygame.time.get_ticks()
                        
            # Update position
            self.rect.x += dx
            self.rect.y += dy
            self.hitbox.center = self.rect.center
            

        self.animate()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        return game_over
            

    def draw(self, screen):
        draw_pos = (self.rect.x, self.rect.y + 10) 
        screen.blit(self.image, draw_pos)
        


class World():
    def __init__(self, data, difficulty_level):
        self.tile_list = []
        self.difficulty = difficulty_level
        #load images
        grass_img = pygame.image.load('GRAPHICS/TILES/Tile_01.png').convert_alpha()
        tile_img = pygame.image.load('GRAPHICS/TILES/Tile_02.png').convert_alpha()
        rock_img = pygame.image.load('GRAPHICS/TILES/Tile_03.png').convert_alpha()

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(tile_img,(tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img,(tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(rock_img,(tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
        # Spawn more enemies based on difficulty
                    for _ in range(self.difficulty): 
                        slime = Enemy(col_count * tile_size, row_count * tile_size)
                        slime_group.add(slime)
                col_count += 1
            row_count +=1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile [1], 2)
            
world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2,],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2,],
    [2, 2, 2, 2, 0, 0, 0, 0, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1,],
    [1, 1, 1, 1, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
    [1, 1, 1, 1, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
    [1, 1, 1, 1, 0, 0, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
]

slime_positions = []

for row_idx, row in enumerate(world_data):
    for col_idx, tile in enumerate(row):
        if tile == 4:
            x = col_idx * tile_size
            y = row_idx * tile_size
            slime_positions.append((x, y))
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load your animations
        self.idle_frames = self.load_frames('GRAPHICS/Enemies/Slime1.png', cols=6, row=2)
        self.walk_frames = self.load_frames('GRAPHICS/Enemies/Slime2.png', cols=8, row=2)
        
        # State Management
        self.state = 'WALKING'
        self.direction = 1 
        
        # Use a float for precise movement
        self.pos_x = float(x)
        self.y = y
        
        self.timer = 0
        self.fps = 60 
        self.durations = {'WALKING': 5 * self.fps, 'IDLE': 3 * self.fps}
        
        # Animation setup
        self.current_frame = 0
        self.animation_speed = 0.15
        
        # Patrol settings
        self.center_x = x
        self.patrol_width = 100
        
        self.rect = self.walk_frames[0].get_rect(topleft=(x, y))
        self.image = self.walk_frames[0]
        self.move_speed = 1.5
        
        # Add physics variables
        self.vel_y = 0
    
        
        # Initialize the image
        self.image = self.walk_frames[0]
        
        # --- NEW: Resize the rect to match the new image size ---
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.hitbox = self.rect.inflate(-20, -20)
        self.collision_rect = self.rect.copy()  

    def load_frames(self, filename, cols, row):
        sheet = pygame.image.load(filename).convert_alpha()
        frame_width = sheet.get_width() // cols
        frame_height = sheet.get_height() // 4 
        
        
        scale_factor = 1.5  # 1.5 means 50% bigger
        new_width = int(frame_width * scale_factor)
        new_height = int(frame_height * scale_factor)
        
        frames = []
        for i in range(cols):
            rect = pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height)
            raw_frame = sheet.subsurface(rect)
            scaled_frame = pygame.transform.scale(raw_frame, (new_width, new_height))
            frames.append(scaled_frame)
        return frames

    def update(self, world):
        self.hitbox.center = self.rect.center
        # --- GRAVITY ---
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
            
        self.rect.y += self.vel_y
        
        # --- COLLISION ---
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect):
                # If falling, land on top
                if self.vel_y > 0:
                    self.rect.bottom = tile[1].top
                    self.vel_y = 0
                # If hitting ceiling (optional), stop
                elif self.vel_y < 0:
                    self.rect.top = tile[1].bottom
                    self.vel_y = 0
        
        self.timer += 1
        
        #  State Switching (Only handle State, NOT Direction)
        if self.timer >= self.durations[self.state]:
            self.timer = 0
            self.state = 'IDLE' if self.state == 'WALKING' else 'WALKING'

        # Movement Logic
        if self.state == 'WALKING':
            # Update float position
            self.pos_x += (self.move_speed * self.direction)
            
            # Boundary collision
            left_bound = self.center_x - self.patrol_width // 2
            right_bound = self.center_x + self.patrol_width // 2
            
            if self.pos_x >= right_bound:
                self.pos_x = right_bound
                self.direction = -1
            elif self.pos_x <= left_bound:
                self.pos_x = left_bound
                self.direction = 1
        
        # Sync Rect to Float Position
        self.rect.x = int(self.pos_x)

        # Animation & Flip Logic
        animation_frames = self.walk_frames if self.state == 'WALKING' else self.idle_frames
        
        self.current_frame += self.animation_speed
        if self.current_frame >= len(animation_frames):
            self.current_frame = 0
            
        raw_image = animation_frames[int(self.current_frame)]
        self.image = pygame.transform.flip(raw_image, True, False) if self.direction == 1 else raw_image
            
class Menu:
    
    def __init__(self):
        self.languages = ["Python", "Java", "JavaScript", "HTML", "CSS"]
        self.levels = list(range(1, 11))
        self.font = pygame.font.SysFont('Arial', 30)

    def draw(self, screen):
        screen.fill((20, 20, 20)) # Background
        title = self.font.render("SELECT LANGUAGE & LEVEL", True, (255, 255, 255))
        screen.blit(title, (300, 50))

        # Draw Language Buttons
        for i, lang in enumerate(self.languages):
            rect = pygame.Rect(100, 150 + i*60, 200, 50)
            pygame.draw.rect(screen, (0, 255, 0), rect, 2)
            text = self.font.render(lang, True, (255, 255, 255))
            screen.blit(text, (110, 160 + i*60))

    def handle_click(self, pos):
        global game_state, selected_language
        # Simple collision check for buttons
        for i, lang in enumerate(self.languages):
            rect = pygame.Rect(100, 150 + i*60, 200, 50)
            if rect.collidepoint(pos):
                selected_language = lang
                game_state = PLAYING
                print(f"Started {selected_language} Level {selected_level}")


bg_manager = BackgroundManager()
player = Player(-5, screen_height - 350)

slime_group = pygame.sprite.Group()

menu = Menu()


run = True
while run:
    clock.tick(fps)
    
  # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        # Handle Menu clicks only when in Menu
        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu.handle_click(pygame.mouse.get_pos())
                # Re-initialize world based on selection
                world = World(world_data, selected_level)

        # Handle Reset only when in PLAYING
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over != 0:
                    game_over = 0
                    player.rect.x = -5
                    player.rect.y = screen_height - 350
                    player.respawn_time = pygame.time.get_ticks()
                    slime_group.empty()
                    for x, y in slime_positions:
                        slime = Enemy(x, y)
                        slime_group.add(slime)
                    player.is_dying = False

    # Debugging: Uncomment the line below to check your state in the terminal
    # print(f"Current State: {game_state}")

    # 2. UPDATE LOGIC (Gatekept by Game State)
    if game_state == PLAYING:
        if game_over == 0:
            game_over = player.update(world, game_over)
            if not player.is_dying:
                slime_group.update(world)
    
    # 3. DRAWING (Gatekept by Game State)
    screen.fill((0, 0, 0)) # Clear everything first

    if game_state == MENU:
        menu.draw(screen) # This must be indented!
        
    elif game_state == PLAYING:
        bg_manager.draw_bg(screen)
        world.draw()
        
        for enemy in slime_group:
            visual_offset_y = -35
            screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y - visual_offset_y))
        
        player.draw(screen)
        
        if game_over == -1:
            font = pygame.font.SysFont('Arial', 40)
            text = font.render('GAME OVER - Press R to Restart', True, (255, 255, 255))
            screen.blit(text, (screen_width // 2 - 250, screen_height // 2))

    pygame.display.update()
pygame.quit()