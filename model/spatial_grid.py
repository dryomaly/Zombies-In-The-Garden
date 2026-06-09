# Пространственное хэширование

import math


class SpatialGrid:
    def __init__(self, cell_size=128):
        self.cell_size = cell_size
        self.cells = {}  # (cx, cy) -> список объектов

    def clear(self):
        self.cells.clear()

    def _key(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def add(self, obj):
        key = self._key(obj.x, obj.y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(obj)

    def query_radius(self, x, y, radius):
        result = []
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
