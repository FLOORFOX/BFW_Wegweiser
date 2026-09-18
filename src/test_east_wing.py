import copy
import importlib.util
import pathlib
import unittest


def _load_module(name):
    module_path = pathlib.Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EastWingDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_database = _load_module("build_database")
        cls.calculate_routes = _load_module("calculate_routes")
        cls.database = cls.build_database.build_database()

    def test_corridor_segments_include_movement_center(self):
        segment = self.database["segments"]["segment:flur_west:p01:p02"]

        self.assertEqual(segment["geometry"][1], self.database["zones"]["flur_west"]["movement_center"])
        self.assertEqual(len(segment["geometry"]), 3)

    def test_room_segments_stay_direct(self):
        segment = self.database["segments"]["segment:E.61:p02:p27"]

        self.assertEqual(segment["geometry"], [[440, 170], [435, 0]])

    def test_shortest_route_builds_expected_cross_zone_path(self):
        route = self.calculate_routes.shortest_route(self.database, "E.61", "E.57")

        self.assertEqual(
            route["sequence"],
            ["E.61", "p02", "flur_west", "p08", "atrium", "p15", "flur_ost", "p18", "E.57"],
        )
        self.assertEqual(route["segment_roles"], ["access", "transit", "access"])

    def test_shortest_route_handles_same_zone(self):
        route = self.calculate_routes.shortest_route(self.database, "E.61", "E.61")

        self.assertEqual(route["status"], "ok")
        self.assertEqual(route["sequence"], ["E.61"])
        self.assertEqual(route["portal_chain"], [])
        self.assertEqual(route["total_cost"], 0.0)

    def test_validate_source_rejects_unrelated_wall_portal(self):
        walls = copy.deepcopy(self.database["graphs"]["adjacency"]["edges"])
        walls["w01"]["portal_id"] = "p22"

        with self.assertRaisesRegex(ValueError, "portal does not match wall rooms"):
            self.build_database.validate_source(
                self.database["rooms"],
                self.database["zones"],
                self.database["portals"],
                walls,
                self.database["indexes"]["zone_portals"],
            )

    def test_validate_routes_allows_unreachable_contract(self):
        routed_database = self.calculate_routes.calculate_all_routes(self.database)
        routed_database["routes"]["E.61"]["E.57"] = {
            "status": "unreachable",
            "sequence": [],
            "portal_chain": [],
            "zone_sequence": [],
            "state_chain": [],
            "segment_ids": [],
            "segment_zones": [],
            "segment_roles": [],
            "distance": None,
            "special_cost": None,
            "total_cost": None,
        }

        self.calculate_routes.validate_routes(routed_database)


if __name__ == "__main__":
    unittest.main()
