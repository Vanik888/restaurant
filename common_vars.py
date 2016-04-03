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

