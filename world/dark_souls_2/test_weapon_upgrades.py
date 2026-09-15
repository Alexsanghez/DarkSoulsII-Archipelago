import random
import unittest

from .WeaponUpgrades import (
    WeaponUpgradeMode,
    format_randomized_weapon_upgrade_spoiler,
    roll_randomized_upgrade_pair,
)


class WeaponUpgradeTests(unittest.TestCase):
    def test_only_off_and_randomized_modes_exist(self):
        self.assertEqual(
            [WeaponUpgradeMode.OFF, WeaponUpgradeMode.RANDOMIZED],
            list(WeaponUpgradeMode),
        )

    def test_randomized_mode_percentage_zero_selects_nothing(self):
        selection_rng = random.Random(1)
        level_rng = random.Random(2)
        values = [
            roll_randomized_upgrade_pair(selection_rng, level_rng, 0, 1, 5, 1, 10)
            for _ in range(100)
        ]
        self.assertTrue(all(value is None for value in values))

    def test_randomized_mode_percentage_hundred_respects_plus5_and_plus10_ranges(self):
        selection_rng = random.Random(3)
        level_rng = random.Random(4)
        values = [
            roll_randomized_upgrade_pair(selection_rng, level_rng, 100, 2, 4, 3, 8)
            for _ in range(100)
        ]
        self.assertTrue(all(value is not None for value in values))
        self.assertTrue(all(2 <= value[0] <= 4 for value in values if value is not None))
        self.assertTrue(all(3 <= value[1] <= 8 for value in values if value is not None))
        self.assertGreater(len({value[0] for value in values if value is not None}), 1)
        self.assertGreater(len({value[1] for value in values if value is not None}), 1)

    def test_randomized_mode_normalizes_reversed_and_out_of_range_bounds(self):
        selection_rng = random.Random(5)
        level_rng = random.Random(6)
        values = [
            roll_randomized_upgrade_pair(selection_rng, level_rng, 100, 9, -3, 15, -2)
            for _ in range(50)
        ]
        self.assertTrue(all(0 <= value[0] <= 5 for value in values if value is not None))
        self.assertTrue(all(0 <= value[1] <= 10 for value in values if value is not None))

    def test_formats_randomized_weapon_entries_for_spoiler(self):
        text = format_randomized_weapon_upgrade_spoiler(
            player_name="Alex",
            percentage=33,
            plus5_min=1,
            plus5_max=5,
            plus10_min=1,
            plus10_max=10,
            entries=[
                ("Alex", "Majula chest", "Longsword", 4, 8),
                ("Riky", "Iron Keep chest", "Black Knight Greatsword", 2, 7),
            ],
        )
        self.assertIn("Mode: randomized | Chance: 33%", text)
        self.assertIn("+5 range: +1..+5 | +10 range: +1..+10", text)
        self.assertIn("[Alex] Majula chest -> Longsword | +5 candidate: +4 | +10 candidate: +8", text)
        self.assertIn("[Riky] Iron Keep chest -> Black Knight Greatsword | +5 candidate: +2 | +10 candidate: +7", text)


if __name__ == "__main__":
    unittest.main()
