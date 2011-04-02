# -*- encording : UTF-8 -*-
import pygame
from pygame.locals import * 
SCR = (320,320)
color_black = 0,0,0
CAP = 'Pyweek'

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode(SCR)
		pygame.display.set_caption(CAP)
		
		self.quit = False

	def update(self):
		return
	
	def draw(self):
		self.screen.fill(color_black)
		pygame.display.flip()
		
	def mainLoop(self):
		while not self.quit:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.quit = True
			self.update()
			self.draw()
			self.clock.tick(60)

if __name__ == '__main__':
	game = Game()
	game.mainLoop()