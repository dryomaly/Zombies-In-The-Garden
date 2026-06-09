# model/base.py — база растений (цель зомби)

from settings import BASE_MAX_HP


class Base:
    """
    База игрока. Зомби добираются до неё и наносят урон.
    Когда HP <= 0 — игра проиграна.
    """

    def __init__(self, pos):
        self.pos = pos           # (col, row) на сетке
        self.max_hp = BASE_MAX_HP
        self.hp = BASE_MAX_HP

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_dead(self):
        return self.hp <= 0

    @property
    def hp_percent(self):
        return self.hp / self.max_hp
