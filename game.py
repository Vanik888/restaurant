#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import pygame

from itertools import product
from pygame import *
from blocks import *
from robot import *
from astar.astar_grid import *


CELL_SIZE = 32
CART_WIDTH = 25
CART_HEIGHT = 20
WIN_WIDTH = CART_WIDTH * CELL_SIZE
WIN_HEIGHT = CART_HEIGHT * CELL_SIZE
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004000"


def make_graph(width, height):
    nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
    graph = {}
    for x, y in product(range(width), range(height)):
        node = nodes[x][y]
        graph[node] = []
        for i, j in product([-1, 0, 1], [-1, 0, 1]):
            if not (0 <= x + i < width):
                continue
            if not (0 <= y + j < height):
                continue
            graph[nodes[x][y]].append(nodes[x+i][y+j])
    return graph, nodes


def main():
    pygame.init() # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY) # Создаем окошко
    pygame.display.set_caption("Robot field") # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)) # Создание видимой поверхности
                                          # будем использовать как фон
    bg.fill(Color(BACKGROUND_COLOR))      # Заливаем поверхность сплошным цветом

    timer = pygame.time.Clock()
    hero = Robot(CELL_SIZE*1, CELL_SIZE*1)
    left = False
    right = False
    up = False
    down = False

    graph, nodes = make_graph(CART_HEIGHT, CART_WIDTH)
    paths = AStarGrid(graph)
    start, end = nodes[2][2], nodes[4][4]
    path = paths.search(start, end)
    hero.set_path(path)


    entities = pygame.sprite.Group() # Все объекты
    platforms = [] # то, во что мы будем врезаться или опираться
    entities.add(hero)

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

    while 1: # Основной цикл программы
        timer.tick(60)
        for e in pygame.event.get(): # Обрабатываем события
            if e.type == QUIT:
                raise SystemExit, "QUIT"

            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True

            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False

        screen.blit(bg, (0, 0))      # Каждую итерацию необходимо всё перерисовывать
        x = 0
        y = 0

        for row in level:
            for col in row:
                if col == "-":
                    pf = Platform(x, y)
                    entities.add(pf)
                    platforms.append(pf)
                x += PLATFORM_WIDTH
            y += PLATFORM_HEIGHT
            x = 0

        # hero.update(left, right, up, down, platforms) # передвижение
        hero.move()
        entities.draw(screen)

        pygame.display.update()     # обновление и вывод всех изменений на экран


if __name__ == "__main__":
    main()

