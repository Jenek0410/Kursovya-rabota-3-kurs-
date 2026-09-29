import unittest

from core.models import Grid


class TestGrid(unittest.TestCase):
    def test_set_wall_ignores_start_and_finish(self):
        grid = Grid(width=5, height=5)
        grid.set_start((0, 0))
        grid.set_finish((4, 4))
        grid.set_wall((0, 0), True)
        grid.set_wall((4, 4), True)
        self.assertNotIn((0, 0), grid.walls)
        self.assertNotIn((4, 4), grid.walls)

    def test_neighbors_excludes_walls_and_out_of_bounds(self):
        grid = Grid(width=3, height=3)
        grid.walls.add((0, 1))
        neighbors = grid.neighbors((0, 0))
        self.assertIn((1, 0), neighbors)
        self.assertNotIn((0, 1), neighbors)
        self.assertNotIn((-1, 0), neighbors)

    def test_to_dict_from_dict_roundtrip(self):
        grid = Grid(width=4, height=4)
        grid.set_start((0, 0))
        grid.set_finish((3, 3))
        grid.walls.add((1, 1))
        restored = Grid.from_dict(grid.to_dict())
        self.assertEqual(restored.width, grid.width)
        self.assertEqual(restored.height, grid.height)
        self.assertEqual(restored.start, grid.start)
        self.assertEqual(restored.finish, grid.finish)
        self.assertEqual(restored.walls, grid.walls)

    def test_clear_walls_keeps_start_and_finish(self):
        grid = Grid(width=3, height=3)
        grid.set_start((0, 0))
        grid.set_finish((2, 2))
        grid.walls.add((1, 1))
        grid.clear_walls()
        self.assertEqual(grid.walls, set())
        self.assertEqual(grid.start, (0, 0))
        self.assertEqual(grid.finish, (2, 2))

    def test_clear_all_resets_everything(self):
        grid = Grid(width=3, height=3)
        grid.set_start((0, 0))
        grid.set_finish((2, 2))
        grid.walls.add((1, 1))
        grid.clear_all()
        self.assertEqual(grid.walls, set())
        self.assertIsNone(grid.start)
        self.assertIsNone(grid.finish)


if __name__ == "__main__":
    unittest.main()
