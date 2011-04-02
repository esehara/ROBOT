# -*- encording : UTF-8 -*-
import pygame
from pygame.locals import * 
import sys

SCR = (320,320)
color_black = 0,0,0
color_blue = 0,0,255
CAP = 'Pyweek'

def load_image(filename,colorkey=None):
    try:
        image = pygame.image.load(filename).convert()
    except pygame.error,message:
        print "Cannot load image:",filename
        raise SystemExit,message
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey,RLEACCEL)
    return image

class Player():
    def __init__(self,filename,filename2,x,y):
        self.jumping = 0
        self.images = []
        self.images.append(load_image(filename))
        self.images.append(load_image(filename2))
        self.rect = self.images[0].get_rect(topleft=(x,y))
        self.walk = {}
        self.muki = 'RIGHT'
        self.walking = False
        self.walkrate = 0
        surface = pygame.Surface((16,16))
        
        ##Right_Stop
        surface = pygame.Surface((16,16))
        surface.blit(self.images[0],(0,0),(0,0,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'right_stop':surface})
        
        ##Right_Walk
        surface = pygame.Surface((16,16))
        surface.blit(self.images[0],(0,0),(16,0,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'right_move':surface})
        
        ##Left_Stop
        surface = pygame.Surface((16,16))
        surface.blit(self.images[0],(0,0),(0,16,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'left_stop':surface})
        
        ##Right_Walk
        surface = pygame.Surface((16,16))
        surface.blit(self.images[0],(0,0),(16,16,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'left_move':surface})
        
        ##RightJump
        surface = pygame.Surface((16,16))
        surface.blit(self.images[1],(0,0),(0,0,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'right_jump':surface})
        
        ##leftJump
        surface = pygame.Surface((16,16))
        surface.blit(self.images[1],(0,0),(16,0,16,16))
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        self.walk.update({'left_jump':surface})

        self.image = self.walk['right_stop']
        self.rect.move_ip(120,250)
        
    def update(self):
        if self.jumping > 0 and self.jumping < 20:
           self.jumping += 1
           self.rect.move_ip(0,-2)
        elif self.jumping > 19 and self.jumping < 39:
            self.jumping += 1
            self.rect.move_ip(0,2)
        elif self.jumping > 38:
            self.jumping = 0
            
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


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR)
        pygame.display.set_caption(CAP)
        self.clock = pygame.time.Clock()
        self.quit = False

    def update(self):
        return
    
    def draw(self):
        self.screen.fill(color_blue)
        self.screen.blit(player.image,player.rect)
        pygame.display.flip()
    
    def keyevent(self):
        keyin = pygame.key.get_pressed()
        player.walking = False          
        if keyin[K_RIGHT]:      
            player.muki = 'RIGHT'
            player.rect.move_ip(2,0)
            player.walking = True
        if keyin[K_LEFT]:
            player.muki = 'LEFT'
            player.rect.move_ip(-2,0)
            player.walking = True
        if keyin[K_SPACE] and player.jumping < 1:
            player.jumping = 1
            
    def mainLoop(self):
        global player
        player = Player("./img/robot.png","./img/robojump.png",0,0)
        while not self.quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
            self.keyevent()
            player.update()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.mainLoop()
