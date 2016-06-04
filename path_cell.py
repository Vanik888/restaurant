# -*- coding: utf-8 -*-

from pygame import *


COLORS = {
    'BLUE':        (0, 0, 255),
    'RED':         (255, 0, 0),
    'ORANGE':      (230, 140, 20),
    'YELLOW':      (240, 255, 0),
    'PURPLE':      (180, 55, 220),
    'PINK':        (255, 100, 100),
    'TRANSPARENT': (0, 0, 0),
}




class PathCell(sprite.Sprite):
    def __init__(self, cell_x, cell_y, CELL_SIZE):
        sprite.Sprite.__init__(self)
        self.time_count = 0
        self.CELL_SIZE = CELL_SIZE
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.image = Surface((CELL_SIZE*1, CELL_SIZE*1))
        self.image.set_colorkey(COLORS['TRANSPARENT'])
        self.image.fill(COLORS['PINK'])
        # draw.line(self.image, COLORS['PINK'],[0, 0],[1,1], CELL_SIZE)
        self.rect = Rect(cell_x*CELL_SIZE, cell_y*CELL_SIZE, CELL_SIZE*1, CELL_SIZE*1)
