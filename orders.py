# -*- coding: utf-8 -*-


class AbstractOrder(object):
    def __init__(self):
        self.wait_time = 10
        self.is_ready = False
        self.table = None

    def cook(self):
        self.wait_time -= 1
        if self.wait_time == 0:
            self.is_ready = True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str("Table = (%s, %s) Wait time = %s" % (self.table.cell_x,self.table.cell_y , self.wait_time))


class Lanch(AbstractOrder):
    def __init__(self, table):
        super(Lanch, self).__init__()
        self.wait_time = 1
        self.table = table


class Dinner(AbstractOrder):
    def __init__(self, table):
        super(Dinner, self).__init__()
        self.wait_time = 10
        self.table = table




