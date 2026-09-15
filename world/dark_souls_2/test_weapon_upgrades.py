import random
import unittest

from .WeaponUpgrades import WeaponUpgradeMode, format_weapon_upgrade_spoiler, roll_normalized_upgrade


class WeaponUpgradeTests(unittest.TestCase):
    def test_off_mode_always_returns_zero(self):
        rng = random.Random(1)
        self.assertEqual(0, roll_normalized_upgrade(rng, WeaponUpgradeMode.OFF, 3, 9, 2, 0.8))

    def test_random_mode_stays_inside_configured_bounds(self):
        rng = random.Random(12345)
        values = [roll_normalized_upgrade(rng, WeaponUpgradeMode.RANDOM, 2, 7, 2, 0.5) for _ in range(100)]
        self.assertTrue(all(2 <= value <= 7 for value in values))
        self.assertGreater(len(set(values)), 1)

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

    def test_reversed_bounds_are_normalized(self):
        rng = random.Random(42)
        values = [roll_normalized_upgrade(rng, WeaponUpgradeMode.RANDOM, 8, 2, 0, 0.5) for _ in range(50)]
        self.assertTrue(all(2 <= value <= 8 for value in values))

    def test_formats_progression_weapon_entries_for_spoiler(self):
        text = format_weapon_upgrade_spoiler(
            player_name="Alex",
            mode="progression",
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


if __name__ == "__main__":
    unittest.main()
