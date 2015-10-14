#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import pygame

from pygame import *
from blocks import *
from player import *

WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#004000"


def read_commands(commands_abs_path):
    with open(commands_abs_path, 'r') as f:
        if os.stat(commands_abs_path).st_size != 0:
            smbl = int(f.readline())
        else: smbl = -1
        return smbl


def clean_commands_file(commands_abs_path):
    with open(commands_abs_path, 'w+'):
        pass


def main():
    cmd_file = '/home/vanik/darwin/speach-detector/speech-client/stat/cmd'
    pygame.init() # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY) # Создаем окошко
    pygame.display.set_caption("Super Mario Boy") # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)) # Создание видимой поверхности
                                          # будем использовать как фон
    bg.fill(Color(BACKGROUND_COLOR))      # Заливаем поверхность сплошным цветом

    timer = pygame.time.Clock()
    hero = Player(55, 55)
    left = False
    right = False
    up = False
    down = False

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

            if read_commands(cmd_file) == 0:
                up = True
                down = False
                left = False
                right = False
            if read_commands(cmd_file) == 1:
                up = False
                down = True
                left = False
                right = False
            if read_commands(cmd_file) == 2:
                up = False
                down = False
                left = False
                right = True

            if read_commands(cmd_file) == 3:
                up = False
                down = False
                left = True
                right = False


            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
                clean_commands_file(cmd_file)
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
                clean_commands_file(cmd_file)
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
                clean_commands_file(cmd_file)
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
                clean_commands_file(cmd_file)

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

        hero.update(left, right, up, down, platforms) # передвижение
        entities.draw(screen)

        pygame.display.update()     # обновление и вывод всех изменений на экран


if __name__ == "__main__":
    main()

