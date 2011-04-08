import pygame
from load_image import *
from pygame.locals import *
from main import *
import random
import json

color_red = 255,0,0

class Way():
    right, left = range(2)

class Motion():
    right_stop, right_move, left_stop, left_move, right_jump, left_jump = range(6)

class Background():
    def __init__(self, filename):
        self.image = load_image(filename)
        self.rect = self.image.get_rect()
        self.images = []
        
        for i in range(self.rect.w / 16):
            surface = pygame.Surface((16, 16))
            surface.blit(self.image, (0, 0), (16 * i, 0, 16, 16))
            surface = surface.convert()
            self.images.append(surface)

class Wall():
    def __init__(self, filename):
        self.image = load_image(filename, -1)
        self.rect = self.image.get_rect()
        self.images = []
        
        for i in range(self.rect.w / 16):
            surface = pygame.Surface((16, 16))
            surface.blit(self.image, (0, 0), (16 * i, 0, 16, 16))
            if i == 0:
                surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            surface = surface.convert()
            self.images.append(surface)

class Landscape():
    def __init__(self, background_filename, wall_filename):
        f = open(background_filename)
        self.background_grid = json.load(f)
        f.close()
        f = open(wall_filename)
        self.wall_grid = json.load(f)
        f.close()

class Singleton:
    __instances = {}
    __creations = set()

    def __init__(self):
        if self.__class__ not in self.__creations:
            raise RuntimeError("must call instance()")

    @classmethod
    def instance(cls):
        instance = Singleton.__instances.get(cls, None)
        if instance is None:
            Singleton.__creations.add(cls)
            try:
                Singleton.__instances[cls] = instance = cls()
            finally:
                Singleton.__creations.remove(cls)
        return instance

class Task():
    def __init__(self):
        self.image = None
        self.rect = Rect(0, 0, 0, 0)
        self.generator = None
        self.is_deleted = False
        self.wall = Wall("./img/wall.png")
        self.background = Background("./img/background.png")
        self.landscape = Landscape("./data/background.json", "./data/wall.json")

    def act(self):
        raise NotImplementedError

class BulletTask(Task):
    pass

class EnemyTask(Task):
    pass

class PlayerTask(Task):
    pass

class TaskNotImplementedError():
    pass

class ScreenTask(Task):
    pass

class Ground(ScreenTask):
    def __init__(self):
        Task.__init__(self)
        self.image = pygame.Surface((320, 240))
        for y in range(len(self.landscape.background_grid)):
            for x in range(len(self.landscape.background_grid[y])):
                index = self.landscape.background_grid[y][x]
                self.image.blit(self.background.images[index], (x * 16, y * 16))
        for y in range(len(self.landscape.wall_grid)):
            for x in range(len(self.landscape.wall_grid[y])):
                index = self.landscape.wall_grid[y][x]
                self.image.blit(self.wall.images[index], (x * 16, y * 16))

    def act(self):
        while True:
            yield

class Tracker(Singleton):
    def __init__(self):
        Singleton.__init__(self)
        self.screen_tasks = []
        self.bullet_tasks = []
        self.enemy_tasks = []
        self.player_tasks = []
        self.tasks_containers = [
            self.screen_tasks,
            self.bullet_tasks,
            self.enemy_tasks,
            self.player_tasks]

    def add_task(self, task):
        if isinstance(task, ScreenTask):
            self.screen_tasks.append(task)
        elif isinstance(task, BulletTask):
            self.bullet_tasks.append(task)
        elif isinstance(task, EnemyTask):
            self.enemy_tasks.append(task)
        elif isinstance(task, PlayerTask):
            self.player_tasks.append(task)
        else:
            raise TaskNotImplementedError
        task.generator = task.act()

    def act_all_tasks(self):
        for task in self.get_all_tasks():
            ret = task.generator.next()
            if ret == False:
                task.is_deleted = True

    def delete_tasks(self):
        for task_container in self.tasks_containers:
            for task in task_container:
                if task.is_deleted == True:
                    task_container.remove(task)

    def get_all_tasks(self):
        for task_container in self.tasks_containers:
            for task in task_container:
                yield task

class Balloon(PlayerTask):
    def __init__(self, player_task):
        Task.__init__(self)

        self.player_task = player_task

        self.image = pygame.Surface((16, 16))
        self.balloon = load_image("./img/balloon.png").convert()
        self.image.blit(self.balloon, (0, 0))
        self.image.set_colorkey(self.image.get_at((0, 0)), RLEACCEL)

        self.rect.left = player_task.rect.left
        self.rect.top = player_task.rect.top - self.image.get_rect().height
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            self.rect.left = self.player_task.rect.left
            self.rect.top = self.player_task.rect.top - self.image.get_rect().height
            self.image.blit(self.balloon, (0, 0))
            life_rect = pygame.Rect(0, 0, 0, 0)
            life_rect.left = 3
            life_rect.top = 4
            life_rect.w = self.player_task.life
            life_rect.h = 6
            color_red = 255, 0, 0
#            pygame.draw.rect(self.image, color_red, life_rect, 0)
            self.image.fill(color_red, life_rect)
            yield

class Player(PlayerTask):
    def __init__(self, filename, filename2, left, top):
        Task.__init__(self)
        self.jumping = 0
        base_images = []

        base_images.append(load_image(filename))
        base_images.append(load_image(filename2))

        self.rect = base_images[0].get_rect(topleft = (left, top))
        self.walk = {}
        self.way = Way.right
        self.walking = False
        self.walkcount = 0
        self.gravity_flag = True
        self.bullet_flag = False
        self.life = 9
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[0], (0, 0), (0, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.right_stop:surface})
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[0], (0, 0), (16, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.right_move:surface})
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[0], (0, 0),(0, 16, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.left_stop:surface})
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[0], (0, 0), (16, 16, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.left_move:surface})
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[1],(0, 0), (0, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.right_jump:surface})
        
        surface = pygame.Surface((16, 16))
        surface.blit(base_images[1], (0, 0), (16, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({Motion.left_jump:surface})

        self.image = self.walk[Motion.right_stop]
        self.rect.move_ip(120, 120)        

        Tracker.instance().add_task(Balloon(self))

    def keyevent(self):
        keyin = pygame.key.get_pressed()
        self.walking = False

        if keyin[K_RIGHT]:
            self.way = Way.right
            self.walking = True
            self.clash_wall(2, 0)
        if keyin[K_LEFT]:
            self.way = Way.left
            self.walking = True
            self.clash_wall(-2, 0)
        if ((keyin[K_UP] | keyin[K_z]) and self.jumping == 0 and not self.gravity()):
            self.jumping = 1
        if keyin[K_x] and not self.bullet_flag and self.life > 0:
            self.bullet_flag = True
            self.life -= 1
            way = Way.right if self.way == Way.right else Way.left
            Tracker.instance().add_task(PlayerBulletTask(self.rect.left, self.rect.top, way))
        if not keyin[K_UP]:
            self.jumping = 0

    def motion(self):
        if self.jumping > 0 and self.jumping < 39:
            self.jumping += 1
            self.clash_wall(0, -2)
        elif self.jumping > 38:
            self.jumping = 0

        self.gravity_flag = self.gravity()

        if self.gravity_flag:
            self.rect.move_ip(0, 2)
        self.walkcount += 1

        if self.walking is False or self.walkcount < 6:
            if self.way == Way.right:
             self.image = self.walk[Motion.right_stop] if self.jumping < 1 else self.walk[Motion.right_jump]
            elif self.way == Way.left:
                self.image = self.walk[Motion.left_stop] if self.jumping < 1 else self.walk[Motion.left_jump]
        elif self.walking is True and self.walkcount > 6:
            if self.way == Way.right:
                self.image = self.walk[Motion.right_move] if self.jumping < 1 else self.walk[Motion.right_jump]
            elif self.way == Way.left:
                self.image = self.walk[Motion.left_move] if self.jumping < 1 else self.walk[Motion.left_jump]
        if self.walkcount > 12:
            self.walkcount = 0

    def act(self):
        while True:
            self.keyevent()
            self.motion()
            yield True

    def clash_wall(self, x, y):
        # Clash Left or not ?
        cell_top = (self.rect.top + y) / 16
        cell_left = (self.rect.left + x)/ 16
        cell_bottom = ((self.rect.bottom + y) / 16 -1)
        cell_right = ((self.rect.right + x) / 16) -2

        if x < 0:
            if not ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_left] > 0)):
                self.rect.move_ip(x, y) 
        if x > 0:
            if not ((self.landscape.wall_grid[cell_top][cell_right] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
                self.rect.move_ip(x, y)
        if y < 0:
            if not ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)):
                self.rect.move_ip(x, y)
            elif ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)):
                self.jumping = 0

    def gravity(self):
        cell_left = self.rect.left / 16
        cell_bottom = (self.rect.top + 18) / 16
        cell_right = ((self.rect.right ) / 16) -2

        if self.jumping > 0 and self.jumping < 39:
            return False
        if not ((self.landscape.wall_grid[cell_bottom][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
            return True
        elif ((self.landscape.wall_grid[cell_bottom][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
            return False

class PlayerBulletTask(BulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)

        surface = pygame.Surface((8, 8))
        self.image = load_image("./img/tama.png",-1)
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface.convert()

        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.way = way

    def act(self):
        while True:
            if self.way == Way.right:
                self.rect.left += 8
                if self.clash_wall():
                    yield False
            elif self.way == Way.left:
                self.rect.left -= 8
                if self.clash_wall():
                    yield False
            yield True

    def clash_wall(self):
        cell_x = self.rect.left / 16
        cell_y = self.rect.top / 16
        cell_b = self.rect.bottom / 16
        if (self.landscape.wall_grid[cell_y][cell_x] > 0):
            self.bullet_flag = False
            return True
        elif (self.landscape.wall_grid[cell_b][cell_x]>0):
            self.bullet_flag = False
            return True
        else:
            return False 

class SampleBossBulletTask(BulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)
        surface = pygame.Surface((2, 2))
        self.image = surface.convert()
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.way = way

    def act(self):
        while True:
            if self.way == Way.right:
                self.rect.left += 2
                if self.rect.left > 320:
                    yield False
            elif self.way == Way.left:
                self.rect.left -= 2
                if self.rect.left < 0 - 2:
                    yield False
            yield True

class SampleBossTask(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        surface = pygame.Surface((16, 32))
        self.image = surface.convert()
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                yield True


