# -*- encording : UTF-8 -*-

import pygame
from pygame.locals import * 
import json
import random
import sys

SCR = (640, 480)
color_black = 0, 0, 0
color_blue = 0, 0, 255
color_red = 255, 0, 0
CAP = 'Pyweek'

def load_image(filename, colorkey=None):
    try:
        image = pygame.image.load(filename).convert()
    except pygame.error, message:
        print "Cannot load image:", filename
        raise SystemExit, message
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

class Player():
    def __init__(self, filename, filename2, x, y):
        self.jumping = 0
        self.images = []

        self.images.append(load_image(filename))
        self.images.append(load_image(filename2))
        self.images.append(load_image("./img/huki.png"))

        self.rect = self.images[0].get_rect(topleft=(x, y))
        self.walk = {}
        self.muki = 'RIGHT'
        self.walking = False
        self.walkrate = 0
        self.grab_flag = True
        self.bullet_flag = False
        self.inochi = 9
        
        ##Right_Stop
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[0], (0, 0), (0, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'right_stop':surface})
        
        ##Right_Walk
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[0], (0, 0), (16, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'right_move':surface})
        
        ##Left_Stop
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[0],(0, 0),(0, 16, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'left_stop':surface})
        
        ##Right_Walk
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[0], (0, 0), (16, 16, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'left_move':surface})
        
        ##RightJump
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[1],(0, 0), (0, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'right_jump':surface})
        
        ##leftJump
        surface = pygame.Surface((16, 16))
        surface.blit(self.images[1], (0, 0), (16, 0, 16, 16))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface = surface.convert()
        self.walk.update({'left_jump':surface})

        ##hukidashi
        self.hukidashi = pygame.Surface((16, 16))
        self.hukidashi.blit(self.images[2],(0, 0),(0, 0, 16, 16))
        self.hukidashi.set_colorkey(self.hukidashi.get_at((0, 0)), RLEACCEL)
        self.hukidashi = self.hukidashi.convert()

        self.image = self.walk['right_stop']
        self.rect.move_ip(120, 120)        

    def update(self):
        if self.jumping > 0 and self.jumping < 39:
            self.jumping += 1
            self.clash_wall(0, -2)
        elif self.jumping > 38:
            self.jumping = 0

        self.grab_flag = self.grab()

        if self.grab_flag:
            self.rect.move_ip(0, 2)
            
        self.walkrate += 1

        if self.walking is False or self.walkrate < 6:
            if self.muki == 'RIGHT':
             self.image = self.walk['right_stop'] if self.jumping < 1 else self.walk['right_jump'] 
            elif self.muki == 'LEFT':
                self.image = self.walk['left_stop'] if self.jumping < 1 else self.walk['left_jump'] 
        elif self.walking is True and self.walkrate > 6:
            if self.muki == 'RIGHT':
                self.image = self.walk['right_move'] if self.jumping < 1 else self.walk['right_jump'] 
            elif self.muki == 'LEFT':
                self.image = self.walk['left_move'] if self.jumping < 1 else self.walk['left_jump'] 
        if self.walkrate > 12:
            self.walkrate = 0

    def clash_wall(self, x, y):
        # Clash Left or not ?

        mas_top = (self.rect.top + y) / 16
        mas_left = (self.rect.left + x)/ 16
        mas_bottom = ((self.rect.bottom + y) / 16 -1)
        mas_right = ((self.rect.right + x) / 16) -2

        if x < 0:
            if not ((game.landscape.wall_grid[mas_top][mas_left] > 0) or (game.landscape.wall_grid[mas_bottom][mas_left] > 0)):
                self.rect.move_ip(x, y) 
        if x > 0:
            if not ((game.landscape.wall_grid[mas_top][mas_right] > 0) or (game.landscape.wall_grid[mas_bottom][mas_right] > 0)):
                self.rect.move_ip(x, y)
        if y < 0:
            if not ((game.landscape.wall_grid[mas_top][mas_left] > 0) or (game.landscape.wall_grid[mas_top][mas_right] > 0)):
                self.rect.move_ip(x, y)
            elif ((game.landscape.wall_grid[mas_top][mas_left] > 0) or (game.landscape.wall_grid[mas_top][mas_right] > 0)):
                self.jumping = 0

    def grab(self):

        mas_left = self.rect.left / 16
        mas_bottom = (self.rect.top + 18) / 16
        mas_right = ((self.rect.right ) / 16) -2

        if self.jumping > 0 and self.jumping < 39:
            return False
        if not ((game.landscape.wall_grid[mas_bottom][mas_left] > 0) or (game.landscape.wall_grid[mas_bottom][mas_right] > 0)):
            return True        
        elif ((game.landscape.wall_grid[mas_bottom][mas_left] > 0) or (game.landscape.wall_grid[mas_bottom][mas_right] > 0)):
            return False

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

class Count():
    def __init__(self):
        self.image = load_image("./img/counter.png", -1)
        self.rect = self.image.get_rect()
        self.images = []       
        for i in range(self.rect.w / 16):
            surface = pygame.Surface((16, 16))
            surface.blit(self.image, (0, 0), (16 * i, 0, 16, 16))
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            surface = surface.convert()
            self.images.append(surface)
        self.counter = 0
        self.rect.move_ip(10,10)

    def update(self):
        self.counter += 1
        draw_count = str(self.counter)
        i = 0
        for keta in draw_count:
            game.screen.blit(self.images[int(keta)], (10 + i * 16, 10))
            self.rect.left = 10 + i * 16
            i += 1   

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

class Tracker(Singleton):
    def __init__(self):
        Singleton.__init__(self)
        self.bullet_tasks = []
        self.enemy_tasks = []
        self.player_tasks = []
        self.tasks_containers = [
            self.bullet_tasks,
            self.enemy_tasks,
            self.player_tasks]

    def add_task(self, task):
        if isinstance(task, BulletTask):
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

class Way():
    right, left = range(2)

class PlayerBulletTask(BulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)
        surface = pygame.Surface((8, 8))
        self.image = surface.convert()
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
        mas_x = self.rect.left / 16
        mas_y = self.rect.top / 16
        mas_b = self.rect.bottom / 16
        if (game.landscape.wall_grid[mas_y][mas_x] > 0):
            game.player.bullet_flag = False
            return True
        elif (game.landscape.wall_grid[mas_b][mas_x]>0):
            game.player.bullet_flag = False
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR)
        pygame.display.set_caption(CAP)
        self.clock = pygame.time.Clock()
        self.quit = False
        self.player = Player("./img/robot.png", "./img/robojump.png", 0, 0)
        self.wall = Wall("./img/wall.png")
        self.background = Background("./img/background.png")
        self.landscape = Landscape("./data/background.json", "./data/wall.json")
        self.counter = Count()
        self.purse_flag = False
        Tracker.instance().add_task(SampleBossTask(200, 160))

    def update(self):
        Tracker.instance().act_all_tasks()
        return 

    def draw(self):
        self.screen.fill(color_blue)
        for y in range(len(self.landscape.background_grid)):
            for x in range(len(self.landscape.background_grid[y])):
                index = self.landscape.background_grid[y][x]
                self.screen.blit(self.background.images[index], (x * 16, y * 16))
        for y in range(len(self.landscape.wall_grid)):
            for x in range(len(self.landscape.wall_grid[y])):
                index = self.landscape.wall_grid[y][x]
                self.screen.blit(self.wall.images[index], (x * 16, y * 16))
        for task in Tracker.instance().get_all_tasks():
            self.screen.blit(task.image, (task.rect.left, task.rect.top))
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.player.hukidashi, (self.player.rect.left, self.player.rect.top - 16))
        #Bullet no kazu
        tamakazu = pygame.rect
        tamakazu.left = self.player.rect.left + 3
        tamakazu.top = self.player.rect.top - 13
        tamakazu.width = self.player.inochi
        tamakazu.height = 6

        if self.player.inochi > 0:
            pygame.draw.rect(self.screen, color_red, Rect(tamakazu.left,tamakazu.top,tamakazu.width,6), 0)

        self.counter.update()

        ## 320, 240 ==> 640, 480
        tmpSurface = pygame.Surface((320, 240))
        tmpSurface.blit(self.screen, (0, 0))

        if self.purse_flag:
            tmpSurface = self.convert_to_gs(tmpSurface)

        self.screen.blit(pygame.transform.scale(tmpSurface, (640, 480)), (0, 0)) 
        pygame.display.flip()

    def keyevent(self):
        
        keyin = pygame.key.get_pressed()
        self.player.walking = False

        if keyin[K_RIGHT]:
            self.player.muki = 'RIGHT'
            self.player.walking = True
            self.player.clash_wall(2, 0)
        if keyin[K_LEFT]:
            self.player.muki = 'LEFT'
            self.player.walking = True
            self.player.clash_wall(-2, 0)
        if ((keyin[K_UP] | keyin[K_z]) and self.player.jumping == 0 and not self.player.grab()):
            self.player.jumping = 1
        if keyin[K_x] and not self.player.bullet_flag and self.player.inochi > 0:
            self.player.bullet_flag = True
            self.player.inochi -= 1
            way = Way.right if self.player.muki == 'RIGHT' else Way.left
            Tracker.instance().add_task(PlayerBulletTask(self.player.rect.left, self.player.rect.top, way))
        if not keyin[K_UP]:
            self.player.jumping = 0

    def mainLoop(self):
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_q):
                    self.purse_flag = True
            
            if self.purse_flag:
                self.purseLoop()
            
            self.keyevent()
            self.player.update()
            self.update()
            self.draw()
            Tracker.instance().delete_tasks()
            self.clock.tick(60)

    def purseLoop(self):
        while self.purse_flag:
            self.draw()
            for event in pygame.event.get():
                if (event.type == KEYDOWN and event.key == K_q):
                    self.purse_flag = False
            self.clock.tick(60)

    def titleLoop(self):
        titleimage = load_image('./img/title.png', -1)
        typed_start = False
        while not typed_start:
            self.screen.fill(color_blue)
            self.screen.blit(titleimage, (60, 50))
            tmpSurface = pygame.Surface((320, 240))
            self.screen.blit(pygame.transform.scale(tmpSurface, (640, 480)), (0, 0)) 
            tmpSurface.blit(self.screen, (0, 0))
            pygame.display.flip()
            for event in pygame.event.get():
                if (event.type == KEYDOWN and event.key == K_SPACE):
                    typed_start = True
                if event.type == QUIT:
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit = True
            self.clock.tick(60)
        return

    def convert_to_gs(self, surf):
        width, height = surf.get_size()
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = surf.get_at((x, y))
                average = (red + green + blue) // 3
                gs_color = (average, average, average, alpha)
                surf.set_at((x, y), gs_color)
        return surf

if __name__ == '__main__':
    game = Game()
    #game.titleLoop()
    game.mainLoop()
