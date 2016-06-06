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
from common_vars import COLORS_TO_DIN_OBJECTS
from common_vars import COLORS

CELL_SIZE = 32
CART_WIDTH = 38
CART_HEIGHT = 24
WIN_WIDTH = CART_WIDTH * CELL_SIZE
WIN_HEIGHT = CART_HEIGHT * CELL_SIZE
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = COLORS['WHITE']


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
        no_robots = self.no_object(x, y, self.robots)
        no_peoples = self.no_object(x, y, self.peoples)
        return no_robots and no_peoples


class ColorsStorage():
    def __init__(self):
        self.count = 0

    def get_color(self):
        description, color = COLORS_TO_DIN_OBJECTS[self.count]
        self.count += 1
        return color


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
    bg.fill(BACKGROUND_COLOR)      # Заливаем поверхность сплошным цветом

    CS = ColorsStorage()                  # Возвращает свободные цвета для траекторий




    timer = pygame.time.Clock()
    entities = pygame.sprite.Group() # Все объекты
    trajectory_entities = pygame.sprite.Group()
    platforms = [] # то, во что мы будем врезаться или опираться


    # level = [
    #        "-------------------------",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-                       -",
    #        "-------------------------"]

    level = [ "----------------------------------------",
              "-            -                         -",
              "-            -                         -",
              "-            ---------------------------",
              "-                                      -",
              "-                                      -",
              "-            ---------------------     -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-                                      -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "-           -                          -",
              "----------------------------------------"
              ]

    level = [ "--------------------------------------",
              "-    -       -                       -",
              "-            -                       -",
              "-            -                       -",
              "-            -------------------------",
              "-                                    -",
              "-    -                               -",
              "------                               -",
              "-            --------------------    -",
              "-                                    -",
              "-                                    -",
              "-                                    -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "-           -                        -",
              "----------------------------------------"
              ]

    barriers = get_static_barriers(level)

    START_CELL_X = 14
    START_CELL_Y = 4
    # table1 = Table(3, 24, CELL_SIZE)
    table2 = Table(3, 18, CELL_SIZE)
    table3 = Table(3, 14, CELL_SIZE)
    table4 = Table(3, 10, CELL_SIZE)
    # table5 = Table(7, 24, CELL_SIZE)
    table6 = Table(7, 18, CELL_SIZE)
    table7 = Table(7, 14, CELL_SIZE)
    table8 = Table(7, 10, CELL_SIZE)

    # ряд1
    table9 = Table(15, 9, CELL_SIZE)
    table10 = Table(20, 9, CELL_SIZE)
    table11 = Table(25, 9, CELL_SIZE)
    table12 = Table(30, 9, CELL_SIZE)

    # ряд2
    table13 = Table(15, 14, CELL_SIZE)
    table14 = Table(20, 14, CELL_SIZE)
    table15 = Table(25, 14, CELL_SIZE)
    table16 = Table(30, 14, CELL_SIZE)

    # ряд3
    table17 = Table(15, 19, CELL_SIZE)
    table18 = Table(20, 19, CELL_SIZE)
    table19 = Table(25, 19, CELL_SIZE)
    table20 = Table(30, 19, CELL_SIZE)

    # ряд4
    table21 = Table(15, 24, CELL_SIZE)
    table22 = Table(20, 24, CELL_SIZE)
    table23 = Table(25, 24, CELL_SIZE)
    table24 = Table(30, 24, CELL_SIZE)

    tables = [table4, table2, table3, table8, table6, table7,
              table9, table10, table11, table12,
              table13, table14, table15, table16,
              table17, table18, table19, table20,
              ]
    busy_tables = []
    meals_queue = []
    cooking_meals = []

    chef = Chef(cooking_meals=cooking_meals, meals_queue=meals_queue)
    people_julia = People('Julia', 8, 5, tables, CART_WIDTH, CART_HEIGHT, barriers, CS.get_color())
    people_anna = People('ANNA', 10, 3, tables, CART_WIDTH, CART_HEIGHT, barriers, CS.get_color())
    people_kristy = People('Kristy', 12, 5, tables, CART_WIDTH, CART_HEIGHT, barriers, CS.get_color())
    peoples = [people_julia, people_anna]

    robot1 = Robot('r1', 14, 5, tables, CART_WIDTH, CART_HEIGHT, barriers, 10, 4, CS.get_color())
    robot2 = Robot('r2', 16, 5, tables, CART_WIDTH, CART_HEIGHT, barriers, 11,4, CS.get_color())
    robot3 = Robot('r3', 17, 5, tables, CART_WIDTH, CART_HEIGHT, barriers, 11,5, CS.get_color())
    robot4 = Robot('r4', 16, 6, tables, CART_WIDTH, CART_HEIGHT, barriers, 12,5, CS.get_color())
    # robot3 = Robot('r3', 20, 4, tables, CART_WIDTH, CART_HEIGHT, barriers, 11,5)
    # robot2 = Robot('r2', START_CELL_X, START_CELL_Y+3, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot3 = Robot(START_CELL_X, START_CELL_Y+6, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot4 = Robot(START_CELL_X, START_CELL_Y+9, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot5 = Robot(START_CELL_X, START_CELL_Y+12, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robot6 = Robot(START_CELL_X, START_CELL_Y+15, tables, CART_WIDTH, CART_HEIGHT, barriers)
    # robots = [robot1, robot2, robot3, robot4, robot5, robot6]
    ##to_remove
    # robot1.set_path(4,6)
    # robot2.set_path(2,3)
    robots = [robot1, robot2, robot3, robot4]
    paths = []
    OD = ObstaclesDefiner(robots=robots, peoples=peoples)

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
            robot.execute(OD=OD, tables=tables, busy_tables=busy_tables, tables_queue=tables_queue, meals_queue=meals_queue, cooking_meals=cooking_meals, entities=trajectory_entities)
            trajectory_entities.draw(screen)
            entities.draw(screen)
            pygame.display.update()
            screen.blit(bg, (0, 0))
        for p in peoples:
            p.execute(OD=OD, tables=tables, busy_tables=busy_tables, tables_queue=tables_queue, meals_queue=meals_queue, cooking_meals=cooking_meals, entities=trajectory_entities)
            trajectory_entities.draw(screen)
            entities.draw(screen)
            pygame.display.update()
            screen.blit(bg, (0, 0))

        chef.cook()

if __name__ == "__main__":
    main()

