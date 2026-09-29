"""JSON-реализация хранилища карт."""
import json

from core.map_repository import MapRepository
from core.models import Grid


class JsonMapRepository(MapRepository):
    def save(self, grid: Grid, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(grid.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> Grid:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Grid.from_dict(data)
