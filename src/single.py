import pygame
from load_image import *
from pygame.locals import *
from task import *
from main import *

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
