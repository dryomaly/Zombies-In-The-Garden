# Карта тайлов

from settings import GRID_COLS, GRID_ROWS, TILE_SIZE, GRID_X, GRID_Y


class TileMap:
    def __init__(self, level_data):
        self.cols     = GRID_COLS
        self.rows     = GRID_ROWS
        self.spawn    = tuple(level_data["spawn"])
        self.base_pos = tuple(level_data["base_pos"])

        waypoints     = [tuple(w) for w in level_data["waypoints"]]
        self.path     = self._build_path(waypoints)
        self.road_tiles = set(self.path)
        self.plantable  = self._find_plantable()

    def _build_path(self, waypoints):
        path = []
        for i in range(len(waypoints) - 1):
            c0, r0 = waypoints[i]
            c1, r1 = waypoints[i + 1]
            if c0 == c1:
                step = 1 if r1 > r0 else -1
                for r in range(r0, r1 + step, step):
                    cell = (c0, r)
                    if not path or path[-1] != cell:
                        path.append(cell)
            else:
                step = 1 if c1 > c0 else -1
                for c in range(c0, c1 + step, step):
                    cell = (c, r0)
                    if not path or path[-1] != cell:
                        path.append(cell)
        return path

    def _find_plantable(self):
        corner_cells = {(0, 0), (self.cols-1, 0), (0, self.rows-1), (self.cols-1, self.rows-1)}
        plantable = set()
        for c, r in self.road_tiles:
            for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nb = (c + dc, r + dr)
                nc, nr = nb
                if (0 <= nc < self.cols and 0 <= nr < self.rows
                        and nb not in self.road_tiles
                        and nb != self.base_pos
                        and nb not in corner_cells):
                    plantable.add(nb)
        return plantable

    def cell_to_pixel(self, col, row):
        return (GRID_X + col * TILE_SIZE + TILE_SIZE // 2,
                GRID_Y + row * TILE_SIZE + TILE_SIZE // 2)

    def pixel_to_cell(self, px, py):
        col = (px - GRID_X) // TILE_SIZE
        row = (py - GRID_Y) // TILE_SIZE
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return (int(col), int(row))
        return None
