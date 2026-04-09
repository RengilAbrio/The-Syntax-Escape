import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))  # GAME WINDOW/SCREEN (WIDTH,HEIGHT)
pygame.display.set_caption("SYSTEM.REBOOT")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 24, bold=True)

# --- COLORS ---
BLACK = (10, 10, 10)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)

# --- PLAYER/CHARACTER ---
player = pygame.Rect(50, 460, 40, 40)
# --- PLATFORM ---
floor = pygame.Rect(0, 500, 300, 100)
bridge = pygame.Rect(300, 500, 200, 20)
goal = pygame.Rect(500, 500, 300, 100)

# --- GAME PHYSICS ---
vel_y = 0
is_jump = False
bridge_active = False
show_terminal = False
game_state = "RUNNING"

# --- MAIN GAME LOOP ---
while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_state != "RUNNING" and event.key == pygame.K_r:
                player.x, player.y = 50, 460
                vel_y, is_jump, bridge_active, show_terminal, game_state = (
                    0,
                    False,
                    False,
                    False,
                    "RUNNING",
                )

            if event.key == pygame.K_SPACE and not is_jump and not show_terminal:
                vel_y = -16
                is_jump = True

            if show_terminal and event.key == pygame.K_t:
                bridge_active = True
                show_terminal = False

    if game_state == "RUNNING":
        keys = pygame.key.get_pressed()
        if not show_terminal:
            if keys[pygame.K_a]:
                player.x -= 5
            if keys[pygame.K_d]:
                player.x += 5

        vel_y += 1
        player.y += vel_y

        for plat in [floor, goal]:
            if player.colliderect(plat) and vel_y > 0:
                player.bottom = plat.top
                vel_y, is_jump = 0, False

        if bridge_active and player.colliderect(bridge) and vel_y > 0:
            player.bottom = bridge.top
            vel_y, is_jump = 0, False

        if player.right > floor.right and not bridge_active:
            show_terminal = True
            player.right = floor.right

        if player.top > 600:
            game_state = "FAIL"
        if player.x > 700:
            game_state = "WON"

    # DRAW PLATFORM
    pygame.draw.rect(screen, GREEN, floor)
    pygame.draw.rect(screen, GREEN, goal)
    if bridge_active:
        pygame.draw.rect(screen, CYAN, bridge)
    else:
        pygame.draw.rect(screen, GRAY, bridge, 2)
    # DRAW PLAYER
    pygame.draw.rect(screen, CYAN, player)

    if show_terminal:
        pygame.draw.rect(screen, (20, 20, 20), (150, 200, 500, 150))
        pygame.draw.rect(screen, GREEN, (150, 200, 500, 150), 2)
        screen.blit(font.render("if (bridge == __) { }", True, GREEN), (180, 230))
        screen.blit(font.render("Press [T] for TRUE", True, CYAN), (180, 280))

    if game_state == "FAIL":
        screen.blit(font.render("FAILED! Press [R]", True, RED), (300, 300))
    if game_state == "WON":
        screen.blit(font.render("SYSTEM REBOOTED! [R]", True, GREEN), (250, 300))

    pygame.display.flip()
    # GAME TIME
    clock.tick(60)
