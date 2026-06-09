# Класс снарядов

import math
from settings import SCREEN_W, SCREEN_H


def _rects_overlap(r1, r2):
    return (
        r1[0] < r2[0] + r2[2]
        and r1[0] + r1[2] > r2[0]
        and r1[1] < r2[1] + r2[3]
        and r1[1] + r1[3] > r2[1]
    )


class Projectile:
    def __init__(self, ptype, x, y, target_x, target_y, damage, speed, size):
        self.ptype = ptype
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.speed = speed
        self.size = size
        self.active = True

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            dist = 1
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed

    def update(self, dt, zombies):
        if not self.active:
            return None

        self.x += self.vx * dt
        self.y += self.vy * dt

        my_rect = (self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

        for zombie in zombies:
            if not zombie.is_vulnerable():
                continue
            if _rects_overlap(my_rect, zombie.get_rect()):
                zombie.take_damage(self.damage)
                self.active = False
                return zombie

        return None

    def is_out_of_bounds(self):
        margin = 80
        return (
            self.x < -margin
            or self.x > SCREEN_W + margin
            or self.y < -margin
            or self.y > SCREEN_H + margin
        )
