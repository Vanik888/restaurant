#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from pygame import *
from astar.astar_grid import *

CELL_SIZE = 32
MOVE_SPEED = CELL_SIZE
WIDTH = CELL_SIZE
HEIGHT = CELL_SIZE
COLOR = "#888888"


class Robot(sprite.Sprite):
    def __init__(self, cell_start_x, cell_start_y, paths, nodes):
        sprite.Sprite.__init__(self)
        self.paths = paths
        self.nodes = nodes
        self.cell_start_x = cell_start_x
        self.cell_start_y = cell_start_y
        self.cell_current_x = cell_start_x
        self.cell_current_y = cell_start_y
        self.busy = False

        self.xvel = 0   #скорость перемещения. 0 - стоять на месте
        self.yvel = 0 # скорость вертикального перемещения

        self.image = Surface((WIDTH, HEIGHT))
        self.image = image.load("static/Robot-icon_22_22.png")
        self.rect = Rect(self.cell_start_x*CELL_SIZE, self.cell_start_y*CELL_SIZE, WIDTH, HEIGHT) # прямоугольный объект
        self.path = None

    def set_path(self, cell_end_x, cell_end_y):
        self.path = self.paths.search(
            self.nodes[self.cell_current_x][self.cell_current_y],
            self.nodes[cell_end_x][cell_end_y]
        )

    def make_step(self):
        if len(self.path) > 0:
            next_cell = self.path.pop(0)
            self.rect.x = next_cell.x * CELL_SIZE
            self.rect.y = next_cell.y * CELL_SIZE

    # def check_situation(self, tables, partners):
    #     for table in tables:
    #         if table.status == 'ready' and self.busy
    #         if not self.busy:
    #             self.set_path(table)



    def update(self,  left, right, up, down, platforms):
        if left:
            self.xvel = -MOVE_SPEED # Лево = x- n

        if right:
            self.xvel = MOVE_SPEED # Право = x + n

        if up:
            self.yvel = -MOVE_SPEED

        if down:
            self.yvel = MOVE_SPEED

        if not(up or down):
            self.yvel = 0

        if not(left or right): # стоим, когда нет указаний идти
            self.xvel = 0

        self.rect.x += self.xvel # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if xvel > 0: # движение вправо
                    self.rect.right = p.rect.left
                if xvel < 0: # движение влево
                    self.rect.left = p.rect.right
                if yvel > 0: # движение вниз
                    self.rect.bottom = p.rect.top
                if yvel < 0: # движение вверх
                    self.rect.top = p.rect.bottom


