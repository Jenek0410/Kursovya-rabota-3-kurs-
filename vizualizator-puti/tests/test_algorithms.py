import unittest

from algorithms.astar import AStarPathFinder
from algorithms.bfs import BFSPathFinder
from algorithms.dijkstra import DijkstraPathFinder
from core.models import Grid


def build_test_grid() -> Grid:
    grid = Grid(width=5, height=5)
    grid.set_start((0, 0))
    grid.set_finish((4, 4))
    # Стена-перегородка с одним проходом, чтобы путь был неочевидным.
    for row in range(4):
        grid.walls.add((row, 2))
    return grid


class TestPathfindingAlgorithms(unittest.TestCase):
    def test_bfs_finds_path(self):
        grid = build_test_grid()
        result = BFSPathFinder().find_path(grid)
        self.assertIsNotNone(result.path)
        self.assertEqual(result.path[0], grid.start)
        self.assertEqual(result.path[-1], grid.finish)

    def test_dijkstra_matches_bfs_length_on_uniform_grid(self):
        grid = build_test_grid()
        bfs_result = BFSPathFinder().find_path(grid)
        dijkstra_result = DijkstraPathFinder().find_path(grid)
        self.assertEqual(dijkstra_result.path_length, bfs_result.path_length)

    def test_astar_matches_bfs_length_on_uniform_grid(self):
        grid = build_test_grid()
        bfs_result = BFSPathFinder().find_path(grid)
        astar_result = AStarPathFinder().find_path(grid)
        self.assertEqual(astar_result.path_length, bfs_result.path_length)

    def test_astar_visits_no_more_cells_than_bfs(self):
        grid = build_test_grid()
        bfs_result = BFSPathFinder().find_path(grid)
        astar_result = AStarPathFinder().find_path(grid)
        self.assertLessEqual(astar_result.visited_count, bfs_result.visited_count)

    def test_no_path_when_finish_is_walled_off(self):
        grid = Grid(width=3, height=3)
        grid.set_start((0, 0))
        grid.set_finish((2, 2))
        grid.walls.update({(1, 2), (2, 1)})
        result = BFSPathFinder().find_path(grid)
        self.assertIsNone(result.path)

    def test_missing_start_or_finish_returns_empty_result(self):
        grid = Grid(width=3, height=3)
        grid.set_start((0, 0))
        result = BFSPathFinder().find_path(grid)
        self.assertIsNone(result.path)
        self.assertEqual(result.visited_count, 0)


if __name__ == "__main__":
    unittest.main()
