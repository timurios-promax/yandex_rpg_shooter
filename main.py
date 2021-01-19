from datetime import datetime
import sqlite3

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


# initialising pygame, writing basement parameters
pygame.init()
screen_size = [400, 400]
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Dark Fantasy')
speed = 4
ammo = 30
mana = 120
tile_width = tile_height = 50
life_count = 40
enemy_life_count = 80
enemy_bullet_time = 50
bullet_time = 15
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
FPS = 50
radius = 200
coins = list()
step_state = 0
score = 0

# background, walls textures
tile_images = {
    'wall': load_image('walls.jpg'),
    'empty': load_image('grass.jpg'),
    'empty2': load_image('grass2.jpg')
}

# loading window icon, player's images, player's bullet texture, enemy's bullet texture, coin's image
icon = load_image('icon.jpg')
pygame.display.set_icon(icon)
player_image = load_image('down.png')
enemy_image = load_image('down_light.png')
bullet_image = load_image('dark_fireball.png')
enemy_bullet_image = load_image('light_blast.png')
coin_image = load_image('coin.png')

# loading sounds
bullet_sound = pygame.mixer.Sound(r'sounds\fireball.wav')
enemy_damge_sound = pygame.mixer.Sound(r'sounds\enemydamage.wav')
pygame.mixer.music.load(r'sounds\fonmusic.wav')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.3)
step_sound = [pygame.mixer.Sound(r'sounds\step' + str(i) + '.wav') for i in range(1, 10)]
coin_sound = pygame.mixer.Sound(r'sounds\coin.wav')
enemy_bullet_sound = pygame.mixer.Sound(r'sounds\burst.wav')
damage_sound = pygame.mixer.Sound(r'sounds\herodamage.wav')


# Tile class for walls and background
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        if tile_type == 'wall':
            self.add(walls)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


# Player's (Hero's) class
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

    def show_status(self):
        # showing HP
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.health) + ' HP', True, pygame.Color('red'))
        text_x = self.pos[0] + camera.dx
        text_y = self.pos[1] - 10 + camera.dy
        screen.blit(text, (text_x, text_y))

        # showing Mana Points
        font = pygame.font.Font(None, 30)
        text = font.render(str(kol_bul + all_bul) + '/' + str(mana) + ' MP', True, pygame.Color(100, 140, 255, 255))
        text_x = 10
        text_y = 370
        screen.blit(text, (text_x, text_y))

        # showing current ammo
        font = pygame.font.Font(None, 30)
        text = font.render(str(kol_bul) + '/' + str(ammo) + ' AMMO', True, pygame.Color(255, 255, 255, 255))
        text_x = 10
        text_y = 340
        screen.blit(text, (text_x, text_y))

        # showing score
        font = pygame.font.Font(None, 30)
        text = font.render(str(score).rjust(6, '0'), True, pygame.Color(255, 255, 255, 255))
        text_x = 320
        text_y = 10
        screen.blit(text, (text_x, text_y))


# Coin's class
class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(sprite_group)
        self.add(coins_group)
        self.image = coin_image
        self.health = 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 15)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.pos = (tile_width * pos_x + 15, tile_height * pos_y + 5)

    def taken(self):
        global score
        if pygame.sprite.spritecollideany(self, hero_group):
            coin_sound.play()
            score += 10
            self.kill()
            return True
        return False


# Enemy's class
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
        self.new_time = 0
        self.old_time = 0

    def move(self, x, y):
        camera.dx -= x - self.pos[0]
        camera.dy -= y - self.pos[1]
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

    def show_health(self):
        global score
        if self.health <= 0:
            score += 100
            self.kill()
            return True
        # showing enemy's hp
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.health) + ' HP', True, pygame.Color('red'))
        text_x = self.pos[0] + camera.dx
        text_y = self.pos[1] - 10 + camera.dy
        screen.blit(text, (text_x, text_y))

        if pygame.sprite.spritecollideany(self, bullet_group):
            # playing taking damage's sound
            enemy_damge_sound.play()
            self.health -= 20
        return False


# Camera class
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


# Hero's bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, finish_pos, life_count=25, bullet_time=15):
        super().__init__(sprite_group)
        self.add(bullet_group)
        bullet_sound.play()
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
        self.x_speed, self.y_speed = (self.finish_x - self.start_x) / bullet_time, (self.finish_y - self.start_y) / bullet_time

    def bullet_move(self):
        self.abs_pos[0] += self.x_speed
        self.abs_pos[1] += self.y_speed
        # colliding with walls
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        # colliding with enemy
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.kill()
            return
        for sprite in sprite_group:
            # applying bullet's movement to camera
            camera.apply(sprite)
        self.life_count -= 1
        if self.life_count <= 0:
            # killing bullet if it's life count (time of working) = 0
            self.kill()
            return


# Enemy bullet's class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, finish_pos, life_count=25, bullet_time=15):
        super().__init__(sprite_group)
        self.add(enemy_bullet_group)
        enemy_bullet_sound.play()
        self.start_x, self.start_y = start_pos
        self.start_y += 5
        self.abs_pos = [self.start_x, self.start_y]
        self.image = enemy_bullet_image
        self.rect = self.image.get_rect().move(
            self.start_x, self.start_y)
        self.life_count = life_count
        self.finish_pos = finish_pos
        self.finish_x, self.finish_y = finish_pos
        self.x_speed, self.y_speed = (self.finish_x - self.start_x) / bullet_time, (self.finish_y - self.start_y) / bullet_time

    def bullet_move(self):
        self.abs_pos[0] += self.x_speed
        self.abs_pos[1] += self.y_speed
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        for sprite in sprite_group:
            camera.apply(sprite)
        self.life_count -= 1
        if self.life_count <= 0:
            self.kill()
            return
        if pygame.sprite.spritecollideany(self, hero_group) and self.life_count > 0:
            damage_sound.play()
            hero.health -= 20
            self.kill()
            self.life_count = 0
            return


player = None
running = True
clock = pygame.time.Clock()

# creating sprite groups
sprite_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit


# start screen
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
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


# end screen
def end_screen():
    global score
    con = sqlite3.connect('records.db')
    cur = con.cursor()
    current_datetime = datetime.now()
    datee = str(current_datetime)
    cur.execute(f"INSERT INTO records (date, score) VALUES ('{datee}', {score})")
    con.commit()
    con.close()
    intro_text = ["                       Вы проиграли",
                  "",
                  "",
                  "Заработано: " + str(score) + ' очков']

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
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
                os.system('python main.py')
                return
        pygame.display.flip()
        clock.tick(FPS)


# level loading from map
def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for i in range(len(level_map)):
        level_map[i] = str(level_map[i])
    return level_map


# level generating
def generate_level(level):
    new_player, x, y = None, None, None
    enemies = list()
    global coins
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '%':
                Tile('empty2', x, y)
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
            elif level[y][x] == '*':
                Tile('empty', x, y)
                coins.append(Coin(x, y))
                d = list(level[y])
                d[x] = "."
                level[y] = d
    return new_player, x, y, enemies


def check(y1, x1):
    if level_map[y1 // tile_height][x1 // tile_width] == ".":
        return True


# hero's movement
def move(hero, movement):
    global step_state
    x, y = hero.pos
    step_sound[step_state].play()
    step_state = (step_state + 1) % 9
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


# random level generating
levels = [[str(random.randint(0, 3)) for i in range(3)] for j in range(3)]
level_map = load_level(map_file)
for i in range(len(levels)):
    for j in range(len(levels[0])):
        map = load_level('map' + str(i) + str(j) + levels[i][j] + '.map')
        for k in range(len(map)):
            for t in range(len(map[0])):
                if i < 1 and j < 1:
                    d = list(level_map[i * 8 + k])
                    d[j * 8 + t] = map[k][t]
                    level_map[i * 8 + k] = ''.join(d)
                else:
                    d = list(level_map[i * 8 + k + i * 4])
                    rand = random.randint(0, 20)
                    if rand == 10 and map[k][t] != '#':
                        d[j * 8 + t + j * 4] = '$'
                    elif rand == 20 and map[k][t] != '#':
                        d[j * 8 + t + j * 4] = '*'
                    else:
                        d[j * 8 + t + j * 4] = map[k][t]
                    level_map[i * 8 + k + i * 4] = ''.join(d)

start_screen()
camera = Camera()
hero, max_x, max_y, enemy_list = generate_level(level_map)
camera.update(hero)


# bullet's reloading
def reload():
    global all_bul, kol_bul, old_time
    old_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec + 1
    some_bulls = min(30 - kol_bul, abs(all_bul - kol_bul))
    kol_bul += some_bulls
    if kol_bul != 0:
        all_bul -= some_bulls


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                up_flag = 1
            elif event.key == pygame.K_s:
                down_flag = 1
            elif event.key == pygame.K_a:
                left_flag = 1
            elif event.key == pygame.K_d:
                right_flag = 1
            if event.key == pygame.K_r:
                reload()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                up_flag = 0
            if event.key == pygame.K_s:
                down_flag = 0
            if event.key == pygame.K_a:
                left_flag = 0
            if event.key == pygame.K_d:
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
        # reloading and shooting code
        if kol_bul > 0:
            new_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec
            if new_time - old_time > 0.3:
                bullets.append(Bullet(hero.pos, mouse_pos, life_count, bullet_time))
                kol_bul -= 1
                old_time = new_time
        else:
            reload()

    screen.fill(pygame.Color("black"))
    i = 0
    while i < len(bullets):
        # moving bullets
        bullets[i].bullet_move()
        if bullets[i].life_count < 0:
            del bullets[i]
            i -= 1
        i += 1
    i = 0
    while i < len(coins):
        # taking coins
        k = coins[i].taken()
        if k:
            del coins[i]
            i -= 1
        i += 1

    # drawing sprite groups
    sprite_group.draw(screen)
    hero_group.draw(screen)
    hero.show_status()
    enemy_group.draw(screen)

    i = 0
    while i < len(enemy_list):
        # showing enemy's health or killing them
        k = enemy_list[i].show_health()
        if k:
            del enemy_list[i]
            i -= 1
        i += 1

    # wrong, enemy's shooting
    for enemy in enemy_list:
        if ((hero.pos[0] - enemy.pos[0]) ** 2 + (hero.pos[1] - enemy.pos[1]) ** 2) ** 0.5 <= radius:
            enemy.new_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec
            if enemy.new_time - enemy.old_time > 0.8:
                bullets.append(EnemyBullet(enemy.pos, hero.pos, enemy_life_count, enemy_bullet_time))
                enemy.old_time = enemy.new_time

    if len(enemy_list) == 0 or hero.health <= 0:
        end_screen()

    clock.tick(30)
    pygame.display.flip()
pygame.quit()