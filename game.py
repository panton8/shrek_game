import pygame
import os
import random
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shrek_game')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 28
screen_scroll = 0
bg_scroll = 0
level = 1

# define player action variables
moving_left = False
moving_right = False
shoot = False

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'images/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# load images for background
view_img = pygame.image.load('images/BackGround/View.png').convert_alpha()
tree1_img = pygame.image.load('images/BackGround/Tree1.png').convert_alpha()
tree2_img = pygame.image.load('images/BackGround/Tree2.png').convert_alpha()
swamp_img = pygame.image.load('images/BackGround/Swamp.png').convert_alpha()
grass_img = pygame.image.load('images/BackGround/Grass.png').convert_alpha()


# load images
stone_img = pygame.image.load('images/Icons/stone.png').convert_alpha()
arrow_img = pygame.image.load('images/Icons/arrow.png').convert_alpha()

# pick up boxes
heal_box_img = pygame.image.load('images/Icons/health.png').convert_alpha()
coin_box_img = pygame.image.load('images/Icons/coin.png').convert_alpha()
ammo_box_img = pygame.image.load('images/Icons/ammo.png').convert_alpha()

item_boxes = {
    'Health': heal_box_img,
    'Ammo': ammo_box_img,
    'Coin': coin_box_img,
}

# define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    screen.blit(view_img, (0, 0))
    screen.blit(tree1_img, (0, SCREEN_HEIGHT - tree1_img.get_height() - 100))
    screen.blit(tree2_img, (0, SCREEN_HEIGHT - tree2_img.get_height() - 85))
    screen.blit(swamp_img, (0, SCREEN_HEIGHT - swamp_img.get_height() - 50))
    screen.blit(grass_img, (0, SCREEN_HEIGHT - grass_img.get_height() - 40))


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type

        if char_type == 'Player':
            self.weapon_image = stone_img
        else:
            self.weapon_image = arrow_img

        self.speed = speed
        self.coins = 0
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the characters
        animation_types = ['Idle', 'Run', 'Jump', 'Shoot', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        # jump
        if self.jump is True and self.in_air is False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground,i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 50
            if self.char_type == 'Player':
                stone_object = ShootingSubject(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.weapon_image)
                stone_group.add(stone_object)
            else:
                arrow_object = ShootingSubject(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.weapon_image)
                arrow_group.add(arrow_object)
            # reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and shrek.alive:
            if self.idling is False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the AI in near the player
            if self.vision.colliderect(shrek.rect):
                # stop running and face the player
                self.update_action(3)   # 3: shoot
                # shoot
                self.shoot()
            else:
                if self.idling is False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        elif not self.alive:
            self.update_action(4)   # 4: death
        else:
            self.update_action(0)  # 0: idle

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 115
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 16:
                        self.obstacle_list.append(tile_data)
                    elif tile == 17:    # create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:    # create coin
                        item_box = ItemBox('Coin', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:    # create health_point
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:    # create a player
                        shrek = Character('Player', x * TILE_SIZE, y * TILE_SIZE, 1.15, 3.75, 20)
                        health_bar = HealthBar(10, 10, shrek.health, shrek.health)
                    elif tile == 21:    # create enemy
                        enemy = Character('Enemy', x * TILE_SIZE, y * TILE_SIZE, 1.15, 1.5, 20)
                        enemy_group.add(enemy)
                    elif tile == 22:
                        spikes = Spikes(img, x * TILE_SIZE, y * TILE_SIZE)
                        spikes_group.add(spikes)
                    elif tile >= 23 and tile <= 26:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 27:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return shrek, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Spikes(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, shrek):
            # check what kind of box it was
            if self.item_type == 'Health':
                shrek.health += 25
                if shrek.health > shrek.max_health:
                    shrek.health = shrek.max_health
            elif self.item_type == 'Coin':
                shrek.coins += 1
            elif self.item_type == 'Ammo':
                shrek.ammo += 5


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class ShootingSubject(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image_weapon):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = image_weapon
        self.rect = image_weapon.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move stone
        self.rect.x += self.direction * self.speed
        # check if stone has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(shrek, arrow_group, False):
            if shrek.alive:
                shrek.health -= 20
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, stone_group, False):
                if enemy.alive:
                    enemy.health -= 50
                    self.kill()


# create sprite groups
enemy_group = pygame.sprite.Group()
stone_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# load in level data and create world
with open(f'level{level - 1}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
shrek, health_bar = world.process_data(world_data)


run = True
while run:
    clock.tick(FPS)

    # update background
    draw_bg()

    # draw world map
    world.draw()

    # show player health
    health_bar.draw(shrek.health)

    # show ammo
    screen.blit(stone_img, (5, 37.5))
    draw_text(f': {shrek.ammo}', font, WHITE, 25, 40)
    screen.blit(coin_box_img, (3, 67.5))
    draw_text(f': {shrek.coins}', font, WHITE, 25, 65)

    shrek.update()
    shrek.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # update and draw groups
    stone_group.update()
    arrow_group.update()
    stone_group.draw(screen)
    arrow_group.draw(screen)

    decoration_group.update()
    exit_group.update()
    spikes_group.update()
    exit_group.draw(screen)
    decoration_group.draw(screen)
    spikes_group.draw(screen)

    item_box_group.update()
    item_box_group.draw(screen)

    # update player action
    if shrek.alive:
        # shoot stones
        if shoot:
            shrek.shoot()
            shrek.update_action(3)  # 3: shoot
        elif shrek.in_air:
            shrek.update_action(2)  # 2: jump
        elif moving_left or moving_right:
            shrek.update_action(1)  # 1: run
        else:
            shrek.update_action(0)  # 0: idle
        shrek.move(moving_left, moving_right)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboards presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and shrek.alive:
                shrek.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboards button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
