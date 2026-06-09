# controller/hotkeys.py — хоткеи по физическим клавишам (работают на любой раскладке)

import pygame

# SDL scancodes для QWERTY-позиций
_SC_Q = 20
_SC_W = 26
_SC_E = 8
_SC_P = 19
_SC_ESCAPE = 41


def _pressed(event, scancode, *keys):
    if event.type != pygame.KEYDOWN:
        return False
    if event.scancode == scancode:
        return True
    return event.key in keys


def is_escape(event):
    return _pressed(event, _SC_ESCAPE, pygame.K_ESCAPE)


def is_peashooter(event):
    return _pressed(event, _SC_Q, pygame.K_q, ord('q'), ord('Q'), ord('й'), ord('Й'))


def is_boxer(event):
    return _pressed(event, _SC_W, pygame.K_w, ord('w'), ord('W'), ord('ц'), ord('Ц'))


def is_machinegun(event):
    return _pressed(event, _SC_E, pygame.K_e, ord('e'), ord('E'), ord('у'), ord('У'))


def is_pause(event):
    return _pressed(event, _SC_P, pygame.K_p, ord('p'), ord('P'), ord('з'), ord('З'))
