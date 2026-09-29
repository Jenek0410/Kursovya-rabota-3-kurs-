"""A* — поиск кратчайшего пути с эвристикой (манхэттенское расстояние).

За счёт эвристики A* обычно посещает меньше клеток, чем BFS или
Дейкстра, оставаясь при этом гарантированно кратчайшим на равномерной
сетке, поэтому в сравнении алгоритмов A* — хорошая демонстрация
эффективности информированного поиска.
"""
import heapq
from typing import Dict, List, Optional

from core.models import Grid, Position
from core.pathfinder import PathFinder, PathResult


class AStarPathFinder(PathFinder):
    name = "A*"

    def find_path(self, grid: Grid) -> PathResult:
        if grid.start is None or grid.finish is None:
            return PathResult()

        visited_order: List[Position] = []
        g_score: Dict[Position, float] = {grid.start: 0}
        came_from: Dict[Position, Optional[Position]] = {grid.start: None}
        visited: set = set()

        heap = [(self._heuristic(grid.start, grid.finish), grid.start)]

        while heap:
            _, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            visited_order.append(current)

            if current == grid.finish:
                path = self._reconstruct_path(came_from, current)
                return PathResult(
                    visited_order=visited_order,
                    path=path,
                    visited_count=len(visited_order),
                    path_length=len(path) - 1,
                )

            for neighbor in grid.neighbors(current):
                new_g = g_score[current] + 1
                if new_g < g_score.get(neighbor, float("inf")):
                    g_score[neighbor] = new_g
                    came_from[neighbor] = current
                    f_score = new_g + self._heuristic(neighbor, grid.finish)
                    heapq.heappush(heap, (f_score, neighbor))

        return PathResult(visited_order=visited_order, path=None, visited_count=len(visited_order))

    @staticmethod
    def _heuristic(a: Position, b: Position) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _reconstruct_path(came_from: Dict[Position, Optional[Position]], end: Position) -> List[Position]:
        path = [end]
        while came_from[path[-1]] is not None:
            path.append(came_from[path[-1]])
        path.reverse()
        return path
