"""
Абстракция хранения карт (паттерн Repository).

Отделяет ядро приложения от конкретного способа сохранения —
сейчас это JSON-файл (storage/json_map_repository.py), но в будущем
можно добавить, например, SQLite-репозиторий, не меняя UI и core.
"""
from abc import ABC, abstractmethod

from core.models import Grid


class MapRepository(ABC):
    """Интерфейс сохранения и загрузки карт."""

    @abstractmethod
    def save(self, grid: Grid, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> Grid:
        raise NotImplementedError
