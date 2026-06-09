# Класс зомби

import math
from settings import ZOMBIE_STATS, TILE_SIZE


class ZombieState:
    WALKING = "walking" 
    DYING = "dying" # анимация смерти
    DEAD = "dead"


class Zombie:
    DEATH_ANIM_TIME = 0.45

    def __init__(self, ztype, path_pixels):
        stats = ZOMBIE_STATS[ztype]
        self.ztype = ztype

        # Характеристики
        self.speed = stats["speed"] * TILE_SIZE
        self.max_hp = stats["hp"]
        self.hp = stats["hp"]
        self.base_damage = stats["base_damage"]

        self.x = float(path_pixels[0][0])
        self.y = float(path_pixels[0][1])

        # Путь
        self.path = path_pixels
        self.path_index = 1
        
        self.state = ZombieState.WALKING
        self.die_timer = 0.0

        self.reached_base = False

        self.radius = 20


    def take_damage(self, amount):
        if self.state != ZombieState.WALKING:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self._start_dying()

    def is_vulnerable(self):
        return self.state == ZombieState.WALKING

    def is_dead(self):
        return self.state == ZombieState.DEAD

    def _start_dying(self):
        self.state = ZombieState.DYING
        self.die_timer = self.DEATH_ANIM_TIME

    def update(self, dt):
        self.reached_base = False

        if self.state == ZombieState.DYING:
            self.die_timer -= dt
            if self.die_timer <= 0:
                self.state = ZombieState.DEAD
            return

        if self.state == ZombieState.DEAD:
            return

        if self.path_index >= len(self.path):
            self.reached_base = True
            return

        tx, ty = self.path[self.path_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        move = self.speed * dt

        if dist <= move + 1:
            self.x = float(tx)
            self.y = float(ty)
            self.path_index += 1
        else:
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

    def get_rect(self):
        r = self.radius
        return (self.x - r, self.y - r, r * 2, r * 2)


    @property
    def hp_percent(self):
        return self.hp / self.max_hp

    @property
    def die_progress(self):
        if self.state != ZombieState.DYING:
            return 0.0
        return 1.0 - (self.die_timer / self.DEATH_ANIM_TIME)

    @property
    def direction(self):
        if self.path_index >= len(self.path):
            return (1, 0)
        tx, ty = self.path[self.path_index]
        dx = tx - self.x
        dy = ty - self.y
        if abs(dx) >= abs(dy):
            return (1, 0) if dx >= 0 else (-1, 0)
        else:
            return (0, 1) if dy >= 0 else (0, -1)
