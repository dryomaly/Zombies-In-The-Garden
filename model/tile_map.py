# model/tile_map.py — карта тайлов уровня

from settings import GRID_COLS, GRID_ROWS, TILE_SIZE, GRID_X, GRID_Y
from model.pathfinder import astar


class TileMap:
    """
    Хранит информацию о карте уровня:
    - какие клетки — дорога, трава, база
    - какие клетки доступны для постановки растений
    - путь зомби (вычисляется через A*)
    """

    def __init__(self, level_data):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS

        self.spawn    = tuple(level_data["spawn"])     # (col, row) — точка появления зомби
        self.base_pos = tuple(level_data["base_pos"])  # (col, row) — база

        # Строим набор дорожных тайлов из ключевых точек (waypoints)
        waypoints = [tuple(w) for w in level_data["waypoints"]]
        self.road_tiles = self._build_road(waypoints)

        # A* находит порядок обхода тайлов дороги от спауна до базы
        self.path = astar(
            self.road_tiles,
            self.spawn,
            self.base_pos,
            self.cols,
            self.rows
        )
        if self.path is None:
            raise ValueError(f"A*: путь от {self.spawn} до {self.base_pos} не найден!")

        # Клетки рядом с дорогой — сюда можно ставить растения
        self.plantable = self._find_plantable()

    # ------------------------------------------------------------------
    def _build_road(self, waypoints):
        """
        Строит множество тайлов дороги по списку ключевых точек.
        Между соседними точками рисуем горизонтальный или вертикальный отрезок.
        """
        road = set()
        for i in range(len(waypoints) - 1):
            c0, r0 = waypoints[i]
            c1, r1 = waypoints[i + 1]
            if c0 == c1:
                # Вертикальный отрезок
                step = 1 if r1 > r0 else -1
                for r in range(r0, r1 + step, step):
                    road.add((c0, r))
            else:
                # Горизонтальный отрезок
                step = 1 if c1 > c0 else -1
                for c in range(c0, c1 + step, step):
                    road.add((c, r0))
        return road

    def _find_plantable(self):
        """
        Клетка доступна для растения, если она:
        1. Не на дороге
        2. Не на месте базы
        3. Имеет хотя бы одного соседа на дороге
        4. Находится в пределах сетки
        5. НЕ является одним из четырёх внешних углов сетки
        """
        # Четыре внешних угла сетки — постановка туда запрещена
        corner_cells = {
            (0, 0),
            (self.cols - 1, 0),
            (0, self.rows - 1),
            (self.cols - 1, self.rows - 1),
        }

        plantable = set()
        for (c, r) in self.road_tiles:
            for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nb = (c + dc, r + dr)
                nc, nr = nb
                if (0 <= nc < self.cols and 0 <= nr < self.rows
                        and nb not in self.road_tiles
                        and nb != self.base_pos
                        and nb not in corner_cells):   # углы исключены
                    plantable.add(nb)
        return plantable

    # ------------------------------------------------------------------
    def cell_to_pixel(self, col, row):
        """Центр клетки в пикселях."""
        x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
        y = GRID_Y + row * TILE_SIZE + TILE_SIZE // 2
        return (x, y)

    def pixel_to_cell(self, px, py):
        """Пиксели → клетка сетки. Возвращает None если вне сетки."""
        col = (px - GRID_X) // TILE_SIZE
        row = (py - GRID_Y) // TILE_SIZE
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return (int(col), int(row))
        return None
