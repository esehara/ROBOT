import pygame
from load_image import *
from pygame.locals import *
from main import *
from single import *
import random
import json
import math

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

class Stage():
    def __init__(self, filename):
        f = open(filename)
        self.data = json.load(f)
        f.close()

class Task():
    def __init__(self):
        self.image = None
        self.rect = Rect(0, 0, 0, 0)
        self.generator = None
        self.is_deleted = False

    def set_stage(self,stg):
        Tracker.instance().stage = stg

    def act(self):
        raise NotImplementedError

class ClearTask(Task):
    pass

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
        self.clear_tasks = []
        self.tasks_containers = [
            self.screen_tasks,
            self.enemy_tasks,
            self.player_tasks,
            self.bullet_tasks,
            self.player_bullet_tasks,
            self.clear_tasks]
        self.wall = Wall("./img/wall.png")
        self.stage_number = 0
        self.load_stage()
        self.player_task = None
        self.ground_task = None
        self.attacked_time = 0
        self.reserved_tasks = []

    def load_stage(self):
        self.background = Background("./img/background0" + str(self.stage_number) + ".png")
        self.landscape = Landscape("./data/background0" + str(self.stage_number) + ".json", "./data/wall0" + str(self.stage_number) + ".json")
        self.stage = Stage("./data/stage0" + str(self.stage_number) + ".json")

    def increment_stage(self):
        self.stage_number += 1
        self.load_stage()
        self.ground_task.load_images()
        self.player_task.rect.left = self.stage.data["x"]
        self.player_task.rect.top = self.stage.data["y"]

    def add_task_next_frame(self, task):
        self.reserved_tasks.append(task)

    def add_all_reserved_tasks(self):
        for task in self.reserved_tasks:
            self.add_task(task)
        self.reserved_tasks = []

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
        elif isinstance(task, ClearTask):
            self.clear_tasks.append(task)
        else:
            raise TaskNotImplementedError
        task.generator = task.act()

    def delete_all_tasks(self):
        self.screen_tasks = []
        self.enemy_tasks = []
        self.player_tasks = []
        self.bullet_tasks = [] 
        self.player_bullet_tasks = []
        self.clear_tasks = []

    def delete_bullet_tasks(self):
#        print("delete bullet")
        for task in self.bullet_tasks:
            task.is_deleted = True

    def delete_player_bullet_tasks(self):
#        print("delete player bullet")
        for task in self.player_bullet_tasks:
            task.is_deleted = True

    def act_all_tasks(self):
        for task in self.get_all_tasks():
            try:
                ret = task.generator.next()
                if ret == False:
                    task.is_deleted = True
            except StopIteration, e:
                for task in self.get_all_tasks():
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

    def detect_collision(self, target_parent, actor_task, is_delete = False):
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
                if is_delete:
                    task.is_deleted = True
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
            left = (4 - len(draw_count)) * 16
            i = 0
            for digit in draw_count:
                self.image.blit(self.base_images[int(digit)], (left + i * 16, 0))
                i += 1
            Tracker.instance().attacked_time = self.counter
            yield True

class ClearLogoTask(ClearTask):
    def __init__(self):
        Task.__init__(self)
        self.image = load_image("./img/yourscore.png", -1)
        self.rect = pygame.Rect(80, 80, self.image.get_rect().width, self.image.get_rect().height)

    def act(self):
        while True:
            yield True

class ClearScoreTask(ClearTask):
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
        self.rect = pygame.Rect(120, 150, 16 * 4, 16)
        self.image = pygame.Surface((16 * 4, 16)).convert()
        self.image.set_colorkey(self.image.get_at((0, 0)), RLEACCEL)
        self.attacked_time = Tracker.instance().attacked_time

    def act(self):
        while True:
            self.image.fill((0, 0, 0))
            draw_count = str(self.attacked_time)
            left = (4 - len(draw_count)) * 16
            i = 0
            for digit in draw_count:
                self.image.blit(self.base_images[int(digit)], (left + i * 16, 0))
                i += 1
            yield True

class GroundTask(ScreenTask):
    def __init__(self):
        Task.__init__(self)
        self.load_images()

    def load_images(self):
        self.image = pygame.Surface((320, 240)).convert()
        landscape = Tracker.instance().landscape
        for y in range(len(landscape.background_grid)):
            for x in range(len(landscape.background_grid[y])):
                index = landscape.background_grid[y][x]
                self.image.blit(Tracker.instance().background.images[index], (x * 16, y * 16))
        for y in range(len(landscape.wall_grid)):
            for x in range(len(landscape.wall_grid[y])):
                index = landscape.wall_grid[y][x]
                self.image.blit(Tracker.instance().wall.images[index], (x * 16, y * 16))

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

        self.rect = pygame.Rect(left, top, 0, 0)
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

        self.is_pressed_bullet_key = False
        self.is_clear = False
        self.clear_counter = 0

        Tracker.instance().add_task(Balloon(self))

    def keyevent(self):
        global bullet_flag
        keyin = pygame.key.get_pressed()
        self.walking = False

        if keyin[K_RIGHT]:
            self.way = Way.right
            self.walking = True
            if self.is_collision_side_wall(2):
                self.rect.left += 2
        if keyin[K_LEFT]:
            self.way = Way.left
            self.walking = True
            if self.is_collision_side_wall(-2):
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
#            print('life is %d' % self.life)
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
        gameover = False
        while not gameover:
            self.keyevent()
            self.motion()
            if self.life <= 0:
                gameover = True
            if self.is_clear and self.clear_counter < 600:
                Tracker.instance().add_task(ClearBulletTask(self))
                self.clear_counter += 1
            yield True
        if gameover:
            import main
            Tracker.instance().delete_all_tasks()
            main.gameover()

    def jump_up(self):
        self.update_jump_status()
        jump_height = self.calculate_jump_height()
        cell_top = int(int(self.rect.top + jump_height) / 16)
        cell_left = int(self.rect.left / 16)
        cell_right = int(self.rect.right / 16) + 1
        is_right = True if self.rect.right % 16 else False

        landscape = Tracker.instance().landscape
        if is_right:
            if (landscape.wall_grid[cell_top][cell_left] == 0) and (landscape.wall_grid[cell_top][cell_right] == 0):
                self.rect.top -= jump_height
        else:
            if landscape.wall_grid[cell_top][cell_left] == 0:
                self.rect.top -= jump_height

    def jump_down(self):
        self.update_jump_status()
        jump_height = self.calculate_jump_height()
        cell_top = int(int(self.rect.top + jump_height) / 16)
        next_cell_bottom = int(int(self.rect.bottom + jump_height) / 16) + 1
        cell_left = int(self.rect.left / 16)
        cell_right = int(self.rect.right / 16) + 1
        is_right = True if self.rect.right % 16 else False

        landscape = Tracker.instance().landscape
        if is_right:
            is_collision_top = (landscape.wall_grid[cell_top][cell_left] > 0) and (landscape.wall_grid[cell_top][cell_right] > 0)
            is_collision_next_bottom = (landscape.wall_grid[next_cell_bottom][cell_left] > 0) and (landscape.wall_grid[next_cell_bottom][cell_right] > 0)
        else:
            is_collision_top = landscape.wall_grid[cell_top][cell_left] > 0
            is_collision_next_bottom = landscape.wall_grid[next_cell_bottom][cell_left] > 0
        if not is_collision_top:
            self.rect.top += jump_height
            if is_collision_next_bottom:
                self.rect.top = (next_cell_bottom - 1) * 16

    def is_head_butt(self):
        jump_height = self.calculate_jump_height()
        cell_top = int(int(self.rect.top - jump_height) / 16)
        cell_left = int(self.rect.left / 16)
        cell_right = int(self.rect.right / 16) + 1

        landscape = Tracker.instance().landscape
        is_right = True if self.rect.right % 16 else False
        if is_right:
            if (landscape.wall_grid[cell_top][cell_left] == 0) and (landscape.wall_grid[cell_top][cell_right] == 0):
                return False
            else:
                return True
        else:
            if landscape.wall_grid[cell_top][cell_left] == 0:
                return False
            else:
                return True

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

    def is_collision_side_wall(self, x):
        cell_top = int(self.rect.top / 16)
        cell_left = int((self.rect.left + x) / 16)
        cell_bottom = int((self.rect.bottom - 1) / 16) + 1
        cell_right = int((self.rect.right + x) / 16) + 1
        is_top = True if self.rect.top % 16 else False

        landscape = Tracker.instance().landscape
        if x < 0:
            if is_top:
                if (landscape.wall_grid[cell_top][cell_left] == 0) and (landscape.wall_grid[cell_bottom][cell_left] == 0):
                    return True
                else:
                    return False
            else:
                if landscape.wall_grid[cell_bottom][cell_left] == 0:
                    return True
                else:
                    return False
        if x > 0:
            if is_top:
                if (landscape.wall_grid[cell_top][cell_right] == 0) and (landscape.wall_grid[cell_bottom][cell_right] == 0):
                    return True
                else:
                    return False
            else:
                if landscape.wall_grid[cell_bottom][cell_right] == 0:
                    return True
                else:
                    return False
        return False

    def is_on_flooring(self):
        cell_bottom = int((self.rect.top + 16) / 16)
        cell_left = int(self.rect.left / 16)
        cell_right = int((self.rect.right / 16)) + 1
        is_right = True if self.rect.right % 16 else False

        landscape = Tracker.instance().landscape
        if is_right:
            if (landscape.wall_grid[cell_bottom][cell_left] == 0) and (landscape.wall_grid[cell_bottom][cell_right] == 0):
                return False
            else:
                return True
        else:
            if landscape.wall_grid[cell_bottom][cell_left] == 0:
                return False
            else:
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

        landscape = Tracker.instance().landscape
        if (landscape.wall_grid[cell_y][cell_x] > 0):
            return True
        elif (landscape.wall_grid[cell_b][cell_x]>0):
            return True
        else:
            return False 
        return True

class ClearBulletTask(PlayerBulletTask):
    def __init__(self, player_task):
        Task.__init__(self)
        self.image = pygame.Surface((4, 4))
        self.image.fill((random.randrange(256), random.randrange(256), random.randrange(256)))
        self.rect.left = player_task.rect.left
        self.rect.top = player_task.rect.top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.player_task = player_task
        self.counter = 0

    def act(self):
        while True:
            self.counter += 1
            self.rect.left = self.player_task.rect.left + math.sin(self.counter / math.pi / 1) * self.counter * 0.1
            self.rect.top = self.player_task.rect.top + math.cos(self.counter / math.pi / 1) * self.counter * 0.1
            yield True

class SampleBossBulletTask(BulletTask):
    def __init__(self, left, top, way):
        Task.__init__(self)
        self.image = load_image("./img/gorem_tama.png", -1)
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

class BossRingTask(BulletTask):
    def __init__(self, boss_task):
        Task.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.rect.left = boss_task.rect.left
        self.rect.top = boss_task.rect.top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.boss_task = boss_task
        self.counter = 0

    def act(self):
        while True:
            self.counter += 1
            self.rect.left = self.boss_task.rect.left + 25 + math.sin(self.counter / math.pi / 6) * 30
            self.rect.top = self.boss_task.rect.top + math.cos(self.counter / math.pi / 6) * 4
            if self.boss_task.is_deleted:
                yield False
            yield True

class SinBulletTask(BulletTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = pygame.Surface((2, 2))
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.counter = 0

    def act(self):
        while True:
            self.counter += 1
            self.rect.left -= 2
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 4
            yield True

class SuperBulletTask(BulletTask):
    def __init__(self, boss_task):
        Task.__init__(self)
        self.image = pygame.Surface((4, 4))
        self.rect.left = boss_task.rect.left
        self.rect.top = boss_task.rect.top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.boss_task = boss_task
        self.counter = 0

    def act(self):
        while True:
            self.counter += 1
            self.rect.left = self.boss_task.rect.left + 25 + math.sin(self.counter / math.pi / 6) * self.counter
            self.rect.top = self.boss_task.rect.top + math.cos(self.counter / math.pi / 6) * self.counter
            if self.boss_task.is_deleted:
                yield False
            yield True

class UmbrellaBulletTask(BulletTask): # oops...
    def __init__(self, left, top):
        Task.__init__(self)
        surface = load_image("./img/umb_bullet.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((16, 16)))
            self.images[i].blit(surface, (0, 0), (i * 16, 0, 16, 16))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()
        self.image = self.images[0]
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height
        self.counter = 0

    def act(self):
        while True:
            self.counter += 1
            self.rect.left -= 3
            self.image = self.images[self.counter % 2]
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 4
            yield True

class Boss0Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/mons_stone.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((32, 64)))
            self.images[i].blit(self.image, (0, 0), (i * 32, 0, 32, 64))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                Tracker.instance().delete_player_bullet_tasks()
                Tracker.instance().add_task_next_frame(Boss1Task(130, 180))
                yield False
            if Tracker.instance().detect_collision(PlayerTask, self):
                Tracker.instance().increment_stage()
                Tracker.instance().add_task_next_frame(Boss1Task(130, 180))
                Tracker.instance().delete_player_bullet_tasks()
                Tracker.instance().player_task.life -= 1
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15
            if random.randrange(10) == 0:
                Tracker.instance().add_task(SinBulletTask(self.rect.left, self.rect.top))
            yield True

class Boss1Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/mons_slim.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((48, 64)))
            self.images[i].blit(self.image, (0, 0), (i * 48, 0, 48, 64))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

        self.walk_rate = 0
        self.walk_flag = False

        Tracker.instance().add_task(BossRingTask(self))

    def act(self):
        while True:
            self.walk_rate +=1

            if self.walk_flag:
                self.rate = 0
                self.walk_flag = False
                self.image = self.images[self.walk_flag]
            else:
                self.rate = 0
                self.walk_flag = True
                self.image = self.images[self.walk_flag]

            for i in range(60):
                if i % 2:
                    self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss2Task(50, 50))
                    yield False
                yield True
            for i in range(60):
                if i % 2:
                    self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss2Task(50, 50))
                    yield False
                yield True

class Boss2Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/slim.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((32, 32)))
            self.images[i].blit(self.image, (0, 0), (i*32, 0, 32, 32))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15

            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss3Task(200, 150))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss3Task(200, 150))
                    yield False
                yield True
            
class Boss3Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/goast.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((16, 16)))
            self.images[i].blit(self.image, (0, 0), (i*16, 0, 16, 16))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15
            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss4Task(250, 100))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss4Task(250, 100))
                    yield False
                yield True

class Boss4Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/mons_toyoi.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((30, 40)))
            self.images[i].blit(self.image, (0, 0), (i*30, 0, 30, 40))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15
            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss5Task(200, 150))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss5Task(200, 150))
                    yield False
                yield True

class Boss5Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/gorem.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((16, 32)))
            self.images[i].blit(self.image, (0, 0), (i*16, 0, 16, 32))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15
            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss6Task(200, 100))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss6Task(200, 100))
                    yield False
                yield True

class Boss6Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/mons_star.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((46, 42)))
            self.images[i].blit(self.image, (0, 0), (i*46, 0, 46, 42))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15

            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss7Task(200, 200))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss7Task(200, 200))
                    yield False
                yield True

class Boss7Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/gorem.png", -1)
        self.images = []
        for i in range(2):
            self.images.append(pygame.Surface((16, 32)))
            self.images[i].blit(self.image, (0, 0), (i*16, 0, 16, 32))
            self.images[i].set_colorkey(self.images[i].get_at((0, 0)), RLEACCEL)
            self.images[i] = self.images[i].convert()

        self.image = self.images[0]
        self.counter = 0

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().increment_stage()
                yield False
            self.counter += 1
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 2) * 15
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 2) * 15

            for i in range(30):
                self.rect.left += 1
                if random.randrange(40) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss8Task(160, 120))
                    yield False
                yield True
            for i in range(30):
                self.rect.left -= 1
                if random.randrange(25) == 0:
                    Tracker.instance().add_task(SampleBossBulletTask(self.rect.left, self.rect.top + random.randrange(32), Way.left))
                if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                    Tracker.instance().player_task.life -= 1
                if Tracker.instance().detect_collision(PlayerBulletTask, self):
                    Tracker.instance().increment_stage()
                    Tracker.instance().delete_bullet_tasks()
                    Tracker.instance().delete_player_bullet_tasks()
                    Tracker.instance().add_task_next_frame(Boss8Task(160, 120))
                    yield False
                yield True

class Boss8Task(EnemyTask):
    def __init__(self, left, top):
        Task.__init__(self)
        self.image = load_image("./img/mons_last.png", -1)
        self.images = []

        self.images.append(pygame.Surface((39, 33)))
        self.images[0].blit(self.image, (0, 0), (0, 0, 39, 33))
        self.images[0].set_colorkey(self.images[0].get_at((0, 0)), RLEACCEL)
        self.images[0] = self.images[0].convert()

        self.image = self.images[0]
        self.counter = 135
        self.is_right = True

        self.base_left = left
        self.base_top = top
        self.rect.left = left
        self.rect.top = top
        self.rect.width = self.image.get_rect().width
        self.rect.height = self.image.get_rect().height

    def act(self):
        while True:
            if Tracker.instance().detect_collision(PlayerBulletTask, self):
                Tracker.instance().add_task(ClearLogoTask())
                Tracker.instance().add_task(ClearScoreTask())
                Tracker.instance().player_task.is_clear = True
                yield False
            if self.is_right:
                self.counter += 1
                if self.counter > 225:
                    self.is_right = False
            else:
                self.counter -= 1
                if self.counter < 135:
                    self.is_right = True
            self.rect.left = self.base_left + math.sin(self.counter / math.pi / 10) * 60
            self.rect.top = self.base_top + math.cos(self.counter / math.pi / 10) * 60
            if Tracker.instance().detect_collision(BulletTask, Tracker.instance().player_task):
                Tracker.instance().player_task.life -= 1
            if random.randrange(10) == 0:
                Tracker.instance().add_task(SuperBulletTask(self))
            yield True


