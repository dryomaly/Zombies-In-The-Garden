# model/plant.py — базовый класс растений и конкретные типы

from settings import (PLANT_STATS, TILE_SIZE, GRID_X, GRID_Y,
                       PEASHOOTER, BOXER, MACHINEGUN)


class Plant:
    """
    Базовый класс растения.
    Конкретные типы (Peashooter, Boxer, MachineGun) наследуются от него.
    """

    def __init__(self, ptype, col, row):
        stats = PLANT_STATS[ptype]
        self.ptype = ptype
        self.col   = col
        self.row   = row

        # Характеристики
        self.damage         = stats["damage"]
        self.range_px       = stats["range"] * TILE_SIZE  # радиус атаки в пикселях
        self.attack_rate    = stats["attack_rate"]        # атак в секунду
        self.has_projectile = stats["has_projectile"]

        # Кулдаун атаки (секунды до следующего удара)
        self.attack_cooldown = 0.0

        # Пиксельный центр клетки
        self.x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
        self.y = GRID_Y + row * TILE_SIZE + TILE_SIZE // 2

    # ------------------------------------------------------------------

    def update(self, dt):
        """Уменьшаем кулдаун каждый кадр."""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def can_attack(self):
        return self.attack_cooldown <= 0

    def do_attack(self):
        """Сброс кулдауна после атаки."""
        self.attack_cooldown = 1.0 / self.attack_rate

    def get_target(self, zombies_in_range):
        """
        Выбираем цель — зомби, который дальше всего прошёл по пути
        (ближе всего к базе). Сортировка по path_index убывающая.
        """
        alive = [z for z in zombies_in_range if z.is_vulnerable()]
        if not alive:
            return None
        alive.sort(key=lambda z: -z.path_index)
        return alive[0]


# ------------------------------------------------------------------
# Конкретные типы — отличаются только начальными параметрами через PLANT_STATS
# ------------------------------------------------------------------

class Peashooter(Plant):
    """Дешёвое начальное растение: средняя дальность, малый урон, пистолет."""
    def __init__(self, col, row):
        super().__init__(PEASHOOTER, col, row)


class Boxer(Plant):
    """Боксёр: малая дальность, средний урон, мгновенный удар (без снаряда)."""
    def __init__(self, col, row):
        super().__init__(BOXER, col, row)


class MachineGun(Plant):
    """Пулемётчик: большая дальность, средний урон, высокая скорость стрельбы."""
    def __init__(self, col, row):
        super().__init__(MACHINEGUN, col, row)


# ------------------------------------------------------------------
# Фабрика — создаём нужный класс по строковому типу
# ------------------------------------------------------------------

def create_plant(ptype, col, row):
    factories = {
        PEASHOOTER: Peashooter,
        BOXER:      Boxer,
        MACHINEGUN: MachineGun,
    }
    cls = factories.get(ptype)
    if cls is None:
        raise ValueError(f"Неизвестный тип растения: {ptype}")
    return cls(col, row)
