import random
import unittest

from .WeaponUpgrades import (
    WeaponUpgradeMode,
    format_progression_weapon_upgrade_spoiler,
    format_randomized_weapon_upgrade_spoiler,
    roll_normalized_upgrade,
    roll_randomized_upgrade_pair,
)


class WeaponUpgradeTests(unittest.TestCase):
    def test_off_mode_always_returns_zero(self):
        rng = random.Random(1)
        self.assertEqual(0, roll_normalized_upgrade(rng, WeaponUpgradeMode.OFF, 3, 9, 2, 0.8))

    def test_randomized_mode_does_not_use_progression_formula(self):
        rng = random.Random(1)
        self.assertEqual(0, roll_normalized_upgrade(rng, WeaponUpgradeMode.RANDOMIZED, 0, 10, 2, 1.0))

    def test_progression_mode_scales_with_sphere_depth_without_variance(self):
        rng = random.Random(1)
        early = roll_normalized_upgrade(rng, WeaponUpgradeMode.PROGRESSION, 0, 10, 0, 0.0)
        middle = roll_normalized_upgrade(rng, WeaponUpgradeMode.PROGRESSION, 0, 10, 0, 0.5)
        late = roll_normalized_upgrade(rng, WeaponUpgradeMode.PROGRESSION, 0, 10, 0, 1.0)
        self.assertEqual((0, 5, 10), (early, middle, late))

    def test_progression_variance_is_clamped_to_user_bounds(self):
        rng = random.Random(9)
        values = [roll_normalized_upgrade(rng, WeaponUpgradeMode.PROGRESSION, 3, 6, 10, 0.5) for _ in range(100)]
        self.assertTrue(all(3 <= value <= 6 for value in values))

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

    def test_formats_progression_weapon_entries_for_spoiler(self):
        text = format_progression_weapon_upgrade_spoiler(
            player_name="Alex",
            min_level=0,
            max_level=10,
            variance=0,
            entries=[
                (0, 0, "Alex", "Majula chest", "Longsword", 0),
                (3, 60, "Riky", "Iron Keep chest", "Greatsword", 6),
                (None, 100, "Alex", "Excluded chest", "Mace", 10),
            ],
        )
        self.assertIn("Dark Souls II Weapon Reinforcement Levels (Alex)", text)
        self.assertIn("Mode: progression | Normalized range: +0..+10 | Variance: +/-0", text)
        self.assertIn("Sphere 0 (0%): [Alex] Majula chest -> Longsword | normalized +0/10", text)
        self.assertIn("Sphere 3 (60%): [Riky] Iron Keep chest -> Greatsword | normalized +6/10", text)
        self.assertIn("Fallback (100%): [Alex] Excluded chest -> Mace | normalized +10/10", text)

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
