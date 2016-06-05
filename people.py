#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import operator
from itertools import product

from pygame import *
from astar.astar_grid import *

from common_vars import TABLE_STATUSES, PEOPLE_STATUSES
from orders import Lanch
from path_cell import PathCell
from robot import Robot
from dymanic_elements_mixin import DynamicElement


CELL_SIZE = 32
MOVE_SPEED = CELL_SIZE
WIDTH = CELL_SIZE
HEIGHT = CELL_SIZE
ON_CLIENT = 'on_client'
ON_BASE = 'on_base'
ON_TABLE = 'on_table'
ON_OUT = 'on_out'
COLOR = "#888888"
READY_TO_ORDER = 'ready_to_order'


class People(sprite.Sprite, DynamicElement):
    def __init__(self, name, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers, entries, game, screen):
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
        self.current_task = None
        self.status = PEOPLE_STATUSES['JUST_CAME']
        self.tasks = [self.move_to_dest,
                      self.get_out,
                      self.waiting_the_bill,
                      self.get_the_bill,
                      self.eating,
                      self.waiting_meal,
                      self.wait_to_make_order,
                      self.take_table,
                      self.move_to_dest,
                      self.get_free_table,
                      ]
        self.table = None
        self.eat_time = 3

        self.entries = entries
        self.game = game
        self.screen = screen
        self.trajectory = None
        self.trajectory_changed = False

    def eat(self):
        self.eat_time -= 1
        return self.eat_time != 0


    def on_base(self):
        return (self.cell_current_x, self.cell_current_y) == (self.cell_start_x, self.cell_start_y)

    def get_current_pos(self):
        return self.cell_current_x, self.cell_current_y

    # заняли столик
    def get_free_table(self, *args, **kwargs):
        tables = kwargs['tables']
        busy_tables = kwargs['busy_tables']
        entities = kwargs['entities']
        free_tables = {}
        for t in tables:
            if t not in busy_tables:
                # считаем расстояние для каждого из свободных столиков
                x, y = t.get_sit_point()
                free_tables[t] = sqrt((self.cell_current_x-x)**2 + (self.cell_current_y-y)**2)
        # если есть свободные столы
        if len(free_tables) > 0:
            # сортируем по длине пути
            t = sorted(free_tables.items(), key=operator.itemgetter(1))[0][0]
            busy_tables.append(t)
            self.table = t
            # установили путь до стола
            self.set_path_to_table(entities)
            return
        print('%s: all tables are busy' % self.name)
        self.tasks.append(self.get_free_table)

    # засетили путь до стола
    def set_path_to_table(self, entities):
        destination = self.table.get_sit_point()
        self.set_path(*destination, entities=entities)
        self.dest_description = ON_TABLE

    # шагаем до стола
    def move_to_dest(self, *args, **kwargs):
        OD = kwargs['OD']
        entities = kwargs['entities']
        self.make_step(OD, entities)
        if len(self.path) > 0:
            self.tasks.append(self.move_to_dest)

    # ждем официанта для заказа
    def wait_to_make_order(self, *args, **kwargs):
        # робот пришел к столу и мы с ним обсудили заказ
        if self.table.status == TABLE_STATUSES['WAITING_MEAL']:
            self.status == PEOPLE_STATUSES['WAITING_MEAL']
        else:
            # робот еще не пришел, ждем
            self.tasks.append(self.wait_to_make_order)

    # ждем официанта с заказом
    def waiting_meal(self, *args, **kwargs):
        # робот принес еду
        if self.table.status == TABLE_STATUSES['EATING']:
            self.status = PEOPLE_STATUSES['EATING']
        # робот еще не принес еду
        else:
            print('%s waiting meal' % self.name)
            self.tasks.append(self.waiting_meal)

    # задача- поесть
    def eating(self, *args, **kwargs):
        if self.status == PEOPLE_STATUSES['EATING']:
            # если еще не доели
            if self.eat():
                print('%s eating' % self.name)
                self.tasks.append(self.eating)
            else:
                print('%s ended eating' % self.name)

    # вызываем официанта для того, чтобы получить счет
    def get_the_bill(self, *args, **kwargs):
        tables_queue = kwargs['tables_queue']
        if self.status == PEOPLE_STATUSES['EATING']:
            self.table.set_status(TABLE_STATUSES['WAITING_BILL'])
            self.status = PEOPLE_STATUSES['WAITING_BILL']
            tables_queue.append(self.table)
            print('%s calls waiter for bill' % self.name)

    # ждем робота
    def waiting_the_bill(self, *args, **kwargs):
        # пока робот не пришел
        if self.table.status == TABLE_STATUSES['WAITING_BILL']:
            print('%s waiting the bill' % self.name)
            self.tasks.append(self.waiting_the_bill)
        else:
            print('%s robot brang the bill' % self.name)

    # идем на базовую точку, чистим стол
    def get_out(self, *args, **kwargs):
        print('%s goes to out' % self.name)
        entities = kwargs['entities']
        self.set_path_to_out(entities)
        self.table.set_status(TABLE_STATUSES['NOT_READY'])

    # устанавливаем путь до отхода
    def set_path_to_out(self, entities):
        destination = (self.cell_start_x, self.cell_start_y)
        print("out x=%s, y=%s" % destination)
        self.set_path(*destination, entities=entities)
        self.dest_description = ON_OUT


    # делаем стол красным и кладем задачу в очередь для робота
    def take_table(self, *args, **kwargs):
        tables_queue = kwargs['tables_queue']
        # еще не делали заказ и уже за столом=> зовем официанта
        if self.status == PEOPLE_STATUSES['JUST_CAME'] and (self.cell_current_x, self.cell_current_y) == self.table.get_sit_point():
            print('call waitress')
            print('self table people')
            print(self.table)
            self.status = PEOPLE_STATUSES['WAITING_TO_MAKE_ORDER']
            self.table.set_status(TABLE_STATUSES['WAITING_TO_MAKE_ORDER'])
            self.table.order = Lanch(self.table)
            tables_queue.append(self.table)

    def execute(self, *args, **kwargs):
        if len(self.tasks) > 0:
            self.current_task = self.tasks.pop()
            self.current_task(*args, **kwargs)
        else:
            print('%s: has no tasks' % self.name)





