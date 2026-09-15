import io
import unittest
from types import SimpleNamespace

from Options import OptionError

from .EnemyRandomizerIntegration import install_enemy_randomizer_integration


class FakeMultiworld:
    seed_name = "AP_TEST_SEED"

    @staticmethod
    def get_player_name(player):
        return f"Player{player}"


def build_world_class():
    class FakeWorld:
        player = 1

        def __init__(self, *, enabled=True, bosses=True, scaling=True, game_version="sotfs"):
            self.options = SimpleNamespace(
                enemy_randomizer=enabled,
                enemy_randomizer_bosses=bosses,
                enemy_randomizer_scaling=scaling,
                game_version=game_version,
            )
            self.multiworld = FakeMultiworld()
            self.base_generate_early_called = False

        def generate_early(self):
            self.base_generate_early_called = True

        def fill_slot_data(self):
            return {"existing_slot_data": 7}

        def write_spoiler(self, spoiler_handle):
            spoiler_handle.write("BASE SPOILER\n")

    install_enemy_randomizer_integration(FakeWorld)
    return FakeWorld


class EnemyRandomizerIntegrationTests(unittest.TestCase):
    def test_fill_slot_data_preserves_existing_data_and_adds_enemy_payload(self):
        world = build_world_class()(enabled=True, bosses=False, scaling=True)
        data = world.fill_slot_data()

        self.assertEqual(7, data["existing_slot_data"])
        self.assertEqual(1, data["enemy_randomizer"])
        self.assertEqual(0, data["enemy_randomizer_bosses"])
        self.assertEqual(1, data["enemy_randomizer_scaling"])
        self.assertIn("#BOSS_RANDO 0\n", data["enemy_randomizer_config"])

    def test_disabled_enemy_randomizer_only_adds_disabled_marker(self):
        world = build_world_class()(enabled=False)
        data = world.fill_slot_data()
        self.assertEqual({"existing_slot_data": 7, "enemy_randomizer": 0}, data)

    def test_spoiler_wrapper_preserves_existing_spoiler_output(self):
        world = build_world_class()(enabled=True)
        output = io.StringIO()
        world.write_spoiler(output)
        text = output.getvalue()

        self.assertTrue(text.startswith("BASE SPOILER\n"))
        self.assertIn("Dark Souls II Enemy Randomizer V1 (Player1):", text)

    def test_vanilla_with_enemy_randomizer_enabled_is_rejected_after_base_generate_early(self):
        world = build_world_class()(enabled=True, game_version="vanilla")
        with self.assertRaises(OptionError):
            world.generate_early()
        self.assertTrue(world.base_generate_early_called)


if __name__ == "__main__":
    unittest.main()
