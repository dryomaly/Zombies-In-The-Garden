# model/pathfinder.py — алгоритм A* для нахождения пути зомби по сетке
# A* (A star) — классический алгоритм поиска кратчайшего пути с эвристикой

import heapq


def heuristic(a, b):
    """Манхэттенское расстояние — подходит для сетки без диагоналей"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(passable_tiles, start, goal, cols, rows):
    """
    Ищет путь от start до goal по сетке.

    passable_tiles — set из (col, row), по которым можно идти
    start, goal    — (col, row)
    cols, rows     — размеры сетки (для проверки границ)

    Возвращает список (col, row) от start до goal,
    или None если путь не найден.
    """

    # Открытый список — куча (f-score, (col, row))
    open_heap = []
    heapq.heappush(open_heap, (0, start))

    came_from = {}           # откуда пришли в каждую клетку
    g_score = {start: 0}    # стоимость пути от start до клетки

    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            # Восстанавливаем путь
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        col, row = current
        # Соседи: вверх, вниз, влево, вправо (без диагоналей)
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (col + dc, row + dr)
            nc, nr = neighbor

            # Проверка границ
            if nc < 0 or nc >= cols or nr < 0 or nr >= rows:
                continue
            # Проходимость
            if neighbor not in passable_tiles:
                continue

            new_g = g_score[current] + 1  # каждый шаг стоит 1

            if neighbor not in g_score or new_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = new_g
                f = new_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, neighbor))

    return None  # путь не найден
