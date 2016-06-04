#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from itertools import product

from pygame import *
from astar.astar_grid import *

from common_vars import TABLE_STATUSES
from common_vars import ROBOT_STATUSES

CELL_SIZE = 32
MOVE_SPEED = CELL_SIZE
WIDTH = CELL_SIZE
HEIGHT = CELL_SIZE
COLOR = "#888888"


class Robot(sprite.Sprite):
    def __init__(self, name, cell_start_x, cell_start_y, tables, cart_field_width, cart_field_height, barriers, init_x, init_y):
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
        print('sold path: ' + str(old_path))
        print('new path: ' + str(new_path))




    def set_path_to_base(self, *args, **kwargs):
        destination = (self.cell_start_x, self.cell_start_y)
        self.set_path(*destination)
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


        # destination = (self.cell_start_x, self.cell_start_y)
        # self.set_path()
        #


    def move_to_base(self, *args, **kwargs):
        OD = kwargs['OD']
        tables_queue = kwargs['tables_queue']
        meals_queue = kwargs['meals_queue']
        self.make_step(OD)

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
        destination = self.table.get_stay_point()
        self.set_path(*destination)
#        self.dest_description = ON_CLIENT
        self.tasks.append(self.move_to_table)

    # идем к столу
    def move_to_table(self, *args, **kwargs):
        OD = kwargs['OD']
        self.make_step(OD)
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

