# Растения, зомби и снаряды + волны

import math
import random
from settings import (
    PLANT_STATS, TILE_SIZE, GRID_X, GRID_Y,
    PEASHOOTER, BOXER, MACHINEGUN,
    ZOMBIE_STATS, SCREEN_W, SCREEN_H,
)


# Растения
class Plant:
    def __init__(self, ptype, col, row):
        stats = PLANT_STATS[ptype]
        self.ptype = ptype
        self.col   = col
        self.row   = row
        self.damage        = stats["damage"]
        self.range_px      = stats["range"] * TILE_SIZE
        self.attack_rate   = stats["attack_rate"]
        self.has_projectile= stats["has_projectile"]
        self.attack_cooldown = 0.0
        self.x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
        self.y = GRID_Y + row * TILE_SIZE + TILE_SIZE // 2

    def update(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def can_attack(self):
        return self.attack_cooldown <= 0

    def do_attack(self):
        self.attack_cooldown = 1.0 / self.attack_rate

    def get_target(self, zombies_in_range):
        alive = [z for z in zombies_in_range if z.is_vulnerable()]
        if not alive:
            return None
        alive.sort(key=lambda z: -z.path_index)
        return alive[0]


class Peashooter(Plant):
    def __init__(self, col, row): super().__init__(PEASHOOTER, col, row)

class Boxer(Plant):
    def __init__(self, col, row): super().__init__(BOXER, col, row)

class MachineGun(Plant):
    def __init__(self, col, row): super().__init__(MACHINEGUN, col, row)


def create_plant(ptype, col, row):
    factories = {PEASHOOTER: Peashooter, BOXER: Boxer, MACHINEGUN: MachineGun}
    cls = factories.get(ptype)
    if cls is None:
        raise ValueError(f"Неизвестный тип растения: {ptype}")
    return cls(col, row)


# Зомби

class ZombieState:
    WALKING = "walking"
    DYING   = "dying"
    DEAD    = "dead"


class Zombie:
    DEATH_ANIM_TIME = 0.45

    def __init__(self, ztype, path_pixels):
        stats = ZOMBIE_STATS[ztype]
        self.ztype       = ztype
        self.speed       = stats["speed"] * TILE_SIZE
        self.max_hp      = stats["hp"]
        self.hp          = stats["hp"]
        self.base_damage = stats["base_damage"]
        self.x           = float(path_pixels[0][0])
        self.y           = float(path_pixels[0][1])
        self.path        = path_pixels
        self.path_index  = 1
        self.state       = ZombieState.WALKING
        self.die_timer   = 0.0
        self.reached_base= False
        self.radius      = 20

    def take_damage(self, amount):
        if self.state != ZombieState.WALKING:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.state     = ZombieState.DYING
            self.die_timer = self.DEATH_ANIM_TIME

    def is_vulnerable(self): return self.state == ZombieState.WALKING
    def is_dead(self):       return self.state == ZombieState.DEAD

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
        dx, dy = tx - self.x, ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        move = self.speed * dt
        if dist <= move + 1:
            self.x, self.y = float(tx), float(ty)
            self.path_index += 1
        else:
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

    def get_rect(self):
        r = self.radius
        return (self.x - r, self.y - r, r * 2, r * 2)

    @property
    def hp_percent(self):  return self.hp / self.max_hp

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
        dx, dy = tx - self.x, ty - self.y
        if abs(dx) >= abs(dy):
            return (1, 0) if dx >= 0 else (-1, 0)
        return (0, 1) if dy >= 0 else (0, -1)


# Снаряды 

def _rects_overlap(r1, r2):
    return (r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0]
            and r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1])


class Projectile:
    def __init__(self, ptype, x, y, target_x, target_y, damage, speed, size):
        self.ptype  = ptype
        self.x      = float(x)
        self.y      = float(y)
        self.damage = damage
        self.speed  = speed
        self.size   = size
        self.active = True
        dx, dy = target_x - x, target_y - y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
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
        m = 80
        return self.x < -m or self.x > SCREEN_W + m or self.y < -m or self.y > SCREEN_H + m


# Волны

class WaveManager:
    BETWEEN_WAVE_DELAY = 10.0
    SPAWN_INTERVAL     = 2.5
    FIRST_WAVE_DELAY   = 5.0

    def __init__(self, waves_data):
        self.waves        = waves_data
        self.current_wave = 0
        self.spawn_timer  = 0.0
        self.wave_timer   = self.FIRST_WAVE_DELAY
        self.state        = "countdown"
        self.spawn_queue  = []
        self.wave_number  = 0

    def update(self, dt):
        if self.state == "done":
            return None
        if self.state == "countdown":
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self._start_next_wave()
            return None
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.spawn_queue:
            ztype = self.spawn_queue.pop(0)
            self.spawn_timer = self.SPAWN_INTERVAL
            if not self.spawn_queue:
                if self.current_wave >= len(self.waves):
                    self.state = "done"
                else:
                    self.state      = "countdown"
                    self.wave_timer = self.BETWEEN_WAVE_DELAY
            return ztype
        return None

    def _start_next_wave(self):
        if self.current_wave >= len(self.waves):
            self.state = "done"
            return
        wave = self.waves[self.current_wave]
        self.current_wave += 1
        self.wave_number   = self.current_wave
        queue = []
        for group in wave:
            queue.extend([group["type"]] * group["count"])
        random.shuffle(queue)
        self.spawn_queue = queue
        self.state       = "spawning"
        self.spawn_timer = 1.0

    def all_done(self):
        return self.state == "done" and len(self.spawn_queue) == 0

    def get_wave_display(self):
        return f"{self.wave_number} / {len(self.waves)}"

    def get_countdown(self):
        if self.state == "countdown":
            return max(0, int(self.wave_timer) + 1)
        return 0
