#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import operator
from itertools import product

from pygame import *
from astar.astar_grid import *

from common_vars import TABLE_STATUSES, PEOPLE_STATUSES
from orders import Lanch
from path_cell import PathCell


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


class People(sprite.Sprite):
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

        self.set_trajectory()

        self.path.pop(0)

    def remove_trajectory_images(self, entities):
        for c in self.trajectory:
            entities.remove(c)

    def draw_path(self, entities):
        if self.path is not None:
            if self.trajectory_changed:
                for c in self.trajectory:
                    entities.add(c)
            else:
                for c in self.trajectory:
                    entities.remove(c)


    def set_trajectory(self):
        self.trajectory = []
        self.trajectory_changed = True
        for p in self.path:
            self.trajectory.append(PathCell(p.x, p.y, CELL_SIZE))

    def on_client(self):
        return (self.cell_current_x, self.cell_current_y) == self.client_destination

    def on_base(self):
        return (self.cell_current_x, self.cell_current_y) == (self.cell_start_x, self.cell_start_y)

    def get_current_pos(self):
        return self.cell_current_x, self.cell_current_y

    def make_step(self, od, entities):
        self.trajectory_changed = False
        if len(self.path) > 0:
            next_cell = self.path.pop(0)
            print(next_cell.x, next_cell.y)
            if (od.is_clear(next_cell.x, next_cell.y)):
                self.rect.x = next_cell.x * CELL_SIZE
                self.rect.y = next_cell.y * CELL_SIZE
                self.cell_current_x = next_cell.x
                self.cell_current_y = next_cell.y
            # не последний шаг и есть препятствия => перестраиваем маршрут
            elif len(self.path) != 0:
                print('%s: current state is  (x=%s; y=%s)' %(self.name, self.cell_current_x, self.cell_current_y))
                if not od.no_robots(next_cell.x, next_cell.y):
                    print('%s: there are robot on (x=%s; y=%s)' % (self.name, next_cell.x, next_cell.y))
                    self.update_path(next_cell.x, next_cell.y, entities)
                elif not od.no_peoples(next_cell.x, next_cell.y):
                    self.update_path(next_cell.x, next_cell.y, entities)
                    print('%s: there are people on (x=%s; y=%s)' % (self.name, next_cell.x, next_cell.y))
            else:
                if not od.no_robots(next_cell.x, next_cell.y):
                    print('%s: there are robot on (x=%s; y=%s)' % (self.name, next_cell.x, next_cell.y))
                    print('%s: skip the step')
                elif not od.no_peoples(next_cell.x, next_cell.y):
                    print('%s: there are people on (x=%s; y=%s)' % (self.name, next_cell.x, next_cell.y))
                    print('%s: skip the step')


     # создаем новый путь с учетом препятствия x, y
    def update_path(self, obstacle_x, obstacle_y, entities):
        print("%s: dest is (x=%s, y=%s)" % (self.name, self.path[0].get_cart_coordinates()[0], self.path[0].get_cart_coordinates()[1]))
        print("%s: len=%s" % (self.name, str(len(self.path))))
        destination = self.path[len(self.path)-1].get_cart_coordinates()
        self.remove_trajectory_images(entities)
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


    def set_path_to_base(self):
        destination = (self.cell_start_x, self.cell_start_y)
        self.set_path(*destination)
        self.dest_description = ON_BASE

    def get_next_client(self, client):
        destination = client.get_stay_point()
        self.client_destination = destination
        self.set_path(*destination)
        self.dest_description = ON_CLIENT

    # заняли столик
    def get_free_table(self, *args, **kwargs):
        tables = kwargs['tables']
        busy_tables = kwargs['busy_tables']
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
            self.set_path_to_table()
            return
        print('%s: all tables are busy' % self.name)
        self.tasks.append(self.get_free_table)

    # засетили путь до стола
    def set_path_to_table(self):
        destination = self.table.get_sit_point()
        self.set_path(*destination)
        self.dest_description = ON_TABLE

    # шагаем до стола
    def move_to_dest(self, *args, **kwargs):
        # if not self.path:
        #     self.set_path_to_table()
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
        self.set_path_to_out()
        self.table.set_status(TABLE_STATUSES['NOT_READY'])

    # устанавливаем путь до отхода
    def set_path_to_out(self):
        destination = (self.cell_start_x, self.cell_start_y)
        print("out x=%s, y=%s" % destination)
        self.set_path(*destination)
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
            print('people have no task')





