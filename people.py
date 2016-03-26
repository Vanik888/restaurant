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


class People(sprite.Sprite):
    def __init__(self, name, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers):
        sprite.Sprite.__init__(self)
        self.name = name
        self.cell_start_x = cell_start_x
        self.cell_start_y = cell_start_y
        self.cell_current_x = cell_start_x
        self.cell_current_y = cell_start_y
        self.dest_description = ON_BASE
        self.tables = tables
        self.cart_field_width = cart_field_width
        self.cart_field_height = cart_field_height
        self.barriers = barriers

        self.xvel = 0   #скорость перемещения. 0 - стоять на месте
        self.yvel = 0 # скорость вертикального перемещения

        self.image = Surface((WIDTH, HEIGHT))
        self.image = image.load("static/girl_22_22.png")
        self.rect = Rect(self.cell_start_x*CELL_SIZE, self.cell_start_y*CELL_SIZE, WIDTH, HEIGHT) # прямоугольный объект
        self.path = None

    def get_tables_area(self):
        tables_area = []
        for t in self.tables:
            tables_area += t.get_table_area()
        return tables_area

    def make_graph(self, width, height, barriers):
        tables_area = self.get_tables_area()
        nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
        graph = {}
        for x, y in product(range(width), range(height)):
            if (x, y) not in barriers + tables_area:
                node = nodes[x][y]
                graph[node] = []
                for i, j in product([-1, 0, 1], [-1, 0, 1]):
                    if not (0 <= x + i < width):
                        continue
                    if not (0 <= y + j < height):
                        continue
                    if not (x+i,y+j) in barriers + tables_area:
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
        return (self.cell_current_x, self.cell_current_y) == self.client_destination

    def on_base(self):
        return (self.cell_current_x, self.cell_current_y) == (self.cell_start_x, self.cell_start_y)

    def get_current_pos(self):
        return self.cell_current_x, self.cell_current_y

    def make_step(self, od):
        if len(self.path) > 0:
            next_cell = self.path.pop(0)
            if (od.is_clear(next_cell.x, next_cell.y)):
                self.rect.x = next_cell.x * CELL_SIZE
                self.rect.y = next_cell.y * CELL_SIZE
                self.cell_current_x = next_cell.x
                self.cell_current_y = next_cell.y
            elif not od.no_robots(next_cell.x, next_cell.y):
                self.path.append(next_cell)
                print('there are robot')
            elif not od.no_peoples(next_cell.x, next_cell.y):
                self.path.append(next_cell)
                print('there are people')

    def set_path_to_base(self):
        destination = (self.cell_start_x, self.cell_start_y)
        self.set_path(*destination)
        self.dest_description = ON_BASE

    def get_next_client(self, client):
        destination = client.get_stay_point()
        self.client_destination = destination
        self.set_path(*destination)
        self.dest_description = ON_CLIENT



