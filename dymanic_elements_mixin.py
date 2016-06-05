# -*- coding: utf-8 -*-

from itertools import product

from path_cell import PathCell
from astar.astar_grid import AStarGrid
from astar.astar_grid import AStarGridNode

CELL_SIZE = 32

class DynamicElement():
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

    def get_tables_area(self):
        tables_area = []
        for t in self.tables:
            tables_area += t.get_table_area()
        return tables_area

    def remove_trajectory_images(self, entities):
        if self.trajectory:
            for t in self.trajectory:
                entities.remove(t)

    def set_trajectory(self, entities):
        self.trajectory = []
        for p in self.path:
            self.trajectory.append(PathCell(p.x, p.y, CELL_SIZE, self.trajectory_color))

        high_priority_elements = []
        for s in entities.sprites():
            high_priority_elements.append(s)
        entities.empty()
        for t in self.trajectory:
            entities.add(t)
        for e in entities.sprites():
            print e
        for e in high_priority_elements:
            entities.add(e)

    def set_path(self, cell_end_x, cell_end_y, dyn_obstacles=[], entities=[]):
        graph, nodes = self.make_graph(self.cart_field_width, self.cart_field_height, self.barriers, dyn_obstacles)
        paths = AStarGrid(graph)
        self.path = paths.search(
            nodes[self.cell_current_x][self.cell_current_y],
            nodes[cell_end_x][cell_end_y]
        )
        self.set_trajectory(entities)
        self.path.pop(0)

    def make_step(self, od, entities):
        # self.trajectory_changed = False
        self.remove_trajectory_images(entities)
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
                    print('%s: skip the step' % (self.name))
                elif not od.no_peoples(next_cell.x, next_cell.y):
                    print('%s: there are people on (x=%s; y=%s)' % (self.name, next_cell.x, next_cell.y))
                    print('%s: skip the step' % (self.name))


    # принтим старый путь и новый
    def print_path_diff(self, old_path, new_path):
        old_path = [(p.x, p.y)for p in old_path]
        new_path = [(p.x, p.y)for p in new_path]
        print('%s: old path: %s' % (self.name, str(old_path)))
        print('%s: new path: %s' % (self.name, str(new_path)))

     # создаем новый путь с учетом препятствия x, y
    def update_path(self, obstacle_x, obstacle_y, entities):
        destination = self.path[len(self.path)-1].get_cart_coordinates()
        old_path = self.path
        self.set_path(*destination, dyn_obstacles=[(obstacle_x, obstacle_y)], entities=entities)
        new_path = self.path
        self.print_path_diff(old_path, new_path)
