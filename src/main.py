# -*- encording : UTF-8 -*-
import pygame
from pygame.locals import * 
from task import *
from load_image import *
import sys

SCR = (640, 480)
color_black = 0, 0, 0
color_blue = 0, 0, 255
color_red = 255, 0, 0
CAP = 'Pyweek'

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR)
        pygame.display.set_caption(CAP)
        self.clock = pygame.time.Clock()
        self.quit = False
        self.pause_flag = False
        self.pause_image = load_image("./img/pause.png", -1)
        x = Tracker.instance().stage.data["x"]
        y = Tracker.instance().stage.data["y"]
        player_task = Player("./img/robot.png", "./img/robojump.png", x, y)
        Tracker.instance().add_task(player_task)
        Tracker.instance().player_task = player_task
        Tracker.instance().add_task(Boss0Task(180, 160))
        ground_task = GroundTask()
        Tracker.instance().add_task(ground_task)
        Tracker.instance().ground_task = ground_task
        Tracker.instance().add_task(CountTask())
        self.is_pressed_pause_key = False
        self.temp_surface = pygame.Surface((320, 240)).convert()

        base_image = load_image("./img/counter.png", -1)
        self.base_images = []
        for i in range(base_image.get_rect().w / 16):
            surface = pygame.Surface((16, 16))
            surface.blit(base_image, (0, 0), (16 * i, 0, 16, 16))
            surface = surface.convert()
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            self.base_images.append(surface)
  
        import os 
        for line in open(os.path.join(os.path.dirname(__file__), '../data/highscore.dat'),'r'):
            temp = line[:-1].split(':')
            self.highscore = temp[0]
            self.highstage = temp[1]

        self.rect = pygame.Rect(16, 16, 16 * 4, 16)
        self.image = pygame.Surface((16 * 4, 16)).convert()
        self.image.set_colorkey(self.image.get_at((0, 0)), RLEACCEL)
        
    def update(self):
        if not self.pause_flag:
            Tracker.instance().act_all_tasks()
        return 

    def draw(self):
        if not self.pause_flag:
            self.temp_surface.fill(color_blue)
            for task in Tracker.instance().get_all_tasks():
                self.temp_surface.blit(task.image, (task.rect.left, task.rect.top))

        self.screen.blit(pygame.transform.scale(self.temp_surface, (640, 480)), (0, 0)) 
        pygame.display.flip()

    def keyevent(self):
        keyin = pygame.key.get_pressed()
        if keyin[K_q] and not self.is_pressed_pause_key:
            self.is_pressed_pause_key = True
            if self.pause_flag:
                self.pause_flag = False
            else:
                self.pause_flag = True
                self.temp_surface.blit(self.pause_image, (60 + random.randint(0,15), 140 + random.randint(0,15)))
        if not keyin[K_q] and self.is_pressed_pause_key:
            self.is_pressed_pause_key = False

    def mainLoop(self):
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit = True

            self.keyevent()
            self.update()
            self.draw()
            Tracker.instance().delete_tasks()
            Tracker.instance().add_all_reserved_tasks()
            self.clock.tick(60)

    def titleLoop(self):
        titlecount = 0
        start_draw_flag = True

        titleimage = load_image('./img/title.png', -1)
        startimage = load_image('./img/pushstart.png',-1)
        subtitleimage = load_image('./img/subtitle.png',-1)

        typed_start = False
        
        while not typed_start:
            titlecount += 1
            if titlecount > 16:
                if start_draw_flag:
                    start_draw_flag = False
                else:
                    start_draw_flag = True
                titlecount = 0

            game.screen.fill(color_blue)
            game.screen.blit(titleimage, (60, 50))
            game.screen.blit(subtitleimage, (70, 110))
            if start_draw_flag:
                game.screen.blit(startimage, (20,200))

            tmpSurface = pygame.Surface((320, 240))
            tmpSurface.blit(game.screen, (0, 0))
            game.screen.blit(pygame.transform.scale(tmpSurface, (640, 480)), (0, 0)) 
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

    def gameOver(self):
        gameoverimage = load_image('./img/gameover.png', -1)
        
        while True:
            game.screen.fill(color_blue)
            game.screen.blit(gameoverimage, (10, 50))

            tmpSurface = pygame.Surface((320, 240))
            tmpSurface.blit(game.screen, (0, 0))
            game.screen.blit(pygame.transform.scale(tmpSurface, (640, 480)), (0, 0)) 
            pygame.display.flip()
            self.clock.tick(60)
            for event in pygame.event.get():
                if (event.type == KEYDOWN and event.key == K_SPACE):
                    return 
                if event.type == QUIT:
                    self.quit = True
                    return
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit = True
                    return

    def convert_to_girl(self, surf):
        width, height = surf.get_size()
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = surf.get_at((x, y))
                average = (red + green + blue) // 3
                gs_color = (average, average, average, alpha)
                surf.set_at((x, y), gs_color)
        return surf

def main():
    global game
    game = Game()
    game.titleLoop()
    game.mainLoop()

def gameover():
    global game
    game = Game()
    game.gameOver()
