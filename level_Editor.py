import button
from button import*
import csv

pygame.init()

clock = pygame.time.Clock()
FPS = 60
# game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Lever Editor')

# define game variables
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 28
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# load images
view_img = pygame.image.load('images/BackGround/View.png').convert_alpha()
tree1_img = pygame.image.load('images/BackGround/Tree1.png').convert_alpha()
tree2_img = pygame.image.load('images/BackGround/Tree2.png').convert_alpha()
swamp_img = pygame.image.load('images/BackGround/Swamp.png').convert_alpha()
grass_img = pygame.image.load('images/BackGround/Grass.png').convert_alpha()

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'images/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('images/Buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('images/Buttons/load_btn.png').convert_alpha()

# define colors
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

# define font
font = pygame.font.SysFont('Futura', 30)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

# create ground
for tile in range(0, MAX_COLS):
    world_data[ROWS-1][tile] = 0


# create function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# create function for drawing background
def draw_bg():
    screen.fill(GREEN)
    width = view_img.get_width()
    for x in range(4):
        screen.blit(view_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(tree1_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(tree2_img, ((x * width) - scroll * 0.6, 0))
        screen.blit(swamp_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - swamp_img.get_height() - 50))
        screen.blit(grass_img, ((x * width) - scroll * 0.65, SCREEN_HEIGHT - grass_img.get_height() - 40))


# create function for drawing grid
def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for r in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, r * TILE_SIZE), (SCREEN_WIDTH, r * TILE_SIZE))


# function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))


# create buttons
save_button = button.Button(SCREEN_WIDTH // 3, SCREEN_HEIGHT + LOWER_MARGIN - 45, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 3 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 45, load_img, 1)

# make a button list
button_list = []
button_col = 0
button_row = 0

for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 25, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 4:
        button_row += 1
        button_col = 0


run = True

while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()
    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 65)

    # save and load data
    if save_button.draw(screen):
        # save level data
        with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for row in world_data:
                writer.writerow(row)

    if load_button.draw(screen):
        # load in level data
        # reset scroll back to the start of the level
        scroll = 0
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    # draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # choose a tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    # highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 4)

    # scroll the map
    if scroll_left is True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right is True and scroll < (MAX_COLS * TILE_SIZE) - swamp_img.get_width():
        scroll += 5 * scroll_speed

    # add new tiles to screen
    # get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    # check that the coordinates are within the tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        # update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
