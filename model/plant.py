# Класс растений

from settings import (
    PLANT_STATS,
    TILE_SIZE,
    GRID_X,
    GRID_Y,
    PEASHOOTER,
    BOXER,
    MACHINEGUN,
)


class Plant:
    """
    Базовый класс растения.
    Конкретные типы (Peashooter, Boxer, MachineGun) наследуются от него.
    """

    def __init__(self, ptype, col, row):
        stats = PLANT_STATS[ptype]
        self.ptype = ptype
        self.col = col
        self.row = row

        # Характеристики
        self.damage = stats["damage"]
        self.range_px = stats["range"] * TILE_SIZE
        self.attack_rate = stats["attack_rate"]
        self.has_projectile = stats["has_projectile"]

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
    def __init__(self, col, row):
        super().__init__(PEASHOOTER, col, row)


class Boxer(Plant):
    def __init__(self, col, row):
        super().__init__(BOXER, col, row)


class MachineGun(Plant):
    def __init__(self, col, row):
        super().__init__(MACHINEGUN, col, row)



def create_plant(ptype, col, row):
    factories = {
        PEASHOOTER: Peashooter,
        BOXER: Boxer,
        MACHINEGUN: MachineGun,
    }
    cls = factories.get(ptype)
    if cls is None:
        raise ValueError(f"Неизвестный тип растения: {ptype}")
    return cls(col, row)
