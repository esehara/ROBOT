import pygame
from pygame.locals import * 

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
