# -*- coding: utf-8 -*-

from pygame import *

BLUE = (0, 0, 255)
RED = (255, 0, 0)
TRANSPARENT = (0, 0, 0)


class Table(sprite.Sprite):
    def __init__(self, cell_x, cell_y, CELL_SIZE):
        sprite.Sprite.__init__(self)
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.image = Surface((CELL_SIZE*2, CELL_SIZE*2))
        self.image.set_colorkey(TRANSPARENT)
        # coordinates of circle centre inside self.image
        draw.circle(self.image, BLUE, (CELL_SIZE, CELL_SIZE), CELL_SIZE, 0)
        # coordinates of self.image
        self.rect = Rect(cell_x*CELL_SIZE, cell_y*CELL_SIZE, CELL_SIZE*2, CELL_SIZE*2)

    def get_stay_point(self):
        return self.cell_x-1, self.cell_y+1
