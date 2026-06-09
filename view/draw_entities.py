# view/draw_entities.py
# Функции рисования растений и зомби удалены — теперь используются PNG.
# Здесь остались только вспомогательные элементы, которые рисуются
# поверх спрайтов: полоска HP, анимация смерти, домик базы.

import pygame
import math


def draw_zombie_hp_bar(s, cx, cy, hp):
    w, h = 36, 5
    bx, by = cx - w//2, cy - 52
    pygame.draw.rect(s, (90, 0, 0),    (bx, by, w, h))
    pygame.draw.rect(s, (0, 200, 60),  (bx, by, int(w * hp), h))
    pygame.draw.rect(s, (0, 0, 0),     (bx, by, w, h), 1)


def draw_dying_effect(s, cx, cy, progress):
    """Вспышка-взрыв при гибели зомби (рисуется поверх позиции)."""
    n   = 7
    r   = int(14 + 12 * progress)
    dot = max(1, int(4 * (1 - progress)))
    col = (int(185*(1-progress)), int(215*(1-progress)), int(78*(1-progress)))
    for i in range(n):
        a  = math.radians(i * (360/n) + progress * 50)
        ex = cx + int(r * math.cos(a))
        ey = cy + int(r * math.sin(a))
        pygame.draw.circle(s, col, (ex, ey), dot)


def draw_base_icon(s, cx, cy, hp_pct):
    """Домик базы (рисуется примитивами — спрайта нет)."""
    def _r(col, x, y, w, h): pygame.draw.rect(s, col, (int(x), int(y), int(w), int(h)))
    def _p(col, pts): pygame.draw.polygon(s, col, [(int(x), int(y)) for x, y in pts])
    def _l(col, x1, y1, x2, y2): pygame.draw.line(s, col, (int(x1),int(y1)), (int(x2),int(y2)), 1)

    _r((40,40,38),    cx-26, cy-18, 52, 42)
    _r((182,152,108), cx-24, cy-16, 48, 40)
    _p((32,32,30),    [(cx-30,cy-18),(cx+30,cy-18),(cx,cy-44)])
    _p((152,62,40),   [(cx-28,cy-18),(cx+28,cy-18),(cx,cy-42)])
    _r((98,60,20),    cx-9,  cy+6,  18, 18)
    _r((152,202,222), cx-22, cy-10, 14, 13)
    _l((108,158,178), cx-15, cy-10, cx-15, cy+3)
    _l((108,158,178), cx-22, cy-4,  cx-8,  cy-4)

    bw = 48
    bx = cx - bw//2
    by = cy + 26
    pygame.draw.rect(s, (100, 0, 0), (bx, by, bw, 7))
    pygame.draw.rect(s, (0, 200, 0), (bx, by, int(bw * hp_pct), 7))
    pygame.draw.rect(s, (0, 0, 0),   (bx, by, bw, 7), 1)
