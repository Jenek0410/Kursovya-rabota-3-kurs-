import os
import tempfile
import unittest

from core.models import Grid
from storage.json_map_repository import JsonMapRepository


class TestJsonMapRepository(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        grid = Grid(width=6, height=6)
        grid.set_start((0, 0))
        grid.set_finish((5, 5))
        grid.walls.add((2, 2))

        repository = JsonMapRepository()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "map.json")
            repository.save(grid, path)
            loaded = repository.load(path)

        self.assertEqual(loaded.width, grid.width)
        self.assertEqual(loaded.height, grid.height)
        self.assertEqual(loaded.start, grid.start)
        self.assertEqual(loaded.finish, grid.finish)
        self.assertEqual(loaded.walls, grid.walls)


if __name__ == "__main__":
    unittest.main()
