"""Фабрика алгоритмов (паттерн Factory).

Позволяет UI получать алгоритм по имени, не зная ничего о его
конкретной реализации, и упрощает добавление новых алгоритмов —
достаточно зарегистрировать класс в словаре _ALGORITHMS.
"""
from typing import Dict, List, Type

from algorithms.astar import AStarPathFinder
from algorithms.bfs import BFSPathFinder
from algorithms.dijkstra import DijkstraPathFinder
from core.pathfinder import PathFinder

_ALGORITHMS: Dict[str, Type[PathFinder]] = {
    "BFS": BFSPathFinder,
    "Дейкстра": DijkstraPathFinder,
    "A*": AStarPathFinder,
}


def available_algorithms() -> List[str]:
    return list(_ALGORITHMS.keys())


def build_algorithm(name: str) -> PathFinder:
    try:
        algorithm_cls = _ALGORITHMS[name]
    except KeyError as exc:
        raise ValueError(f"Неизвестный алгоритм: {name}") from exc
    return algorithm_cls()
