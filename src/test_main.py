import importlib.util
import pathlib
import unittest


def _load_main_module():
    module_path = pathlib.Path(__file__).resolve().parent / "main.py"
    spec = importlib.util.spec_from_file_location("main", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoutingContractTests(unittest.TestCase):
    """Verifies the data contract between Python compiler and web presentation layer."""

    @classmethod
    def setUpClass(cls):
        cls.module = _load_main_module()
        cls.data = cls.module.compile_routing_data()

    def test_top_level_contract_keys_exist(self):
        self.assertEqual(self.data["start"], "startpunkt")
        self.assertIn("points", self.data)
        self.assertIn("destinations", self.data)
        self.assertIn("routes", self.data)

    def test_routes_cover_all_destinations(self):
        destinations = self.data["destinations"]
        routes = self.data["routes"]
        self.assertEqual(len(routes), len(destinations))
        for dest in destinations:
            self.assertIn(dest, routes)
            route = routes[dest]
            self.assertIsInstance(route, list)
            self.assertGreater(len(route), 1)
            self.assertEqual(route[0], self.data["start"])
            self.assertEqual(route[-1], dest)

    def test_points_coordinate_format(self):
        points = self.data["points"]
        self.assertIn(self.data["start"], points)
        for name, coords in points.items():
            self.assertIsInstance(coords, list, f"Coordinates for {name} should be a list")
            self.assertEqual(len(coords), 2, f"Coordinates for {name} should have 2 elements")
            self.assertTrue(
                all(isinstance(c, (int, float)) for c in coords),
                f"Coordinates for {name} should be numeric",
            )


class PathfindingAlgorithmTests(unittest.TestCase):
    """Verifies internal pathfinding logic and graph traversal."""

    @classmethod
    def setUpClass(cls):
        cls.module = _load_main_module()
        cls.graph = cls.module.build_graph(cls.module.connections)

    def test_find_path_returns_expected_route(self):
        self.assertEqual(
            self.module.find_path(self.graph, "startpunkt", "nord_1"),
            ["startpunkt", "knoten_1", "knoten_2", "knoten_nord", "nord_1"],
        )

    def test_find_path_uses_knoten_4_for_nord_west_1(self):
        self.assertEqual(
            self.module.find_path(self.graph, "startpunkt", "nord_west_1"),
            ["startpunkt", "knoten_1", "knoten_2", "knoten_3", "knoten_4", "nord_west_1"],
        )


if __name__ == "__main__":
    unittest.main()
