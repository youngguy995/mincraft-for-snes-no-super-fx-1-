import pygame
import math
import sys
import random
import tkinter as tk 
# 1. Initialize Engine & Window Configuration
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Textured 3D Engine: Flight Control Fix")
clock = pygame.time.Clock()

TEX_SIZE = 32 # Texture resolution (32x32 pixels)

# 2. GENERATE RETRO TEXTURES PROCEDURALLY
def create_procedural_textures():
    textures = {}
    
    # 1: Grass Block (Green top band, brown dirt body)
    grass_surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            if y < 8:
                g = random.randint(120, 180)
                grass_surf.set_at((x, y), (34, g, 34))
            else:
                b = random.randint(40, 70)
                grass_surf.set_at((x, y), (b + 30, b, 20))
    textures[1] = grass_surf

    # 2: Stone Block (Speckled Gray)
    stone_surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            c = random.randint(90, 140)
            stone_surf.set_at((x, y), (c, c, c))
    textures[2] = stone_surf

    # 3: Dirt Block (Solid Speckled Brown)
    dirt_surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            b = random.randint(45, 75)
            dirt_surf.set_at((x, y), (b + 30, b, 25))
    textures[3] = dirt_surf

    # 4: Wood Planks (Brown lines pattern)
    wood_surf = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):
        for x in range(TEX_SIZE):
            if y % 8 == 0 or x % 8 == 0:
                wood_surf.set_at((x, y), (70, 40, 15))
            else:
                w = random.randint(110, 140)
                wood_surf.set_at((x, y), (w, int(w*0.6), 30))
    textures[4] = wood_surf

    return textures

TEXTURES = create_procedural_textures()

# 3. Create a 16x16 Room Layout Automatically
MAP_SIZE = 16
MAP = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]

# Build a border wall around the entire map
for i in range(MAP_SIZE):
    MAP[0][i] = 2
    MAP[MAP_SIZE-1][i] = 2
    MAP[i][0] = 2
    MAP[i][MAP_SIZE-1] = 2

# 4. Camera, Flight & Inventory Settings
player_x, player_y = 7.5, 7.5
player_z = 0.0                 # Height level
player_angle = 0.0

# Inventory slots setup
inventory = [1, 2, 3, 4]
selected_slot = 0              

FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 160
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = WIDTH / CASTED_RAYS

font = pygame.font.SysFont("monospace", 16, bold=True)

# 5. Core Engine Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
            
        # Inventory numbers hotkeys 1-4
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: selected_slot = 0
            if event.key == pygame.K_2: selected_slot = 1
            if event.key == pygame.K_3: selected_slot = 2
            if event.key == pygame.K_4: selected_slot = 3
            
            # Left Click -> Destroy block
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bx = int(player_x + math.cos(player_angle) * 1.5)
                by = int(player_y + math.sin(player_angle) * 1.5)
                if 0 < bx < MAP_SIZE - 1 and 0 < by < MAP_SIZE - 1:
                    MAP[by][bx] = 0
                    
            # Right Click -> Place selected inventory block
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                bx = int(player_x + math.cos(player_angle) * 1.5)
                by = int(player_y + math.sin(player_angle) * 1.5)
                if 0 < bx < MAP_SIZE - 1 and 0 < by < MAP_SIZE - 1:
                    MAP[by][bx] = inventory[selected_slot]

    # --- INPUT HANDLER CONTROLS ---
    keys = pygame.key.get_pressed()
    
    # Left / Right Rotation Camera turn
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:  
        player_angle -= 0.04
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
        player_angle += 0.04
    
    # Forward Navigation (W or Up Arrow)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_x = player_x + math.cos(player_angle) * 0.06
        new_y = player_y + math.sin(player_angle) * 0.06
        if MAP[int(new_y)][int(new_x)] == 0:
            player_x, player_y = new_x, new_y
            
    # Backward Navigation (S or Down Arrow)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_x = player_x - math.cos(player_angle) * 0.06
        new_y = player_y - math.sin(player_angle) * 0.06
        if MAP[int(new_y)][int(new_x)] == 0:
            player_x, player_y = new_x, new_y
            
    # FIXED FLIGHT CONTROLS: R and F keys!
    if keys[pygame.K_r]: # R key makes you fly UP
        player_z += 6.0
    if keys[pygame.K_f]: # F key makes you fly DOWN
        player_z -= 6.0

    # --- GRAPHICS RENDERING LAYER ---
    horizon_shift = int(player_z)
    screen.fill((135, 206, 235)) 
    pygame.draw.rect(screen, (60, 60, 60), (0, (HEIGHT // 2) - horizon_shift, WIDTH, (HEIGHT // 2) + horizon_shift))

    # Raycasting View Loop
    start_angle = player_angle - HALF_FOV
    for ray in range(CASTED_RAYS):
        cur_angle = start_angle + ray * STEP_ANGLE
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)
        
        for depth in range(1, 200):
            dist = depth * 0.06
            target_x = player_x + cos_a * dist
            target_y = player_y + sin_a * dist
            
            if target_x < 0 or target_x >= MAP_SIZE or target_y < 0 or target_y >= MAP_SIZE:
                break
                
            block_type = MAP[int(target_y)][int(target_x)]
            if block_type > 0:
                dist *= math.cos(player_angle - cur_angle)
                wall_height = min(HEIGHT * 2, int(HEIGHT / (dist + 0.0001)))
                
                hit_x = target_x - int(target_x)
                hit_y = target_y - int(target_y)
                
                if abs(hit_y) < 0.05 or abs(hit_y) > 0.95:
                    texture_x = int(hit_x * TEX_SIZE)
                else:
                    texture_x = int(hit_y * TEX_SIZE)
                texture_x = max(0, min(TEX_SIZE - 1, texture_x))
                
                texture_slice = TEXTURES[block_type].subsurface(texture_x, 0, 1, TEX_SIZE)
                
                shadow = max(0, min(255, int(255 - (dist * 25))))
                shadow_surf = pygame.Surface((1, TEX_SIZE))
                shadow_surf.fill((0,0,0))
                shadow_surf.set_alpha(255 - shadow)
                
                final_slice = texture_slice.copy()
                final_slice.blit(shadow_surf, (0,0))
                
                scaled_slice = pygame.transform.scale(final_slice, (int(SCALE) + 1, wall_height))
                screen.blit(scaled_slice, (ray * SCALE, ((HEIGHT // 2) - (wall_height // 2)) - horizon_shift))
                break

    # --- INVENTORY OVERLAY DRAWING ---
    pygame.draw.rect(screen, (30, 30, 30), (140, HEIGHT - 65, 360, 55), border_radius=6)
    for i in range(4):
        bx = 160 + (i * 85)
        by = HEIGHT - 55
        border_color = (255, 215, 0) if i == selected_slot else (100, 100, 100)
        border_thickness = 4 if i == selected_slot else 1
        pygame.draw.rect(screen, border_color, (bx, by, 36, 36), border_thickness)
        
        block_id = inventory[i]
        icon_thumb = pygame.transform.scale(TEXTURES[block_id], (28, 28))
        screen.blit(icon_thumb, (bx + 4, by + 4))
        
        lbl = font.render(str(i+1), True, (200, 200, 200))
        screen.blit(lbl, (bx + 2, by - 16))

    # Crosshair
    pygame.draw.circle(screen, (255, 0, 0), (WIDTH // 2, HEIGHT // 2), 2)

    pygame.display.flip()
    clock.tick(120)

