import pygame
from load_image import *
from pygame.locals import *
from main import *
from single import *
import random
import json

color_red = 255,0,0
max_jumping_frame = 35
jumping_max_speed = max_jumping_frame
jumping_division = 18

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

class Task():
    def __init__(self):
        self.image = None
        self.rect = Rect(0, 0, 0, 0)
        self.generator = None
        self.is_deleted = False
        self.wall = Wall("./img/wall.png")
        self.load_stage()

    def get_stage(self):
        return Tracker.instance().stage

    def load_stage(self):
        stage = self.get_stage()
        self.background = Background("./img/background0" + str(stage) + ".png")
        self.landscape = Landscape("./data/background0" + str(stage) + ".json", "./data/wall0" + str(stage) + ".json")

    def act(self):
        raise NotImplementedError

class BulletTask(Task):
    pass

class EnemyTask(Task):
    pass

class PlayerTask(Task):
    pass

class PlayerBulletTask(Task):
    pass

class ScreenTask(Task):
    pass

class TaskNotImplementedError():
    pass

class Tracker(Singleton):
    def __init__(self):
        Singleton.__init__(self)
        self.screen_tasks = []
        self.enemy_tasks = []
        self.player_tasks = []
        self.bullet_tasks = []
        self.player_bullet_tasks = []
        self.tasks_containers = [
            self.screen_tasks,
            self.enemy_tasks,
            self.player_tasks,
            self.bullet_tasks,
            self.player_bullet_tasks]
        self.stage = 0

    def add_task(self, task):
        if isinstance(task, ScreenTask):
            self.screen_tasks.append(task)
        elif isinstance(task, EnemyTask):
            self.enemy_tasks.append(task)
        elif isinstance(task, PlayerTask):
            self.player_tasks.append(task)
        elif isinstance(task, BulletTask):
            self.bullet_tasks.append(task)
        elif isinstance(task, PlayerBulletTask):
            self.player_bullet_tasks.append(task)
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

    def detect_collision(self, target_parent, actor_task):
        if issubclass(target_parent, ScreenTask):
            target_container = self.screen_tasks
        elif issubclass(target_parent, EnemyTask):
            target_container = self.enemy_tasks
        elif issubclass(target_parent, PlayerTask):
            target_container = self.player_tasks
        elif issubclass(target_parent, BulletTask):
            target_container = self.bullet_tasks
        elif issubclass(target_parent, PlayerBulletTask):
            target_container = self.player_bullet_tasks
        else:
            raise TaskNotImplementedError

        is_collision = False
        for task in target_container:
            horizontal_collision = (task.rect.left <= (actor_task.rect.left + actor_task.rect.w)) and (actor_task.rect.left <= (task.rect.left + task.rect.w))
            vertical_collision = (task.rect.top <= (actor_task.rect.top + actor_task.rect.w)) and (actor_task.rect.top <= (task.rect.top + task.rect.h))
            if horizontal_collision and vertical_collision:
                is_collision = True
        return is_collision

class CountTask(ScreenTask):
    def __init__(self):
        Task.__init__(self)
        base_image = load_image("./img/counter.png", -1)
        self.base_images = []
        for i in range(base_image.get_rect().w / 16):
            surface = pygame.Surface((16, 16))
            surface.blit(base_image, (0, 0), (16 * i, 0, 16, 16))
            surface = surface.convert()
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            self.base_images.append(surface)
        self.counter = 0
        self.rect = pygame.Rect(16, 16, 16 * 4, 16)
        self.image = pygame.Surface((16 * 4, 16)).convert()
        self.image.set_colorkey(self.image.get_at((0, 0)), RLEACCEL)

    def act(self):
        while True:
            self.image.fill((0, 0, 0))
            self.counter += 1
            draw_count = str(self.counter)
            left = (3 - len(draw_count)) * 16
            i = 0
            for digit in draw_count:
                self.image.blit(self.base_images[int(digit)], (left + i * 16, 0))
                i += 1
            yield True

class GroundTask(ScreenTask):
    def __init__(self):
        Task.__init__(self)
        self.image = pygame.Surface((320, 240)).convert()
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

class Balloon(PlayerTask):
    def __init__(self, player_task):
        Task.__init__(self)

        self.player_task = player_task

        self.image = pygame.Surface((16, 16)).convert()
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
            self.image.fill(color_red, life_rect)
            yield

class Player(PlayerTask):
    def __init__(self, filename, filename2, left, top):
        Task.__init__(self)
        self.is_jump_upping = False
        self.jumping_count = 0
        self.base_x = 0
        self.last_jump_height = 0
        base_images = []

        base_images.append(load_image(filename))
        base_images.append(load_image(filename2))

        self.rect = base_images[0].get_rect(topleft = (left, top))
        self.walk = {}
        self.way = Way.right
        self.walking = False
        self.walkcount = 0
        self.is_pressed_bullet_key = False
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

        self.is_pressed_bullet_key = False

        Tracker.instance().add_task(Balloon(self))

    def keyevent(self):
        global bullet_flag
        keyin = pygame.key.get_pressed()
        self.walking = False

        if keyin[K_RIGHT]:
            self.way = Way.right
            self.walking = True
            if self.is_collision_wall(2, 0):
                self.rect.left += 2
        if keyin[K_LEFT]:
            self.way = Way.left
            self.walking = True
            if self.is_collision_wall(-2, 0):
                self.rect.left -= 2
        if (keyin[K_UP] or keyin[K_z]) and not self.is_jump_upping and self.is_on_flooring():
            self.is_jump_upping = True
            self.base_x = -1 * jumping_max_speed
            self.last_jump_height = (self.base_x ** 2) / jumping_division
        if not (keyin[K_UP] or keyin[K_z]) and self.is_jump_upping and not self.is_on_flooring():
            self.is_jump_upping = False
            self.reset_jump_status()
        if keyin[K_x] and not self.is_pressed_bullet_key and self.life > 0:
            self.is_pressed_bullet_key = True
            self.life -= 1
            way = Way.right if self.way == Way.right else Way.left
            Tracker.instance().add_task(PlayerBulletNormalTask(self.rect.left, self.rect.top, way))
        if not keyin[K_x] and self.is_pressed_bullet_key:
            self.is_pressed_bullet_key = False

    def motion(self):
        if self.is_jump_upping:
            self.jumping_count += 1
            self.jump_up()
        else:
            if not self.is_on_flooring(): # down
                self.jump_down()
            else: # reach floor
                self.reset_jump_status()

        if self.jumping_count >= max_jumping_frame or self.is_head_butt():
            self.reset_jump_status()

        self.walkcount += 1

        if self.walking is False or self.walkcount < 6:
            if self.way == Way.right:
                self.image = self.walk[Motion.right_stop] if not self.is_jump_upping else self.walk[Motion.right_jump]
            elif self.way == Way.left:
                self.image = self.walk[Motion.left_stop] if not self.is_jump_upping else self.walk[Motion.left_jump]
        elif self.walking is True and self.walkcount > 6:
            if self.way == Way.right:
                self.image = self.walk[Motion.right_move] if not self.is_jump_upping else self.walk[Motion.right_jump]
            elif self.way == Way.left:
                self.image = self.walk[Motion.left_move] if not self.is_jump_upping else self.walk[Motion.left_jump]
        if self.walkcount > 12:
            self.walkcount = 0

    def act(self):
        while True:
            self.keyevent()
            self.motion()
            yield True

    def jump_up(self):
        self.update_jump_status()
        jump_height = self.calculate_jump_height()
        cell_top = int(self.rect.top + jump_height) / 16
        cell_left = self.rect.left / 16
        cell_right = (self.rect.right / 16) - 2

        if not ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)):
            self.rect.top -= jump_height

    def jump_down(self):
        self.update_jump_status()
        jump_height = self.calculate_jump_height()
        cell_top = int(self.rect.top + jump_height) / 16
        next_cell_bottom = int(self.rect.bottom + jump_height) / 16 - 1
        cell_left = self.rect.left / 16
        cell_right = (self.rect.right / 16) - 2

        is_collision_top = (self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)
        is_collision_next_bottom = (self.landscape.wall_grid[next_cell_bottom][cell_left] > 0) or (self.landscape.wall_grid[next_cell_bottom][cell_right] > 0)
        if not is_collision_top:
            self.rect.top += jump_height
            if is_collision_next_bottom:
                self.rect.top -= (self.rect.top + 1) - (int((self.rect.top + 1) / 16) * 16)

    def is_head_butt(self):
        jump_height = self.calculate_jump_height()
        cell_top = int(self.rect.top - jump_height) / 16
        cell_left = self.rect.left / 16
        cell_right = (self.rect.right / 16) - 2

        if ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)):
            return True
        else:
            return False

    def calculate_jump_height(self):
        height = self.last_jump_height - (self.base_x ** 2) / jumping_division
        return abs(height)

    def update_jump_status(self):
        self.last_jump_height = (self.base_x ** 2) / jumping_division
        self.base_x += 1

    def reset_jump_status(self):
        self.last_jump_height = 0
        self.base_x = 0
        self.is_jump_upping = False
        self.jumping_count = 0

    def is_collision_wall(self, x, y):
        cell_top = int(self.rect.top + y) / 16
        cell_left = (self.rect.left + x) / 16
        cell_bottom = ((self.rect.bottom + y) / 16 - 1)
        cell_right = ((self.rect.right + x) / 16) - 2

        if x < 0:
            if not ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_left] > 0)):
                return True
        if x > 0:
            if not ((self.landscape.wall_grid[cell_top][cell_right] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
                return True
        if y < 0:
            if not ((self.landscape.wall_grid[cell_top][cell_left] > 0) or (self.landscape.wall_grid[cell_top][cell_right] > 0)):
                return True
        return False

    def is_on_flooring(self):
        cell_left = self.rect.left / 16
        cell_bottom = int(self.rect.top + 18) / 16
        cell_right = (self.rect.right / 16) - 2

        if not ((self.landscape.wall_grid[cell_bottom][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
            return False
        elif ((self.landscape.wall_grid[cell_bottom][cell_left] > 0) or (self.landscape.wall_grid[cell_bottom][cell_right] > 0)):
            return True

class PlayerBulletNormalTask(PlayerBulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)

        self.image = load_image("./img/tama.png", -1)

        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.way = way

    def act(self):
        while True:
            if self.way == Way.right:
                self.rect.left += 4
                if self.clash_wall():
                    yield False
            elif self.way == Way.left:
                self.rect.left -= 4
                if self.clash_wall():
                    yield False
            yield True

    def clash_wall(self):
        global bullet_flag
        
        cell_x = self.rect.left / 16
        cell_y = self.rect.top / 16
        cell_b = self.rect.bottom / 16

        if (self.landscape.wall_grid[cell_y][cell_x] > 0):
            return True
        elif (self.landscape.wall_grid[cell_b][cell_x]>0):
            return True
        else:
            return False 
        if Tracker.instance().detect_collision(SampleBossTask, self):
            return False
        return True

class SampleBossBulletTask(BulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)
        self.image = pygame.Surface((2, 2)).convert()
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
        self.image = pygame.Surface((16, 32)).convert()
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
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    pass
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    pass 
                yield True


