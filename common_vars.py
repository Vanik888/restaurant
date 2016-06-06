# -*- coding: utf-8 -*-

TABLE_STATUSES = {
    'WAITING_TO_MAKE_ORDER': 01,
    'WAITING_MEAL':          02,
    'EATING':                03,
    'WAITING_BILL':          04,
    'WAITING_CLEAN':         05,
    'NOT_READY':             06,
}

PEOPLE_STATUSES = {
    'JUST_CAME':             01,
    'WAITING_TO_MAKE_ORDER': 02,
    'WAITING_MEAL':          03,
    'EATING':                04,
    'WAITING_BILL':          05,
    'WAITING_CLEAN':         06,
    'GO_HOME':               07,
}

ROBOT_STATUSES = {
    'NO_TASKS':    01,
    'CLEAN_TABLE': 02,
    'BRING_MEAL':  03,
}

COLORS = {
    'BLUE':        (0, 0, 255),
    'RED':         (255, 0, 0),
    'ORANGE':      (230, 140, 20),
    'YELLOW':      (240, 255, 0),
    'PURPLE':      (180, 55, 220),
    'PINK':        (255, 100, 100),
    'WHITE':       (237, 237, 237),
    'TRANSPARENT': (0, 0, 0),
}



COLORS_TO_DIN_OBJECTS = [
    ('blue_1', (15, 15, 79)),
    ('green_1', (136, 201, 87)),
    ('gray_1', (166, 166, 166)),

    ('blue_2', (5, 99, 240)),
    ('green_2', (28, 69, 0)),
    ('gray_3', (95, 95, 95)),

    ('blue_3', (74, 74, 135)),
    ('green_3', (132, 219, 127)),
    ('green_4', (170, 184, 121)),

    ('blue_5', (153, 174, 207)),
]
