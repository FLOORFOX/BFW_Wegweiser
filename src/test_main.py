import importlib.util
import pathlib
import unittest


class MainModuleTests(unittest.TestCase):
    def test_find_path_returns_expected_route(self):
        module_path = pathlib.Path(__file__).resolve().parent / "main.py"
        spec = importlib.util.spec_from_file_location("main", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        graph = module.build_graph(module.connections)
        self.assertEqual(
            module.find_path(graph, "startpunkt", "nord_1"),
            ["startpunkt", "knoten_1", "knoten_2", "knoten_nord", "nord_1"],
        )

    def test_find_path_uses_knoten_4_for_nord_west_1(self):
        module_path = pathlib.Path(__file__).resolve().parent / "main.py"
        spec = importlib.util.spec_from_file_location("main", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        graph = module.build_graph(module.connections)
        self.assertEqual(
            module.find_path(graph, "startpunkt", "nord_west_1"),
            ["startpunkt", "knoten_1", "knoten_2", "knoten_3", "knoten_4", "nord_west_1"],
        )

    def test_compile_routing_data_structure(self):
        module_path = pathlib.Path(__file__).resolve().parent / "main.py"
        spec = importlib.util.spec_from_file_location("main", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        data = module.compile_routing_data()
        self.assertEqual(data["start"], "startpunkt")
        self.assertIn("points", data)
        self.assertIn("destinations", data)
        self.assertIn("routes", data)
        self.assertEqual(len(data["routes"]), len(data["destinations"]))
        self.assertEqual(
            data["routes"]["nord_1"],
            ["startpunkt", "knoten_1", "knoten_2", "knoten_nord", "nord_1"],
        )


if __name__ == "__main__":
    unittest.main()
