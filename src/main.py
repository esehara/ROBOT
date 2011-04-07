# -*- encording : UTF-8 -*-
import pygame
from pygame.locals import * 
from task import *
import sys

SCR = (640, 480)
color_black = 0, 0, 0
color_blue = 0, 0, 255
color_red = 255, 0, 0
CAP = 'Pyweek'

def load_image(filename, colorkey = None):
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
        if not game.pause_flag:
            self.counter += 1
        draw_count = str(self.counter)
        i = 0
        for keta in draw_count:
            game.screen.blit(self.images[int(keta)], (10 + i * 16, 10))
            self.rect.left = 10 + i * 16
            i += 1   

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR)
        pygame.display.set_caption(CAP)
        self.clock = pygame.time.Clock()
        self.quit = False
        self.counter = Count()
        self.pause_flag = False
        Tracker.instance().add_task(Player("./img/robot.png", "./img/robojump.png", 0, 0))
        Tracker.instance().add_task(SampleBossTask(200, 160))

    def update(self):
        Tracker.instance().act_all_tasks()
        return 

    def draw(self):
        self.screen.fill(color_blue)

#        self.screen.blit(self.player.hukidashi, (self.player.rect.left, self.player.rect.top - 16))
#        tamakazu = pygame.rect
#        tamakazu.left = self.player.rect.left + 3
#        tamakazu.top = self.player.rect.top - 13
#        tamakazu.width = self.player.inochi
#        tamakazu.height = 6

#        if self.player.inochi > 0:
#            pygame.draw.rect(self.screen, color_red, Rect(tamakazu.left,tamakazu.top,tamakazu.width,6), 0)
        ground = Ground()
        self.screen.blit(ground.drawscreen(), (0, 0))
        self.counter.update()

        ## 320, 240 ==> 640, 480
        tmpSurface = pygame.Surface((320, 240))
        tmpSurface.blit(self.screen, (0, 0))

        if self.pause_flag:
            tmpSurface = self.convert_to_girl(tmpSurface)

        self.screen.blit(pygame.transform.scale(tmpSurface, (640, 480)), (0, 0)) 
        pygame.display.flip()

    def keyevent(self):
        pass

    def mainLoop(self):
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit = True
                if (event.type == KEYDOWN and event.key == K_q):
                    self.pause_flag = True
            
            if self.pause_flag:
                self.purseLoop()
            
            self.keyevent()
            self.update()
            self.draw()
            Tracker.instance().delete_tasks()
            self.clock.tick(60)

    def purseLoop(self):
        while self.pause_flag:
            self.draw()
            for event in pygame.event.get():
                if (event.type == KEYDOWN and event.key == K_q):
                    self.pause_flag = False
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
    #game.titleLoop()
    game.mainLoop()
