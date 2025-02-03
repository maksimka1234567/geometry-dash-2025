# Импортирование всех необходимых модулей и библиотек
import pygame
import os
import sys

# Инициализация Pygame
pygame.init()


# Функция для загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))  # Берем цвет из верхнего левого пикселя
        image = image.convert()  # Важно! Вызывать convert() ПЕРЕД set_colorkey()
        image.set_colorkey(colorkey)

    else:
        image = image.convert_alpha()
    return image


# ФПС, время и группы спрайтов для каждого типа объектов
FPS = 100
clock = pygame.time.Clock()
spikes = pygame.sprite.Group()
cube_portals = pygame.sprite.Group()
ufo_portals = pygame.sprite.Group()
ball_portals = pygame.sprite.Group()
platforms = pygame.sprite.Group()
trampolines = pygame.sprite.Group()
spheres = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()

flag = False  # флаг для проверки того, открыт ли один из уровней
flag1 = False  # флаг для проверки того, находится ли персонаж на платформе
flag2 = False  # флаг для того, чтобы звуковые эффекты в случае поражения или прохождения уровня воспроизводились только один раз
game_over = False  # флаг для проверки того, проиграл ли игрок
down = True  # флаг для отслеживания гравитации шарика
menu = False  # флаг для проверки того, открыто ли меню
congratulations = False  # флаг для проверки того, прошёл ли игрок уровень


# Функция для остановки работы
def terminate():
    pygame.quit()
    sys.exit()


# Инициализация игры
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash")
screen.fill("black")
is_jumping = False
jump_start = False


# Класс для персонажа "кубик"
class Cube(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):  # конструктор
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('Cube352.jpg'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.gravity = 0.5
        self.angle = 0
        self.original_image = self.image
        self.mask = pygame.mask.from_surface(self.image)  # Маска для кубика

    def update(self):  # обновление кубика
        global game_over
        global flag1
        # Вертикальное движение (прыжок и гравитация)
        if self.is_jumping or self.vy != 0:
            self.vy += self.gravity
            self.rect.y += self.vy
            # Вращение
            self.angle = (self.angle + 5) % 360
            self.image = pygame.transform.rotate(self.original_image, 180 - self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform:
                self.rect.bottom = landing_platform.rect.top + 5
                flag1 = True
                self.vy = 0
                self.is_jumping = False
                # Коррекция угла для приземления на сторону
                closest_angle = round(self.angle / 90) * 90
                self.angle = closest_angle
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
            elif self.rect.y >= HEIGHT - 50:
                self.rect.y = HEIGHT - 50
                self.vy = 0
                self.is_jumping = False
                # Коррекция угла для приземления на сторону
                closest_angle = round(self.angle / 90) * 90
                self.angle = closest_angle
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
                self.rect.y = HEIGHT - 50

    def jump(self):  # функция прыжка
        if not self.is_jumping:
            self.is_jumping = True
            if pygame.sprite.spritecollideany(self, trampolines, collided=pygame.sprite.collide_mask):
                self.vy = -15
            else:
                self.vy = -10

    def check_landing(self):  # функция для проверки приземления кубика
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0:  # Если падает вниз и касается платформы
                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Ufo(pygame.sprite.Sprite):  # класс для персонажа "НЛО"
    def __init__(self, pos_x, pos_y):  # конструктор
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('UFO057.png'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.mask = pygame.mask.from_surface(self.image)  # Маска для НЛО

    def update(self):  # обновление
        global game_over
        global flag1
        # Вертикальное движение (прыжок и гравитация)
        if self.is_jumping or self.vy != 0:
            self.vy += 0.3
            self.rect.y += self.vy
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform:
                self.rect.bottom = landing_platform.rect.top + 5
                flag1 = True
                self.vy = 0
                self.is_jumping = False
            elif self.rect.y >= HEIGHT - 50:
                self.rect.y = HEIGHT - 50
                self.vy = 0
                self.is_jumping = False
            elif self.rect.y <= 0:
                self.rect.y = 0
                self.vy = 0.2

    def jump(self):  # прыжок
        self.is_jumping = True
        if pygame.sprite.spritecollideany(self, trampolines, collided=pygame.sprite.collide_mask):
            self.vy = -10
        else:
            self.vy = -7

    def check_landing(self):  # проверка приземления
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0:  # Если падает вниз и касается платформы
                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Ball(pygame.sprite.Sprite):  # класс для персонажа "шарик"
    def __init__(self, pos_x, pos_y):  # конструктор
        super().__init__(players, all_sprites)
        self.image = pygame.transform.scale(load_image('Ball33.jpg'), (50, 50))
        self.rect = self.image.get_rect()
        self.vy = 0
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.is_jumping = False
        self.mask = pygame.mask.from_surface(self.image)  # Маска для шарика
        self.original_image = self.image
        self.angle = 0

    def update(self):  # обновление
        global game_over
        global flag1
        global down
        # Вращение
        self.angle = (self.angle + 3) % 360
        self.image = pygame.transform.rotate(self.original_image, 180 - self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.vy
        if self.is_jumping or self.vy != 0:
            flag1 = False
            if self.is_jumping:
                if down:
                    self.vy = -5
                else:
                    self.vy = 5
            # Проверка приземления в случае наличия платформ
            landing_platform = self.check_landing()
            if landing_platform and self.vy != 0:
                if not down:
                    self.rect.y = landing_platform.rect.y - 50
                    flag1 = True
                    down = True
                else:
                    self.rect.y = landing_platform.rect.y + 40
                    flag1 = True
                    down = False
                self.vy = 0
                self.is_jumping = False
            if self.rect.y <= -15:
                down = False
                flag1 = False
                self.is_jumping = False
                self.vy = 0
                self.rect.y = -5
            elif self.rect.y >= HEIGHT - 40:
                flag1 = False
                self.is_jumping = False
                self.vy = 0
                self.rect.y = HEIGHT - 50
                down = True

    def jump(self):  # прыжок
        if not self.is_jumping:
            self.is_jumping = True

    def check_landing(self):  # приземление сверху или снизу (шарик - персонаж, способный менять гравитацию)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vy >= 0 and self.rect.y < platform.rect.y and not down and not flag1:  # Если падает вниз и касается платформы

                    return platform  # Возвращаем платформу
                elif self.vy <= 0 and self.rect.y > platform.rect.y and down and not flag1:  # Если летит вверх и касается платформы

                    return platform  # Возвращаем платформу
        return None  # Если приземляться некуда


class Backgrounds(pygame.sprite.Sprite):  # фон для уровней
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('backgrounds1.png'), (WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


class Trampoline(
    pygame.sprite.Sprite):  # батут - объект, реализованный для кубика, кубик будет самостоятельно подпрыгивать при столкновении с батутом
    def __init__(self, pos_x, pos_y):
        super().__init__(trampolines, all_sprites)
        self.image = pygame.transform.scale(load_image('YellowPad.png'), (50, 20))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y + 30)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(
            self):  # обновление - геймплей заключается в том, что все объекты движутся налево, а персонаж взаимодействует с ними, фактически находясь на месте
        self.rect.x -= self.vx


end_blocks = pygame.sprite.Group()  # группа спрайтов для блоков в конце уровня, чтобы была возможность "пройти" уровень


class End(pygame.sprite.Sprite):  # класс блоков в конце
    def __init__(self, pos_x, pos_y):
        super().__init__(end_blocks, all_sprites)
        self.image = pygame.transform.scale(load_image('EndBlock.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5

    def update(self):
        self.rect.x -= self.vx


class Sphere(
    pygame.sprite.Sprite):  # сфера - объект, реализованный для кубика, кубик будет подпрыгивать в воздухе при столкновении со сферой, если во время этого столкновения будет нажата кнопка "вверх"
    def __init__(self, pos_x, pos_y):
        super().__init__(spheres, all_sprites)
        self.image = pygame.transform.scale(load_image('YellowSphere.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


def load_level(filename):  # функция для загрузки карты уровня из текстового файла
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Spike(pygame.sprite.Sprite):  # класс для шипов - любой персонаж проигрывает при столкновении с ними
    def __init__(self, pos_x, pos_y):
        super().__init__(spikes, all_sprites)
        self.image = pygame.transform.scale(load_image('RegularSpike03.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class CubePortal(pygame.sprite.Sprite):  # портал для превращения в кубик
    def __init__(self, pos_x, pos_y):
        super().__init__(cube_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('CubePortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class UfoPortal(pygame.sprite.Sprite):  # портал для превращения в НЛО
    def __init__(self, pos_x, pos_y):
        super().__init__(ufo_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('UFOPortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class BallPortal(pygame.sprite.Sprite):  # портал для превращения в шарик
    def __init__(self, pos_x, pos_y):
        super().__init__(ball_portals, all_sprites)
        self.image = pygame.transform.scale(load_image('BallPortalLabelled.png'), (75, 150))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y - 100)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


class Platform(pygame.sprite.Sprite):  # платформа (блок)
    def __init__(self, pos_x, pos_y):
        super().__init__(platforms, all_sprites)
        self.image = pygame.transform.scale(load_image('RegularBlock01.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            50 * pos_x, 50 * pos_y)
        self.vx = 5
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.vx


def generate_level(level):  # отрисовка уровня из текстового файла
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '^' or level[y][x] == 'v':
                a = Spike(x, y)
                if level[y][x] == 'v':
                    a.image = pygame.transform.rotate(a.image, 180)
            elif level[y][x] == '-':
                Platform(x, y)
            elif level[y][x] == '_':
                Trampoline(x, y)
            elif level[y][x] == '*':
                Sphere(x, y)
            elif level[y][x] == '0':
                CubePortal(x, y)
            elif level[y][x] == '1':
                UfoPortal(x, y)
            elif level[y][x] == '2':
                BallPortal(x, y)
            elif level[y][x] == '3':
                End(x, y)
    # вернем игрока, а также размер поля в клетках
    return x, y


class Button:  # кнопка для открытия одного из уровней
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pressed = False  # Флаг, указывающий, нажата ли кнопка

    def draw(self, screen):  # отрисовка кнопки
        screen.blit(self.image, self.rect)


# кнопки для каждого из уровней в меню игры
button1 = Button(15, 15, pygame.transform.scale(load_image("easy.png"), (380, 95)))
button2 = Button(400, 15, pygame.transform.scale(load_image("normal.png"), (380, 95)))

button3 = Button(15, 235, pygame.transform.scale(load_image("hard.png"), (380, 95)))
button4 = Button(400, 235, pygame.transform.scale(load_image("harder.png"), (380, 95)))
button5 = Button(15, 450, pygame.transform.scale(load_image("insane.png"), (380, 95)))
button6 = Button(400, 450, pygame.transform.scale(load_image("demon.png"), (380, 95)))


def start_screen():  # экран
    global flag
    global flag1
    global flag2
    global game_over
    global down
    global menu
    global congratulations
    player = None  # текущий персонаж
    fon = pygame.transform.scale(load_image('maxresdefault.jpg'), (WIDTH, HEIGHT))  # отрисовка заставки в начале игры
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu and not flag:  # меню уровней
                    # проверка того, какая кнопка нажата и какой уровень соответственно нужно загружать
                    if 15 <= event.pos[0] <= 395 and 15 <= event.pos[1] <= 110:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 50)
                        generate_level(load_level('level1.txt'))
                        flag1 = True
                        pygame.mixer.music.load('easy.mp3')  # музыка для каждого из уровней своя
                        pygame.mixer.music.play()
                        flag2 = False
                    elif 400 <= event.pos[0] <= 780 and 15 <= event.pos[1] <= 110:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 50)
                        generate_level(load_level('level2.txt'))
                        flag1 = True
                        pygame.mixer.music.load('normal.mp3')
                        pygame.mixer.music.play()
                        flag2 = False
                    elif 15 <= event.pos[0] <= 395 and 235 <= event.pos[1] <= 330:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 50)
                        generate_level(load_level('level3.txt'))
                        flag1 = True
                        player.is_jumping = False
                        pygame.mixer.music.load('hard.mp3')
                        pygame.mixer.music.play()
                        flag2 = False
                    elif 400 <= event.pos[0] <= 780 and 235 <= event.pos[1] <= 330:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 50)
                        generate_level(load_level('level4.txt'))
                        flag1 = True
                        pygame.mixer.music.load('harder.mp3')
                        pygame.mixer.music.play()
                        flag2 = False
                    elif 15 <= event.pos[0] <= 395 and 450 <= event.pos[1] <= 545:
                        Backgrounds()
                        flag = True
                        player = Ball(200, HEIGHT - 50)
                        player.is_jumping = False
                        player.vy = 0
                        generate_level(load_level('level5.txt'))
                        flag1 = False
                        down = True
                        pygame.mixer.music.load('insane.mp3')
                        pygame.mixer.music.play()
                        flag2 = False
                    elif 400 <= event.pos[0] <= 780 and 450 <= event.pos[1] <= 545:
                        Backgrounds()
                        flag = True
                        player = Cube(200, HEIGHT - 50)
                        generate_level(load_level('level6.txt'))
                        flag1 = False
                        player.is_jumping = False
                        pygame.mixer.music.load('demon.mp3')
                        pygame.mixer.music.play()
                        flag2 = False
                elif not menu:
                    menu = True  # открытие меню после заставки
                # начинаем игру
                if game_over or congratulations:
                    flag = False
                    game_over = False
                    congratulations = False
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)  # чтобы персонажи не дублировались, когда мы открываем новый уровень
                    for sprite in all_sprites:
                        sprite.rect.x = 0
                        sprite.rect.y = 0
            if event.type == pygame.KEYDOWN and flag:
                if event.key == pygame.K_UP:
                    player.jump()  # прыжок при нажатии на стрелочку вверх
                    flag1 = False
        if menu:
            if menu and not flag:  # отрисовка кнопок в открытом меню
                screen.fill("blue")
                button1.draw(screen)
                button2.draw(screen)
                button3.draw(screen)
                button4.draw(screen)
                button5.draw(screen)
                button6.draw(screen)

            if not game_over and flag and not congratulations:
                # пока идёт игра
                all_sprites.update()
                # дальше идёт обработка событий с персонажами при столкновении с разными объектами
                if player is not None and pygame.sprite.spritecollideany(player, cube_portals,
                                                                         collided=pygame.sprite.collide_mask):  # превращение в кубик
                    player = Cube(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 1
                    player.is_jumping = True

                if player is not None and pygame.sprite.spritecollideany(player, ufo_portals,
                                                                         collided=pygame.sprite.collide_mask):  # превращение в НЛО
                    player = Ufo(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 1

                if player is not None and pygame.sprite.spritecollideany(player, ball_portals,
                                                                         collided=pygame.sprite.collide_mask):  # превращение в шарик
                    player = Ball(200, player.rect.y)
                    to_remove = list(players)[0]
                    players.remove(to_remove)
                    all_sprites.remove(to_remove)
                    player.vy = 5
                    down = False
                    player.is_jumping = True

                if type(player) is Cube:  # Обработка событий с кубиком
                    if pygame.sprite.spritecollideany(player, spikes,
                                                      collided=pygame.sprite.collide_mask):  # столкновение с шипами
                        game_over = True
                        # Столкновение!
                    elif pygame.sprite.spritecollideany(player, platforms,
                                                        collided=pygame.sprite.collide_mask):  # обработка различного рода столкновений с платформами - на неё можно приземлиться, но нельзя врезаться слева и снизу
                        flag1 = True
                        platform = \
                            pygame.sprite.spritecollide(player, platforms, False, collided=pygame.sprite.collide_mask)[
                                0]
                        if platform.rect.x - 45 == player.rect.x:
                            game_over = True
                        elif platform.rect.y < player.rect.y:
                            game_over = True

                    elif flag1 and not pygame.sprite.spritecollideany(player, platforms,
                                                                      collided=pygame.sprite.collide_mask):  # падение с платформы
                        flag1 = False
                        player.vy = 0.2

                    if pygame.sprite.spritecollideany(player, trampolines,
                                                      collided=pygame.sprite.collide_mask):
                        player.jump()
                        flag1 = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and pygame.sprite.spritecollideany(
                            player,
                            spheres,
                            collided=pygame.sprite.collide_mask):  # прыжок в воздухе при столкновении со сферой
                        player.is_jumping = False
                        player.jump()
                        flag1 = False
                elif type(player) is Ufo:  # аналогичная обработка НЛО
                    if pygame.sprite.spritecollideany(player, spikes, collided=pygame.sprite.collide_mask):
                        game_over = True
                        # Столкновение!
                    elif pygame.sprite.spritecollideany(player, platforms, collided=pygame.sprite.collide_mask):
                        flag1 = True
                        platform = \
                            pygame.sprite.spritecollide(player, platforms, False, collided=pygame.sprite.collide_mask)[
                                0]
                        if platform.rect.x - 45 == player.rect.x:
                            game_over = True
                        elif platform.rect.y < player.rect.y:
                            player.vy = 0.1
                            player.rect.top = platform.rect.bottom

                    elif flag1 and not pygame.sprite.spritecollideany(player, platforms,
                                                                      collided=pygame.sprite.collide_mask):
                        flag1 = False
                        player.vy = 0.5

                elif type(player) is Ball:  # обработка шарика
                    player.update()
                    if not pygame.sprite.spritecollideany(player, platforms) and flag1 and player.vy == 0:
                        if down:  # смена гравитации
                            player.vy = 5
                        else:
                            player.vy = -5
                        flag1 = False
                    if pygame.sprite.spritecollideany(player, spikes, collided=pygame.sprite.collide_mask):
                        game_over = True
                        # Столкновение!
                    for platform in platforms:
                        if player.rect.colliderect(platform.rect) and abs(
                                player.rect.top - platform.rect.top) < 20 and abs(
                            player.rect.bottom - platform.rect.bottom) < 20:
                            game_over = True
                if pygame.sprite.spritecollideany(player, end_blocks):
                    congratulations = True  # конец уровня
            elif game_over:
                pygame.mixer.music.stop()  # остановка фоновой музыки и воспроизведение эффекта смерти (один раз)
                if not flag2:
                    pygame.mixer.Sound('death.ogg').play()
                    flag2 = True
                screen.blit(load_image("GAMEOVER.png"), (120, 270))
            elif congratulations:
                pygame.mixer.music.stop()  # остановка фоновой музыки и воспроизведение эффекта прохождения уровня (один раз)
                if not flag2:
                    pygame.mixer.Sound('end.ogg').play()
                    flag2 = True
                screen.blit(load_image("completed.png"), (30, 270))
        pygame.display.flip()  # Обновление и отрисовка всего интерфейса игры
        all_sprites.draw(screen)
        clock.tick(FPS)


running = True  # запуск игры
while running:
    start_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
pygame.quit()
