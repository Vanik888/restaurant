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
    def __init__(self, name, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers):
        sprite.Sprite.__init__(self)
        self.name = name
        self.cell_start_x = cell_start_x
        self.cell_start_y = cell_start_y
        self.cell_current_x = cell_start_x
        self.cell_current_y = cell_start_y
        self.client_count = 0
        self.total_served_client_count = 0
        self.dest_description = ON_BASE
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

    def get_tables_area(self):
        tables_area = []
        for t in self.tables:
            tables_area += t.get_table_area()
        return tables_area

    def make_graph(self, width, height, barriers, dyn_obstacles=[]):
        tables_area = self.get_tables_area()
        nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
        graph = {}
        for x, y in product(range(width), range(height)):
            if (x, y) not in barriers + tables_area + dyn_obstacles:
                node = nodes[x][y]
                graph[node] = []
                for i, j in product([-1, 0, 1], [-1, 0, 1]):
                    if not (0 <= x + i < width):
                        continue
                    if not (0 <= y + j < height):
                        continue
                    if not (x+i,y+j) in barriers + tables_area + dyn_obstacles:
                        graph[nodes[x][y]].append(nodes[x+i][y+j])
        return graph, nodes

    def set_path(self, cell_end_x, cell_end_y, dyn_obstacles=[]):
        graph, nodes = self.make_graph(self.cart_field_width, self.cart_field_height, self.barriers, dyn_obstacles)
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
            # не последний шаг и есть препятствия => перестраиваем маршрут
            elif len(self.path) != 0:
                print('current state is  (x=%s; y=%s)' %(self.cell_current_x, self.cell_current_y))
                if not od.no_robots(next_cell.x, next_cell.y):
                    print('there are robot on (x=%s; y=%s)' % (next_cell.x, next_cell.y))
                    self.update_path(next_cell.x, next_cell.y)
                elif not od.no_peoples(next_cell.x, next_cell.y):
                    self.update_path(next_cell.x, next_cell.y)
                    print('there are people on (x=%s; y=%s)' % (next_cell.x, next_cell.y))
            else:
                if not od.no_robots(next_cell.x, next_cell.y):
                    print('there are robot on (x=%s; y=%s)' % (next_cell.x, next_cell.y))
                    print('skip the step')
                elif not od.no_peoples(next_cell.x, next_cell.y):
                    print('there are people on (x=%s; y=%s)' % (next_cell.x, next_cell.y))
                    print('skip the step')


    def set_path_to_base(self):
        destination = (self.cell_start_x, self.cell_start_y)
        self.set_path(*destination)
        self.dest_description = ON_BASE

    def get_next_client(self, client):
        destination = client.get_stay_point()
        self.client_destination = destination
        self.set_path(*destination)
        self.dest_description = ON_CLIENT

    # создаем новый путь с учетом препятствия x, y
    def update_path(self, obstacle_x, obstacle_y):
        destination = self.path[0].get_cart_coordinates()
        old_path = self.path
        self.set_path(*destination, dyn_obstacles=[(obstacle_x, obstacle_y)])
        new_path = self.path
        self.print_path_diff(old_path, new_path)

    # принтим старый путь и новый
    def print_path_diff(self, old_path, new_path):
        old_path = [(p.x, p.y)for p in old_path]
        new_path = [(p.x, p.y)for p in new_path]
        print('old path: ' + str(old_path))
        print('new path: ' + str(new_path))





