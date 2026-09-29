"""Поиск в ширину (BFS) — гарантирует кратчайший путь на невзвешенном графе."""
from collections import deque
from typing import Dict, List, Optional

from core.models import Grid, Position
from core.pathfinder import PathFinder, PathResult


class BFSPathFinder(PathFinder):
    name = "BFS"

    def find_path(self, grid: Grid) -> PathResult:
        if grid.start is None or grid.finish is None:
            return PathResult()

        visited_order: List[Position] = []
        came_from: Dict[Position, Optional[Position]] = {grid.start: None}
        queue = deque([grid.start])

        while queue:
            current = queue.popleft()
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
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return PathResult(visited_order=visited_order, path=None, visited_count=len(visited_order))

    @staticmethod
    def _reconstruct_path(came_from: Dict[Position, Optional[Position]], end: Position) -> List[Position]:
        path = [end]
        while came_from[path[-1]] is not None:
            path.append(came_from[path[-1]])
        path.reverse()
        return path
