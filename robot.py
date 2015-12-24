#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from itertools import product

from pygame import *
from astar.astar_grid import *


CELL_SIZE = 32
MOVE_SPEED = CELL_SIZE
WIDTH = CELL_SIZE
HEIGHT = CELL_SIZE
ON_CLIENT = 'on_client'
ON_BASE = 'on_base'
COLOR = "#888888"


class Robot(sprite.Sprite):
    def __init__(self, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers):
        sprite.Sprite.__init__(self)
        self.cell_start_x = cell_start_x
        self.cell_start_y = cell_start_y
        self.cell_current_x = cell_start_x
        self.cell_current_y = cell_start_y
        self.client_count = 0
        self.tables = tables
        self.cart_field_width = cart_field_width
        self.cart_field_height = cart_field_height
        self.barriers = barriers


        self.xvel = 0   #скорость перемещения. 0 - стоять на месте
        self.yvel = 0 # скорость вертикального перемещения

        self.image = Surface((WIDTH, HEIGHT))
        self.image = image.load("static/Robot-icon_22_22.png")
        self.rect = Rect(self.cell_start_x*CELL_SIZE, self.cell_start_y*CELL_SIZE, WIDTH, HEIGHT) # прямоугольный объект
        self.path = None

    def make_graph(self, width, height, barriers):
        nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
        graph = {}
        for x, y in product(range(width), range(height)):
            if (x, y) not in barriers:
                node = nodes[x][y]
                graph[node] = []
                for i, j in product([-1, 0, 1], [-1, 0, 1]):
                    if not (0 <= x + i < width):
                        continue
                    if not (0 <= y + j < height):
                        continue
                    if not (x+i,y+j) in barriers:
                        graph[nodes[x][y]].append(nodes[x+i][y+j])
        return graph, nodes

    def set_path(self, cell_end_x, cell_end_y):
        graph, nodes = self.make_graph(self.cart_field_width, self.cart_field_height, self.barriers)
        paths = AStarGrid(graph)
        self.path = paths.search(
            nodes[self.cell_current_x][self.cell_current_y],
            nodes[cell_end_x][cell_end_y]
        )
        self.path.pop(0)

    def on_client(self):
        on_client = False
        for table in self.tables:
            if (self.cell_current_x, self.cell_current_y) == table.get_stay_point():
                on_client = True
                break
        return on_client

    def on_base(self):
        return (self.cell_current_x, self.cell_current_y) == (self.cell_start_x, self.cell_start_y)

    def get_current_pos(self):
        return self.cell_current_x, self.cell_current_y

    def make_step(self):
        if len(self.path) > 0:
            next_cell = self.path.pop(0)
            self.rect.x = next_cell.x * CELL_SIZE
            self.rect.y = next_cell.y * CELL_SIZE
            self.cell_current_x = next_cell.x
            self.cell_current_y = next_cell.y

    def get_next_task(self, tables_queue):
            if self.client_count <= 2 and len(tables_queue) > 0:
                self.client_count += 1
                destination = tables_queue.pop(0).get_stay_point()
                self.set_path(*destination)
                self.dest_description = ON_CLIENT
            else:
                destination = (self.cell_start_x, self.cell_start_y)
                self.set_path(*destination)
                self.dest_description = ON_BASE





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


