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
	def __init__(self,filename,x,y):
		self.image = load_image(filename)
		self.rect = self.image.get_rect(topleft=(x,y))
		self.walk = {}
		self.muki = 'RIGHT'
		self.walking = False
		self.walkrate = 0
		
		##Right_Stop
		surface = pygame.Surface((16,16))
		surface.blit(self.image,(0,0),(0,0,16,16))
		surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
		surface.convert()
		self.walk.update({'right_stop':surface})
		
		##Right_Walk
		surface = pygame.Surface((16,16))
		surface.blit(self.image,(0,0),(16,0,16,16))
		surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
		surface.convert()
		self.walk.update({'right_move':surface})
		
		##Left_Stop
		surface = pygame.Surface((16,16))
		surface.blit(self.image,(0,0),(0,16,16,16))
		surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
		surface.convert()
		self.walk.update({'left_stop':surface})
		
		##Right_Walk
		surface = pygame.Surface((16,16))
		surface.blit(self.image,(0,0),(16,16,16,16))
		surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
		surface.convert()
		self.walk.update({'left_move':surface})

		self.image = self.walk['right_stop']

	def update(self):
		self.walkrate += 1
		if self.walking is False or self.walkrate < 6:
			if self.muki == 'RIGHT':
				self.image = self.walk['right_stop']
			elif self.muki == 'LEFT':
				self.image = self.walk['left_stop']
		elif self.walking is True and self.walkrate > 6:
			if self.muki == 'RIGHT':
				self.image = self.walk['right_move']
			elif self.muki == 'LEFT':
				self.image = self.walk['left_move']
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
		player.walking = False000			
		if keyin[K_RIGHT]:		
			player.muki = 'RIGHT'
			player.rect.move_ip(2,0)
			player.walking = True
		if keyin[K_LEFT]:
			player.muki = 'LEFT'
			player.rect.move_ip(-2,0)
			player.walking = True
			
	def mainLoop(self):
		global player
		player = Player("./img/robot.png",0,0)
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