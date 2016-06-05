# -*- coding: utf-8 -*-

from pygame import *
from common_vars import COLORS

class PathCell(sprite.Sprite):
    def __init__(self, cell_x, cell_y, CELL_SIZE, color):
        sprite.Sprite.__init__(self)
        self.time_count = 0
        self.CELL_SIZE = CELL_SIZE
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.image = Surface((CELL_SIZE*1, CELL_SIZE*1))
        self.image.set_colorkey(COLORS['TRANSPARENT'])
        self.image.fill(color)
        # draw.line(self.image, COLORS['PINK'],[0, 0],[1,1], CELL_SIZE)
        self.rect = Rect(cell_x*CELL_SIZE, cell_y*CELL_SIZE, CELL_SIZE*1, CELL_SIZE*1)
