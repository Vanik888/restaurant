# -*- coding: utf-8 -*-

from pygame import *

from common_vars import TABLE_STATUSES


COLORS = {
    'BLUE':        (0, 0, 255),
    'RED':         (255, 0, 0),
    'ORANGE':      (230, 140, 20),
    'YELLOW':      (240, 255, 0),
    'PURPLE':      (180, 55, 220),
    'PINK':        (255, 100, 100),
    'TRANSPARENT': (0, 0, 0),
}


colors_for_statuses = {
            TABLE_STATUSES['WAITING_TO_MAKE_ORDER']: COLORS['RED'],
            TABLE_STATUSES['WAITING_MEAL']:          COLORS['ORANGE'],
            TABLE_STATUSES['EATING']:                COLORS['YELLOW'],
            TABLE_STATUSES['WAITING_BILL']:          COLORS['PINK'],
            TABLE_STATUSES['WAITING_CLEAN']:         COLORS['PURPLE'],
            TABLE_STATUSES['NOT_READY']:             COLORS['BLUE'],
}


class Table(sprite.Sprite):
    def __init__(self, cell_x, cell_y, CELL_SIZE):
        sprite.Sprite.__init__(self)
        self.time_count = 0
        self.CELL_SIZE = CELL_SIZE
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.image = Surface((CELL_SIZE*2, CELL_SIZE*2))
        self.image.set_colorkey(COLORS['TRANSPARENT'])
        self.status = TABLE_STATUSES['NOT_READY']
        # coordinates of circle centre inside self.image
        draw.circle(self.image, COLORS['BLUE'], (CELL_SIZE, CELL_SIZE), CELL_SIZE, 0)
        # coordinates of self.image
        self.rect = Rect(cell_x*CELL_SIZE, cell_y*CELL_SIZE, CELL_SIZE*2, CELL_SIZE*2)

        self.colors_for_statuses = {
            TABLE_STATUSES['WAITING_TO_MAKE_ORDER']: COLORS['RED'],
            TABLE_STATUSES['WAITING_MEAL']:          COLORS['ORANGE'],
            TABLE_STATUSES['EATING']:                COLORS['YELLOW'],
            TABLE_STATUSES['WAITING_BILL']:          COLORS['PINK'],
            TABLE_STATUSES['NOT_READY']:             COLORS['BLUE'],

        }

    def get_table_area(self):
        table_area = []
        for x in range(2):
            for y in range(2):
                table_area.append((self.cell_x + x, self.cell_y + y))
        return table_area

    def get_stay_point(self):
        return self.cell_x-1, self.cell_y+1

    def get_sit_point(self):
        return self.cell_x+3, self.cell_y+1

    def set_time_count(self, count):
        self.time_count = count

    def dec_time_count(self):
        self.time_count -= 1

    def set_status(self, STATUS):
        self.status = STATUS
        draw.circle(self.image, colors_for_statuses[STATUS], (self.CELL_SIZE, self.CELL_SIZE), self.CELL_SIZE, 0)
