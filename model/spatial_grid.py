# model/spatial_grid.py — пространственное хеширование (spatial hashing)
#
# Позволяет быстро находить объекты рядом с точкой без проверки ВСЕХ объектов.
# Игровое поле делится на квадратные ячейки, объекты хранятся в ячейке по
# своим координатам. При запросе проверяем только соседние ячейки.

import math


class SpatialGrid:
    """Сетка для быстрого поиска ближайших объектов по радиусу."""

    def __init__(self, cell_size=128):
        self.cell_size = cell_size
        self.cells = {}  # (cx, cy) -> список объектов

    def clear(self):
        self.cells.clear()

    def _key(self, x, y):
        """Переводим пиксельные координаты → ключ ячейки."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def add(self, obj):
        """Добавить объект (нужны атрибуты obj.x, obj.y)."""
        key = self._key(obj.x, obj.y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(obj)

    def query_radius(self, x, y, radius):
        """
        Вернуть все объекты в радиусе radius от точки (x, y).
        Реальное расстояние вычисляется через евклидову метрику.
        """
        result = []
        # Сколько ячеек нужно проверить в каждую сторону
        r_cells = int(radius // self.cell_size) + 1
        cx0 = int(x // self.cell_size)
        cy0 = int(y // self.cell_size)

        for dcx in range(-r_cells, r_cells + 1):
            for dcy in range(-r_cells, r_cells + 1):
                key = (cx0 + dcx, cy0 + dcy)
                if key not in self.cells:
                    continue
                for obj in self.cells[key]:
                    dist = math.sqrt((obj.x - x) ** 2 + (obj.y - y) ** 2)
                    if dist <= radius:
                        result.append(obj)

        return result
