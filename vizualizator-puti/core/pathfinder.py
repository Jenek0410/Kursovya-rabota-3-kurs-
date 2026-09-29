"""
Абстракция алгоритма поиска пути (паттерн Strategy).

Каждый конкретный алгоритм (BFS, Дейкстра, A*) реализует один и тот
же интерфейс PathFinder, поэтому UI и код сравнения алгоритмов
работают с ними одинаково, не зная деталей реализации.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from core.models import Grid, Position


@dataclass
class PathResult:
    """Результат работы алгоритма: порядок обхода клеток и найденный путь."""

    visited_order: List[Position] = field(default_factory=list)
    path: Optional[List[Position]] = None
    visited_count: int = 0
    path_length: int = 0


class PathFinder(ABC):
    """Общий интерфейс для всех алгоритмов поиска пути."""

    name: str = "base_pathfinder"

    @abstractmethod
    def find_path(self, grid: Grid) -> PathResult:
        """Найти путь от grid.start до grid.finish."""
        raise NotImplementedError
