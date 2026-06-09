# model/zombie.py — зомби с конечным автоматом (FSM)
#
# FSM состояния:
#   WALKING  → зомби идёт по пути
#   DYING    → анимация смерти (0.45 сек)
#   DEAD     → готов к удалению

import math
from settings import ZOMBIE_STATS, TILE_SIZE


# Константы состояний (строки удобнее для отладки)
class ZombieState:
    WALKING = "walking"
    DYING   = "dying"
    DEAD    = "dead"


class Zombie:
    """
    Базовый класс зомби.
    path_pixels — список (x, y) центров тайлов пути (в пикселях).
    """

    DEATH_ANIM_TIME = 0.45   # секунд на анимацию смерти

    def __init__(self, ztype, path_pixels):
        stats = ZOMBIE_STATS[ztype]
        self.ztype = ztype

        # Характеристики
        self.speed       = stats["speed"] * TILE_SIZE   # px/sec
        self.max_hp      = stats["hp"]
        self.hp          = stats["hp"]
        self.base_damage = stats["base_damage"]

        # Позиция (центр спрайта в пикселях)
        self.x = float(path_pixels[0][0])
        self.y = float(path_pixels[0][1])

        # Путь
        self.path       = path_pixels
        self.path_index = 1   # к какой точке движемся (0 — старт)

        # FSM
        self.state     = ZombieState.WALKING
        self.die_timer = 0.0

        # Флаг: дошёл до базы (устанавливается в update, читается в game.py)
        self.reached_base = False

        # Хитбокс (радиус для AABB и пространственной сетки)
        self.radius = 20

    # ------------------------------------------------------------------
    # Интерфейс урона
    # ------------------------------------------------------------------

    def take_damage(self, amount):
        """Принять урон. Игнорируем если зомби уже умирает/мёртв."""
        if self.state != ZombieState.WALKING:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self._start_dying()

    def is_vulnerable(self):
        """Можно ли нанести урон зомби прямо сейчас."""
        return self.state == ZombieState.WALKING

    def is_dead(self):
        return self.state == ZombieState.DEAD

    # ------------------------------------------------------------------
    # FSM переходы
    # ------------------------------------------------------------------

    def _start_dying(self):
        self.state     = ZombieState.DYING
        self.die_timer = self.DEATH_ANIM_TIME

    # ------------------------------------------------------------------
    # Обновление каждый кадр
    # ------------------------------------------------------------------

    def update(self, dt):
        """
        Обновляет состояние зомби.
        Устанавливает self.reached_base = True если дошёл до базы.
        """
        self.reached_base = False

        if self.state == ZombieState.DYING:
            self.die_timer -= dt
            if self.die_timer <= 0:
                self.state = ZombieState.DEAD
            return

        if self.state == ZombieState.DEAD:
            return

        # --- WALKING ---
        if self.path_index >= len(self.path):
            # Дошли до конца пути (базы)
            self.reached_base = True
            return

        # Двигаемся к следующей точке пути
        tx, ty = self.path[self.path_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        move = self.speed * dt

        if dist <= move + 1:
            # Достигли точки
            self.x = float(tx)
            self.y = float(ty)
            self.path_index += 1
        else:
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move

    # ------------------------------------------------------------------
    # AABB для проверки коллизий
    # ------------------------------------------------------------------

    def get_rect(self):
        """Возвращает (x, y, w, h) хитбокса (левый верхний угол)."""
        r = self.radius
        return (self.x - r, self.y - r, r * 2, r * 2)

    # ------------------------------------------------------------------

    @property
    def hp_percent(self):
        return self.hp / self.max_hp

    @property
    def die_progress(self):
        """Прогресс анимации смерти: 0.0 → 1.0"""
        if self.state != ZombieState.DYING:
            return 0.0
        return 1.0 - (self.die_timer / self.DEATH_ANIM_TIME)

    @property
    def direction(self):
        """
        Текущее направление движения: (1,0) вправо, (-1,0) влево,
        (0,1) вниз, (0,-1) вверх.
        """
        if self.path_index >= len(self.path):
            return (1, 0)
        tx, ty = self.path[self.path_index]
        dx = tx - self.x
        dy = ty - self.y
        if abs(dx) >= abs(dy):
            return (1, 0) if dx >= 0 else (-1, 0)
        else:
            return (0, 1) if dy >= 0 else (0, -1)
