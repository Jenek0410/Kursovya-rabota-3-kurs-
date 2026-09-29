"""Алгоритм Дейкстры — поиск кратчайшего пути с учётом весов рёбер.

В этой визуализации все переходы между соседними клетками имеют вес 1,
поэтому на равномерной сетке результат совпадает с BFS, но реализация
демонстрирует работу с приоритетной очередью (heapq), в отличие от
простого обхода в ширину.
"""
import heapq
from typing import Dict, List, Optional

from core.models import Grid, Position
from core.pathfinder import PathFinder, PathResult


class DijkstraPathFinder(PathFinder):
    name = "Дейкстра"

    def find_path(self, grid: Grid) -> PathResult:
        if grid.start is None or grid.finish is None:
            return PathResult()

        visited_order: List[Position] = []
        distances: Dict[Position, float] = {grid.start: 0}
        came_from: Dict[Position, Optional[Position]] = {grid.start: None}
        visited: set = set()

        heap = [(0, grid.start)]

        while heap:
            dist, current = heapq.heappop(heap)
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
                new_dist = dist + 1
                if new_dist < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_dist
                    came_from[neighbor] = current
                    heapq.heappush(heap, (new_dist, neighbor))

        return PathResult(visited_order=visited_order, path=None, visited_count=len(visited_order))

    @staticmethod
    def _reconstruct_path(came_from: Dict[Position, Optional[Position]], end: Position) -> List[Position]:
        path = [end]
        while came_from[path[-1]] is not None:
            path.append(came_from[path[-1]])
        path.reverse()
        return path
