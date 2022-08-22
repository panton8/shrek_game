import pygame
import os

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
TILE_SIZE = 40

# define player action variables
moving_left = False
moving_right = False
shoot = False

# load images
stone_img = pygame.image.load('images/Icons/stone.png').convert_alpha()
arrow_img = pygame.image.load('images/Icons/arrow.png').convert_alpha()

# pick up boxes
heal_box_img = pygame.image.load('images/Icons/health.png').convert_alpha()
coin_box_img = pygame.image.load('images/Icons/coin.png').convert_alpha()
ammo_box_img = pygame.image.load('images/Icons/ammo.png').convert_alpha()
spikes_box_img = pygame.image.load('images/Icons/spikes.png')
item_boxes = {
    'Health': heal_box_img,
    'Ammo': ammo_box_img,
    'Coin': coin_box_img,
    'Spikes': spikes_box_img
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
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


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
        temp_list = []
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

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
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
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 50
            if self.char_type == 'Player':
                stone_object = ShootingSubject(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.weapon_image)
                stone_group.add(stone_object)
            else:
                arrow_object = ShootingSubject(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, self.weapon_image)
                arrow_group.add(arrow_object)
            # reduce ammo
            self.ammo -= 1

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
            elif self.item_type == 'Spikes':
                shrek.health = 0
            # delete the item box
            if self.item_type != 'Spikes':
                self.kill()


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
#shooting_group = pygame.sprite.Group()
stone_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()


shrek = Character('Player', 200, 200, 1.5, 4, 20)
health_bar = HealthBar(10, 10, shrek.health, shrek.health)

enemy = Character('Enemy', 400, 200, 1.5, 4, 20)
enemy2 = Character('Enemy', 300, 300, 1.5, 4, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)

# temp - create item box
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box1 = ItemBox('Spikes', 350, 260)
item_box_group.add(item_box1)

run = True
while run:

    clock.tick(FPS)

    draw_bg()
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
        enemy.update()
        enemy.draw()

    # update and draw groups
    stone_group.update()
    arrow_group.update()

    stone_group.draw(screen)
    arrow_group.draw(screen)

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
