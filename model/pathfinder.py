# Нахождение пути зомби по сетке

import heapq


def heuristic(a, b):
    # Манхэттенское расстояние
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(passable_tiles, start, goal, cols, rows):

    open_heap = []
    heapq.heappush(open_heap, (0, start))

    came_from = {}
    g_score = {start: 0}
    while open_heap:
        _, current = heapq.heappop(open_heap)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        col, row = current
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (col + dc, row + dr)
            nc, nr = neighbor

            if nc < 0 or nc >= cols or nr < 0 or nr >= rows:
                continue
            if neighbor not in passable_tiles:
                continue

            new_g = g_score[current] + 1

            if neighbor not in g_score or new_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = new_g
                f = new_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, neighbor))

    return None
