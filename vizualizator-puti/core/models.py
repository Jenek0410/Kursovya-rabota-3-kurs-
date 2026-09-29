"""
Визуализатор алгоритмов поиска пути — доменные модели.

Grid — независимое от UI и алгоритмов представление карты:
клетки, стены, старт и финиш. Модуль core не зависит ни от
tkinter, ни от конкретных алгоритмов (принцип инверсии зависимостей).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Set, Tuple

Position = Tuple[int, int]  # (row, col)


class CellType(Enum):
    EMPTY = "empty"
    WALL = "wall"


@dataclass
class Grid:
    width: int
    height: int
    walls: Set[Position] = field(default_factory=set)
    start: Optional[Position] = None
    finish: Optional[Position] = None

    def in_bounds(self, pos: Position) -> bool:
        row, col = pos
        return 0 <= row < self.height and 0 <= col < self.width

    def is_wall(self, pos: Position) -> bool:
        return pos in self.walls

    def set_wall(self, pos: Position, is_wall: bool) -> None:
        if not self.in_bounds(pos):
            return
        if pos == self.start or pos == self.finish:
            return
        if is_wall:
            self.walls.add(pos)
        else:
            self.walls.discard(pos)

    def set_start(self, pos: Position) -> None:
        if not self.in_bounds(pos):
            return
        self.walls.discard(pos)
        self.start = pos

    def set_finish(self, pos: Position) -> None:
        if not self.in_bounds(pos):
            return
        self.walls.discard(pos)
        self.finish = pos

    def neighbors(self, pos: Position) -> List[Position]:
        row, col = pos
        candidates = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        return [p for p in candidates if self.in_bounds(p) and not self.is_wall(p)]

    def clear_walls(self) -> None:
        self.walls = set()

    def clear_all(self) -> None:
        self.walls = set()
        self.start = None
        self.finish = None

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "walls": [list(p) for p in sorted(self.walls)],
            "start": list(self.start) if self.start else None,
            "finish": list(self.finish) if self.finish else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Grid":
        grid = Grid(width=data["width"], height=data["height"])
        grid.walls = {tuple(p) for p in data.get("walls", [])}
        start = data.get("start")
        finish = data.get("finish")
        grid.start = tuple(start) if start else None
        grid.finish = tuple(finish) if finish else None
        return grid
