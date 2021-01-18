import pygame
import os
import sys
import argparse
import random
import time

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
screen_size = [400, 400]
screen = pygame.display.set_mode(screen_size)
speed = 3
FPS = 50

tile_images = {
    'wall': load_image('walls.jpg'),
    'empty': load_image('grass.jpg')
}
player_image = load_image('down.png')
enemy_image = load_image('down_light.png')
bullet_image = load_image('dark_fireball.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        if tile_type == 'wall':
            self.add(walls)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.health = 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, x, y):
        camera.dx -= x - self.pos[0]
        camera.dy -= y - self.pos[1]
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

    def show_health(self):
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.health), True, pygame.Color('red'))
        text_x = self.pos[0] + 5 + camera.dx
        text_y = self.pos[1] - 10 + camera.dy
        screen.blit(text, (text_x, text_y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(sprite_group)
        self.add(enemy_group)
        self.image = enemy_image
        self.health = 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 15)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.pos = (tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, x, y):
        camera.dx -= x - self.pos[0]
        camera.dy -= y - self.pos[1]
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

    def show_health(self):
        if self.health <= 0:
            self.kill()
            return True
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.health), True, pygame.Color('red'))
        text_x = self.pos[0] + camera.dx
        text_y = self.pos[1] - 5 + camera.dy
        screen.blit(text, (text_x, text_y))
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.health -= 20
        return False


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, finish_pos, life_count=100, bullet_speed=10):
        super().__init__(sprite_group)
        self.add(bullet_group)
        self.start_x, self.start_y = start_pos
        self.start_y += 5
        self.abs_pos = [self.start_x, self.start_y]
        self.image = bullet_image
        self.rect = self.image.get_rect().move(
            self.start_x, self.start_y)
        self.life_count = life_count
        self.finish_pos = finish_pos
        self.finish_x, self.finish_y = finish_pos
        self.finish_x += hero.pos[0]
        self.finish_x -= (50 * 3 + 15)
        self.finish_y += hero.pos[1]
        self.finish_y -= (50 * 3 + 5)
        self.x_speed, self.y_speed = (self.finish_x - self.start_x) / bullet_speed, (self.finish_y - self.start_y) / bullet_speed

    def bullet_move(self):
        self.abs_pos[0] += self.x_speed
        self.abs_pos[1] += self.y_speed
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.kill()
            return
        for sprite in sprite_group:
            camera.apply(sprite)
        self.life_count -= 1
        if self.life_count <= 0:
            self.kill()
            return



player = None
running = True
clock = pygame.time.Clock()
sprite_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    intro_text = ["                       Dark fantasy", "",
                  "",
                  "",
                  "",
                  "",
                  "",
                  "Сделали: Таласбаев Тимур",
                  "Камысбаев Амир",
                  "Новак Андрей"]

    fon = pygame.transform.scale(load_image('main_window.gif'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('dark grey'))
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
    level_map = list()
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for i in range(len(level_map)):
        level_map[i] = str(level_map[i])
    max_width = len(level_map[0])
    return level_map


def generate_level(level):
    new_player, x, y = None, None, None
    enemies = list()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                d = list(level[y])
                d[x] = "."
                level[y] = d
            elif level[y][x] == '$':
                Tile('empty', x, y)
                enemies.append(Enemy(x, y))
                d = list(level[y])
                d[x] = "."
                level[y] = d
    return new_player, x, y, enemies

def check(y1, x1):
    if level_map[y1 // tile_height][x1 // tile_width] == ".":
        return True


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y - speed > 0:
            if not pygame.sprite.spritecollideany(hero, walls):
                hero.move(x, y - speed)
                k = 0
                hero.image = load_image('up.png')
                while pygame.sprite.spritecollideany(hero, walls):
                    hero.move(x, y + k)
                    k += 1

    elif movement == "down":
        if y + speed < len(level_map) * tile_height:
            if not pygame.sprite.spritecollideany(hero, walls):
                hero.move(x, y + speed)
                k = 0
                hero.image = load_image('down.png')
                while pygame.sprite.spritecollideany(hero, walls):
                    hero.move(x, y - k)
                    k += 1

    elif movement == "left":
        if x - speed > 0:
            if not pygame.sprite.spritecollideany(hero, walls):
                if not pygame.sprite.spritecollideany(hero, walls):
                    hero.move(x - speed, y)
                    k = 0
                    hero.image = load_image('left.png')
                    while pygame.sprite.spritecollideany(hero, walls):
                        hero.move(x + k, y)
                        k += 1

    elif movement == "right":
        if x + speed < len(level_map[1]) * tile_width:
            if not pygame.sprite.spritecollideany(hero, walls):
                hero.move(x + speed, y)
                k = 0
                hero.image = load_image('right.png')
                while pygame.sprite.spritecollideany(hero, walls):
                    hero.move(x - k, y)
                    k += 1

levels = [[str(random.randint(0, 3)) for i in range(3)] for j in range(3)]
level_map = load_level(map_file)
for i in range(len(levels)):
    for j in range(len(levels[0])):
        map = load_level('map' + str(i) + str(j) + levels[i][j] + '.map')
        for k in range(len(map)):
            for t in range(len(map[0])):
                if  i < 1 and j < 1:
                    d = list(level_map[i * 8 + k])
                    d[j * 8 + t] = map[k][t]
                    level_map[i * 8 + k] = ''.join(d)
                else:
                    d = list(level_map[i * 8 + k + i * 4])
                    rand = random.randint(0, 20)
                    if rand == 10 and map[k][t] != '#':
                        d[j * 8 + t + j * 4] = '$'
                    else:
                        d[j * 8 + t + j * 4] = map[k][t]
                    level_map[i * 8 + k + i * 4] = ''.join(d)

for i in level_map:
    print(i)

bullet_speed = 1

start_screen()
camera = Camera()
hero, max_x, max_y, enemy_list = generate_level(level_map)
camera.update(hero)
up_flag = 0
down_flag = 0
left_flag = 0
right_flag = 0
bullet_flag = 0
bullets = []
kol_bul = 30
all_bul = 90
weapon_speed = 5
old_time = 0


def reload():
    global all_bul, kol_bul, old_time
    old_time = time.localtime().tm_sec + 1
    some_bulls = min(30 - kol_bul, abs(all_bul - kol_bul))
    kol_bul += some_bulls
    if kol_bul != 0:
        all_bul -= some_bulls


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
            if event.key == pygame.K_r:
                reload()
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
                bullet_flag = 1
                mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                bullet_flag = 0
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos

    if up_flag:
        move(hero, "up")
    if down_flag:
        move(hero, "down")
    if left_flag:
        move(hero, "left")
    if right_flag:
        move(hero, "right")
    if bullet_flag:
        if kol_bul > 0:
            new_time = time.localtime().tm_sec
            if new_time - old_time > 0.3:
                bullets.append(Bullet(hero.pos, mouse_pos))
                kol_bul -= 1
                old_time = new_time
        else:
            reload()

    screen.fill(pygame.Color("black"))
    i = 0
    while i < len(bullets):
        bullets[i].bullet_move()
        if bullets[i].life_count < 0:
            del bullets[i]
            i -= 1
        i += 1
    sprite_group.draw(screen)
    hero_group.draw(screen)
    hero.show_health()
    enemy_group.draw(screen)
    i = 0
    while i < len(enemy_list):
        k = enemy_list[i].show_health()
        if k:
            del enemy_list[i]
            i -= 1
        i += 1

    if len(enemy_list) == 0:
        pygame.quit()

    clock.tick(30)
    pygame.display.flip()
pygame.quit()