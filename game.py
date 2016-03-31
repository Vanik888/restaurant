#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import pygame

from operator import itemgetter
from itertools import product
from pygame import *
from blocks import *
from robot import *
from people import *
from table import *
from astar.astar_grid import *
from chef import Chef
from time import sleep


CELL_SIZE = 32
CART_WIDTH = 25
CART_HEIGHT = 20
WIN_WIDTH = CART_WIDTH * CELL_SIZE
WIN_HEIGHT = CART_HEIGHT * CELL_SIZE
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004000"


class ObstaclesDefiner():
    def __init__(self, robots, peoples):
        self.robots = robots
        self.peoples = peoples

    def no_object(self, x, y, objects):
        no_object = True
        for o in objects:
            if (x, y) == (o.cell_current_x, o.cell_current_y):
                no_object = False
        return no_object

    def no_robots(self, x, y):
        return self.no_object(x, y, self.robots)

    def no_peoples(self, x, y):
        return self.no_object(x, y, self.peoples)

    def is_clear(self, x, y):
        return self.no_object(x, y, self.robots) and self.no_object(x, y, self.peoples)

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
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-                       -",
           "-------------------------"]

    barriers = get_static_barriers(level)

    START_CELL_X = 1
    START_CELL_Y = 1
    table1 = Table(5, 5, CELL_SIZE)
    table2 = Table(5, 8, CELL_SIZE)
    table3 = Table(5, 11, CELL_SIZE)
    table4 = Table(10, 5, CELL_SIZE)
    table5 = Table(10, 8, CELL_SIZE)
    table6 = Table(10, 11, CELL_SIZE)
    table7 = Table(15, 5, CELL_SIZE)
    table8 = Table(15, 8, CELL_SIZE)
    table9 = Table(15, 11, CELL_SIZE)
    tables = [table1, table2, table3, table4, table5, table6, table7, table8, table9]
    busy_tables = []
    meals_queue = []
    cooking_meals = []

    chef = Chef(cooking_meals=cooking_meals, meals_queue=meals_queue)
    people_julia = People('Julia', 10, 3, tables, CART_WIDTH, CART_HEIGHT, barriers)
    peoples = [people_julia]

    robot1 = Robot('r1', START_CELL_X, START_CELL_Y, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot2 = Robot('r2', START_CELL_X, START_CELL_Y+3, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot3 = Robot(START_CELL_X, START_CELL_Y+6, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot4 = Robot(START_CELL_X, START_CELL_Y+9, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot5 = Robot(START_CELL_X, START_CELL_Y+12, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot6 = Robot(START_CELL_X, START_CELL_Y+15, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robots = [robot1, robot2, robot3, robot4, robot5, robot6]
    ##to_remove
    robot1.set_path(4,6)
    # robot2.set_path(2,3)
    robots = [robot1]
    OD = ObstaclesDefiner(robots=robots, peoples=[people_julia])

    # очередь столов с заказами
    tables_queue = []
    for table in tables:
        entities.add(table)
    for robot in robots:
        entities.add(robot)
    for people in peoples:
        entities.add(people)



    while 1: # Основной цикл программы
        timer.tick(20)
        sleep(1)
        screen.blit(bg, (0, 0))      # Каждую итерацию необходимо всё перерисовывать

        for b in barriers:
            pf = Platform(b[0]*CELL_SIZE, b[1]*CELL_SIZE)
            entities.add(pf)


        robots.reverse()
        for robot in robots:
        # back
        #     # init pos/ came to base
        #     if robot.on_base() and robot.dest_description == ON_BASE:
        #         robot.client_count = 0
        #         if len(tables_queue) > 0:
        #             robot.get_next_client(tables_queue.pop(0))
        #             robot.client_count += 1
        #             robot.total_served_client_count += 1
        #         else:
        #             robot.set_path_to_base()
        #     # moving from base
        #     elif robot.on_base() and robot.dest_description == ON_CLIENT:
        #         pass
        #     # moving from client
        #     elif robot.on_client() and robot.dest_description == ON_BASE:
        #         if len(tables_queue) > 0 and robot.client_count <= 2:
        #             robot.get_next_client(tables_queue.pop(0))
        #             robot.client_count += 1
        #             robot.total_served_client_count += 1
        #     # came to client
        #     elif robot.on_client() and robot.dest_description == ON_CLIENT:
        #         robot.set_path_to_base()
        #         for table in tables:
        #             if robot.get_current_pos() == table.get_stay_point():
        #                 table.set_not_ready()
        #                 table.set_time_count(10)
        #
        #     # moving to base
        #     elif not robot.on_client() and not robot.on_base() and robot.dest_description == ON_BASE:
        #         if len(tables_queue) > 0 and robot.client_count < 2:
        #             robot.get_next_client(tables_queue.pop(0))
        #             robot.client_count += 1
        #             robot.total_served_client_count += 1
        #     # moving to client
        #     elif not robot.on_client() and not robot.on_base() and robot.dest_description == ON_CLIENT:
        #         pass #still move to client



            robot.execute(OD=OD, tables=tables, busy_tables=busy_tables, tables_queue=tables_queue, meals_queue=meals_queue, cooking_meals=cooking_meals)
            entities.draw(screen)
            pygame.display.update()
        for p in peoples:
            people.execute(OD=OD, tables=tables, busy_tables=busy_tables, tables_queue=tables_queue, meals_queue=meals_queue, cooking_meals=cooking_meals)
            entities.draw(screen)
            pygame.display.update()

        chef.cook()





        # add client
        # for table in tables:
        #     table.dec_time_count()
        #     if table.status == NOT_READY_STATUS and table not in tables_queue:
        #         if table.time_count <= 0:
        #             table.set_ready()
        #             tables_queue.append(table)


        #back
        # entities.draw(screen)

        #back
        # pygame.display.update()     # обновление и вывод всех изменений на экран
        # print('updated display')


if __name__ == "__main__":
    main()

