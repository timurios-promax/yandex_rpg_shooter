import pygame
import os
import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('img', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (400, 400)
screen = pygame.display.set_mode(screen_size)
speed = 3
FPS = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, x, y):
        camera.dx -= x - self.pos[0]
        camera.dy -= y - self.pos[1]
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


player = None
running = True
clock = pygame.time.Clock()
sprite_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "",
                  "Камера"]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y - speed > 0 and level_map[(y - speed) // tile_height][x // tile_width] == ".":
            hero.move(x, y - speed)
        elif y - speed > 0:
            if y - speed > (y // tile_height - 1) * tile_height:
                hero.move(x, y - speed)
    elif movement == "down":
        if y < (max_y * tile_height - speed) and level_map[(y + speed) // tile_height][x // tile_width] == ".":
            hero.move(x, y + speed)
        elif y < (max_y * tile_height - speed):
            if y + speed < (y // tile_height + 1) * tile_height:
                hero.move(x, y + speed)
    elif movement == "left":
        if x - speed > 0 and level_map[y // tile_height][(x - speed) // tile_width] == ".":
            hero.move(x - speed, y)
        elif x - speed > 0:
            if x - speed > (x // tile_width - 1) * tile_width:
                hero.move(x - speed, y)
    elif movement == "right":
        if x < (max_x * tile_width - speed) and level_map[y // tile_height][(x + speed) // tile_width] == ".":
            hero.move(x + speed, y)
        elif x < (max_x * tile_width - speed):
            if x + speed < (x // tile_width + 1) * tile_width:
                hero.move(x + speed, y)


start_screen()
camera = Camera()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera.update(hero)
up_flag = 0
down_flag = 0
left_flag = 0
right_flag = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                up_flag = 1
            elif event.key == pygame.K_DOWN:
                down_flag = 1
            elif event.key == pygame.K_LEFT:
                left_flag = 1
            elif event.key == pygame.K_RIGHT:
                right_flag = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up_flag = 0
            if event.key == pygame.K_DOWN:
                down_flag = 0
            if event.key == pygame.K_LEFT:
                left_flag = 0
            if event.key == pygame.K_RIGHT:
                right_flag = 0
    if up_flag:
        move(hero, "up")
    if down_flag:
        move(hero, "down")
    if left_flag:
        move(hero, "left")
    if right_flag:
        move(hero, "right")
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()