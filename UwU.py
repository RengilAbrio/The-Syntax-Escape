import pygame
from pygame.locals import *
import os

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

class Player():
    def __init__(self, x, y):
        self.animations = {'IDLE': [], 'RUN': [], 'JUMP': []}
        self.status = 'STAND'
        self.frame_index = 0
        self.animation_speed = 0.10
        self.index = 0
        self.counter = 0
        
        self.facing_right = True
        
        self.last_action_time = pygame.time.get_ticks()
        self.is_playing_idle = False
        
        self.import_assets()
        
        # Set initial image
        if len(self.animations['IDLE']) > 0:
            self.image = self.animations['IDLE'][0]
        else:
            self.image = pygame.Surface((180, 180))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Movement variables
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        
    def import_assets(self):
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
        
        # Jumping
        if key[pygame.K_SPACE] and not self.jumped:
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
            # Get input
            dx, dy, action_taken = self.get_input()
            
            
            # Idle animation logic
            current_time = pygame.time.get_ticks()
            if not action_taken and not self.jumped:
                if self.is_playing_idle:
                    self.status = 'IDLE'
                else:
                    self.status = 'STAND'
                    if current_time - self.last_action_time > 5000:  # 5 seconds
                        self.is_playing_idle = True
                        self.frame_index = 0
                        self.status = 'IDLE'
            else:
                # Reset idle timer on any action
                self.last_action_time = current_time
                self.is_playing_idle = False

            # Apply gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            
            # Collision detection
            for tile in world.tile_list:
                # Horizontal collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, 63, 63):
                    dx = 0

                # Vertical collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, 63, 63):
                    # Hit ceiling
                    if self.vel_y < 0:
                        self.rect.top = tile[1].bottom
                        self.vel_y = 0
                    # Landed on ground
                    elif self.vel_y >= 0:
                        self.rect.bottom = tile[1].top
                        self.vel_y = 0
                        # Reset jump when landing
                        if self.status == 'JUMP':
                            if abs(dx) > 0:
                                self.status = 'RUN'
                            else:
                                self.status = 'STAND'
                                
            # --- CHECK FOR COLLISION (ENEMIES) ---
            if pygame.sprite.spritecollide(self, slime_group, False):
                return -1


            # Update position
            self.rect.x += dx
            self.rect.y += dy

        # Animate (MUST be called before drawing)
        self.animate()
        
        # Update width/height for collision
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        return game_over

    def draw(self, screen):
        draw_pos = (self.rect.x, self.rect.y + 10) 
        screen.blit(self.image, draw_pos)
        


class World():
    def __init__(self, data):
        self.tile_list = []

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
                    slime = Enemy(col_count * tile_size, row_count * tile_size )
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
            
            
bg_manager = BackgroundManager()
player = Player(-5, screen_height - 350)

slime_group = pygame.sprite.Group()


world = World (world_data)

run = True
while run:

    clock.tick(fps)
    if game_over == 0: 
        bg_manager.draw_bg(screen)

        world.draw()

        slime_group.update(world)
        for enemy in slime_group:
            visual_offset_y = -35
            screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y - visual_offset_y))
            
        game_over = player.update(world, game_over)
        player.draw(screen)
    else:
        bg_manager.draw_bg(screen)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over != 0:
                game_over = 0
                player.rect.x = -5
                player.rect.y = screen_height - 350
        
                # Clear old slimes
                slime_group.empty()
        
                # Recreate slimes at saved positions
                for x, y in slime_positions:
                    slime = Enemy(x, y)
                    slime_group.add(slime)

    pygame.display.update()

pygame.quit()
