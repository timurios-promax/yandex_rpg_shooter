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


class Bullet:
    def __init__(self, start_pos, finish_pos, life_count=20, bullet_speed=20):
        self.life_count = life_count
        self.finish_pos = finish_pos
        self.finish_x, self.finish_y = finish_pos
        self.start_x, self.start_y = start_pos
        self.x_speed, self.y_speed = (self.finish_x - self.start_x) / bullet_speed, (self.finish_y - self.start_y) / bullet_speed

    def bullet_move(self):
        if self.finish_x > self.start_x:
            self.start_x += self.x_speed
        elif self.finish_x < self.start_x:
            self.start_x -= 1
        if self.finish_y > self.start_y:
            self.start_y += self.y_speed
        elif self.finish_y < self.start_y:
            self.start_y -= 1
        circle_pos = (self.start_x, self.start_y)
        pygame.draw.circle(screen, pygame.Color('red'), circle_pos, 2, 2)
        if circle_pos == self.finish_pos:
            self.life_count = 0
        if self.finish_x < self.start_x + self.x_speed or self.finish_y < self.start_y + self.y_speed:
            self.life_count = 0
        self.life_count -= 1





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

def check(y1, x1):
    if level_map[y1 // tile_height][x1 // tile_width] == ".":
        return True


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y - speed > 0 and level_map[(y - speed) // tile_height][x // tile_width] == ".":
            hero.move(x, y - speed)

    elif movement == "down":
        if y + speed < len(level_map) * tile_height and level_map[(y + speed) // tile_height][x // tile_width] == ".":
            hero.move(x, y + speed)

    elif movement == "left":
        if x - speed > 0 and level_map[y // tile_height][(x - speed) // tile_width] == ".":
            hero.move(x - speed, y)

    elif movement == "right":
        if x + speed < len(level_map[1]) * tile_width and level_map[y // tile_height][(x + speed) // tile_width] == ".":
            hero.move(x + speed, y)

bullet_speed = 1

def shoot(shoot_x, shoot_y):
    x1, y1 = hero.pos
    x_speed, y_speed = abs(shoot_x - x1) / bullet_speed, abs(shoot_y - y1) // bullet_speed
    if shoot_x > x1:
        x1 += 1
    elif shoot_x < x1:
        x1 -= 1
    if shoot_y > y1:
        y1 += 1
    elif shoot_y < y1:
        y1 -= 1
    circle_pos = (x1, y1)
    pygame.draw.circle(screen, pygame.Color('red'), circle_pos, 2, 2)


start_screen()
camera = Camera()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera.update(hero)
up_flag = 0
down_flag = 0
left_flag = 0
right_flag = 0
bullets = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                up_flag = 1
            elif event.key == pygame.K_DOWN:
                down_flag = 1
            elif event.key == pygame.K_LEFT:
                left_flag = 1
            elif event.key == pygame.K_RIGHT:
                right_flag = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up_flag = 0
            if event.key == pygame.K_DOWN:
                down_flag = 0
            if event.key == pygame.K_LEFT:
                left_flag = 0
            if event.key == pygame.K_RIGHT:
                right_flag = 0
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                bullets.append(Bullet(hero.pos, event.pos))


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
    for i in range(len(bullets)):
        bullets[i].bullet_move()
        if bullets[i].life_count == 0:
            del bullets[i]
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
