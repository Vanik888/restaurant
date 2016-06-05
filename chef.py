# -*- coding: utf-8 -*-


class Chef():
    def __init__(self, cooking_meals, meals_queue):
        self.cooking_meals = cooking_meals
        self.meals_queue = meals_queue

    def cook(self):
        for x in range(len(self.cooking_meals)):
            m = self.cooking_meals.pop(0)
            m.cook()
            if m.is_ready:
                self.meals_queue.append(m)
                print("chef: %s: meal is ready" % m)
            else:
                self.cooking_meals.append(m)
