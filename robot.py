#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from itertools import product

from pygame import *
from astar.astar_grid import *

from common_vars import TABLE_STATUSES
from common_vars import ROBOT_STATUSES
from dymanic_elements_mixin import DynamicElement


CELL_SIZE = 32
MOVE_SPEED = CELL_SIZE
WIDTH = CELL_SIZE
HEIGHT = CELL_SIZE
COLOR = "#888888"


class Robot(sprite.Sprite, DynamicElement):
    def __init__(self, name, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers, init_x, init_y, trajectory_color):
        sprite.Sprite.__init__(self)
        self.name = name
        self.cell_start_x = cell_start_x
        self.cell_start_y = cell_start_y
        self.cell_current_x = init_x
        self.cell_current_y = init_y
        self.client_count = 0
        self.total_served_client_count = 0
        self.dest_description = ROBOT_STATUSES['NO_TASKS']
        self.tables = tables
        self.cart_field_width = cart_field_width
        self.cart_field_height = cart_field_height
        self.barriers = barriers

        self.xvel = 0   #скорость перемещения. 0 - стоять на месте
        self.yvel = 0 # скорость вертикального перемещения

        self.image = Surface((WIDTH, HEIGHT))
        self.image = image.load("static/Robot-icon_22_22.png")
        # self.rect = Rect(self.cell_start_x*CELL_SIZE, self.cell_start_y*CELL_SIZE, WIDTH, HEIGHT) # прямоугольный объект
        self.rect = Rect(init_x*CELL_SIZE, init_y*CELL_SIZE, WIDTH, HEIGHT) # прямоугольный объект
        self.path = None

        self.current_task = None
        self.tasks = [ self.update_task]
        self.table = None
        self.conversation_limit = 5
        self.conversation_count = 0
        self.trajectory_color = trajectory_color


    def on_client(self):
        return (self.cell_current_x, self.cell_current_y) == self.client_destination

    def on_base(self):
        return (self.cell_current_x, self.cell_current_y) == (self.cell_start_x, self.cell_start_y)

    def get_current_pos(self):
        return self.cell_current_x, self.cell_current_y


    def set_path_to_base(self, *args, **kwargs):
        entities = kwargs['entities']
        destination = (self.cell_start_x, self.cell_start_y)
        self.set_path(*destination, entities=entities)
        self.tasks.append(self.move_to_base)

    # идем за едой
    def get_waiting_meal(self, *args, **kwargs):
        meals_queue = kwargs['meals_queue']
        if len(meals_queue) > 0:
            self.meal = meals_queue.pop(0)
            self.table = self.meal.table
            # по пути не отвлекаемся, приносим идем за едой
            self.dest_description = ROBOT_STATUSES['BRING_MEAL']
            # уже на базе, можно сразу забрать еду
            if self.on_base():
                print('%s is already on base move meal to table' % self.name)
                self.tasks.append(self.set_path_to_table)
            else:
                print('%s move to base to get meal and then move to table' % self.name)
                self.tasks.append(self.set_path_to_table)
                self.tasks.append(self.set_path_to_base)

    def move_to_base(self, *args, **kwargs):
        OD = kwargs['OD']
        tables_queue = kwargs['tables_queue']
        meals_queue = kwargs['meals_queue']
        entities = kwargs['entities']
        self.make_step(OD, entities=entities)

        # пока шли- появлились заказы или приготовилась
        #  еда и при этом мы не уносим тарелки и не идем за едой
        if (len(tables_queue) > 0 or len(meals_queue) > 0) and\
            self.dest_description == ROBOT_STATUSES['NO_TASKS']:
            if len(tables_queue) >= len(meals_queue):
                self.tasks.append(self.get_waiting_table)
            else:
                # пойти за едой
                self.tasks.append(self.get_waiting_meal)
        else:
            if not self.on_base():
                self.tasks.append(self.move_to_base)

    # выполняем задачу
    def execute(self, *args, **kwargs):
        print('%s: execute task' % self.name)
        if len(self.tasks) > 0:
            self.current_task = self.tasks.pop()
            self.current_task(*args, **kwargs)
        else:
            print('%s: has no task' % self.name)
            self.tasks.append(self.update_task)

    # выбираем стол, к которому подойти
    def get_waiting_table(self, *args, **kwargs):
        tables_queue = kwargs['tables_queue']
        if len(tables_queue) > 0:
            self.table = tables_queue.pop(0)
            self.tasks.append(self.set_path_to_table)


    # сетим путь до стола
    def set_path_to_table(self, *args, **kwargs):
        entities = kwargs['entities']
        destination = self.table.get_stay_point()
        self.set_path(*destination, entities=entities)
#        self.dest_description = ON_CLIENT
        self.tasks.append(self.move_to_table)

    # идем к столу
    def move_to_table(self, *args, **kwargs):
        OD = kwargs['OD']
        entities = kwargs['entities']
        self.make_step(OD, entities)
        if len(self.path) > 0:
            self.tasks.append(self.move_to_table)
        # если дошли до стола
        if len(self.path) == 0 and self.get_current_pos() == self.table.get_stay_point():
            self.tasks.append(self.conversation)

    # общаемся с клиентом
    def conversation(self, *args, **kwargs):
        cooking_meals = kwargs['cooking_meals']
        self.conversation_count += 1
        # поговорили => берем новую задачу
        if self.conversation_count > self.conversation_limit:
            if self.table.status == TABLE_STATUSES['WAITING_TO_MAKE_ORDER']:
                # теперь ждем еду
                self.table.set_status(TABLE_STATUSES['WAITING_MEAL'])
                # свободны для других задач
                self.dest_description = ROBOT_STATUSES['NO_TASKS']
                cooking_meals.append(self.table.order)
            elif self.table.status == TABLE_STATUSES['WAITING_MEAL']:
                self.table.set_status(TABLE_STATUSES['EATING'])
                # свободны для других задач
                self.dest_description = ROBOT_STATUSES['NO_TASKS']
            elif self.table.status == TABLE_STATUSES['WAITING_BILL']:
                self.table.set_status(TABLE_STATUSES['NOT_READY'])
                # уносим тарелки
                self.dest_description = ROBOT_STATUSES['CLEAN_TABLE']
            self.tasks.append(self.update_task)
            print('%s: get next task' % self.name)
        else:
            self.tasks.append(self.conversation)
            print('%s: make conversation' % self.name)

    def update_task(self, *args, **kwargs):
        tables_queue = kwargs['tables_queue']
        meals_queue = kwargs['meals_queue']
        # нечего делать => идем на базу
        if len(tables_queue) == 0 and len(meals_queue) == 0:
            self.tasks.append(self.set_path_to_base)
            print('%s: table queue and meals queue are empty. nothing to do' %self.name)

        elif len(tables_queue) >= len(meals_queue):
            self.tasks.append(self.get_waiting_table)
        elif len(tables_queue) < len(meals_queue):
            self.tasks.append(self.get_waiting_meal)

