#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import pygame

from operator import itemgetter
from itertools import product
from pygame import *
from blocks import *
from robot import *
from table import *
from astar.astar_grid import *


CELL_SIZE = 32
CART_WIDTH = 25
CART_HEIGHT = 20
WIN_WIDTH = CART_WIDTH * CELL_SIZE
WIN_HEIGHT = CART_HEIGHT * CELL_SIZE
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004000"


def make_graph(width, height, barriers):
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


def get_static_barriers(level):
    x = 0
    y = 0
    barriers = []
    for row in level:
        for col in row:
            if col == "-":
                barriers.append((x, y))
            x += 1
        y += 1
        x = 0

    barriers_array = []
    for i in range( max([k[0] for k in barriers]) +1):
        barriers_row = []
        for item in barriers:
            if item[0] == i:
                barriers_row.append(item)
        barriers_array.append(barriers_row)
    return barriers



def main():
    pygame.init() # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY) # Создаем окошко
    pygame.display.set_caption("Robot field") # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)) # Создание видимой поверхности
                                          # будем использовать как фон
    bg.fill(Color(BACKGROUND_COLOR))      # Заливаем поверхность сплошным цветом




    timer = pygame.time.Clock()
    entities = pygame.sprite.Group() # Все объекты
    platforms = [] # то, во что мы будем врезаться или опираться


    level = [
           "-------------------------",
           "-                       -",
           "-                       -",
           "-                       -",
           "-            --         -",
           "-                       -",
           "--                      -",
           "-                       -",
           "-                   --- -",
           "-                       -",
           "-                       -",
           "-      ---              -",
           "-                       -",
           "-   -----------         -",
           "-                       -",
           "-                -      -",
           "-                   --  -",
           "-                       -",
           "-                       -",
           "-------------------------"]

    barriers = get_static_barriers(level)
    graph, nodes = make_graph(CART_WIDTH, CART_HEIGHT, barriers)
    paths = AStarGrid(graph)

    START_CELL_X = 1
    START_CELL_Y = 1
    table1 = Table(7, 5, CELL_SIZE)
    table2 = Table(7, 7, CELL_SIZE)
    tables = [table1, table2]

    robot1 = Robot(START_CELL_X, START_CELL_Y, tables, CART_WIDTH, CART_HEIGHT, barriers)
    robot2 = Robot(START_CELL_X, START_CELL_Y+3, tables, CART_WIDTH, CART_HEIGHT, barriers)
    robot3 = Robot(START_CELL_X, START_CELL_Y+7, tables, CART_WIDTH, CART_HEIGHT, barriers)
    robots = [robot1, robot2, robot3]

    tables_queue = []
    for table in tables:
        entities.add(table)
    for robot in robots:
        entities.add(robot)



    # robot.set_path(table.get_stay_point()[0],table.get_stay_point()[1])
    # graph, nodes = make_graph(CART_WIDTH, CART_HEIGHT, barriers)
    # paths = AStarGrid(graph)
    # start, end = nodes[2][2], nodes[1][1]
    # path = paths.search(start, end)

    # paths = AStarGrid(graph)
    # graph, nodes = make_graph(CART_WIDTH, CART_HEIGHT, barriers)
    # paths = AStarGrid(graph)
    # start, end = nodes[1][1], nodes[2][2]
    # path = paths.search(start, end)

    # hero.set_path(path)

    while 1: # Основной цикл программы
        timer.tick(2000)
        screen.blit(bg, (0, 0))      # Каждую итерацию необходимо всё перерисовывать

        for b in barriers:
            pf = Platform(b[0]*CELL_SIZE, b[1]*CELL_SIZE)
            entities.add(pf)

        for robot in robots:
            # init pos/ came to base
            if robot.on_base() and robot.dest_description == ON_BASE:
                robot.client_count = 0
                if len(tables_queue) > 0:
                    robot.get_next_client(tables_queue.pop(0))
                    robot.client_count += 1
                else:
                    robot.set_path_to_base()
            # moving from base
            elif robot.on_base() and robot.dest_description == ON_CLIENT:
                pass
            # moving from client
            elif robot.on_client() and robot.dest_description == ON_BASE:
                if len(tables_queue) > 0 and robot.client_count <= 2:
                    robot.get_next_client(tables_queue.pop(0))
                    robot.client_count += 1
            # came to client
            elif robot.on_client() and robot.dest_description == ON_CLIENT:
                robot.set_path_to_base()
                for table in tables:
                    if robot.get_current_pos() == table.get_stay_point():
                        table.set_not_ready()
                        table.set_time_count(10)

            # moving to base
            elif not robot.on_client() and not robot.on_base() and robot.dest_description == ON_BASE:
                if len(tables_queue) > 0 and robot.client_count < 2:
                    robot.get_next_client(tables_queue.pop(0))
                    robot.client_count += 1
            # moving to client
            elif not robot.on_client() and not robot.on_base() and robot.dest_description == ON_CLIENT:
                pass #still move to client



            robot.make_step()



        # add client
        for table in tables:
            table.dec_time_count()
            if table.status == NOT_READY_STATUS and table not in tables_queue:
                if table.time_count <= 0:
                    table.set_ready()
                    tables_queue.append(table)


        entities.draw(screen)

        pygame.display.update()     # обновление и вывод всех изменений на экран


if __name__ == "__main__":
    main()

