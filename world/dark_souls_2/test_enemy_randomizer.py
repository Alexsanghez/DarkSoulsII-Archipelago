import unittest

from .EnemyRandomizer import (
    build_enemy_randomizer_slot_data,
    derive_enemy_randomizer_seed,
    format_enemy_randomizer_spoiler,
    render_ds2s_enemy_config,
)


class EnemyRandomizerTests(unittest.TestCase):
    def test_enemy_seed_is_deterministic_player_specific_and_signed_64_bit_safe(self):
        first = derive_enemy_randomizer_seed("AP_123456", 1)
        second = derive_enemy_randomizer_seed("AP_123456", 1)
        other_player = derive_enemy_randomizer_seed("AP_123456", 2)

        self.assertEqual(first, second)
        self.assertNotEqual(first, other_player)
        self.assertGreaterEqual(first, 0)
        self.assertLessEqual(first, (1 << 63) - 1)

    def test_v1_config_randomizes_enemies_and_explicitly_disables_out_of_scope_features(self):
        text = render_ds2s_enemy_config(123456789, randomize_bosses=True, scaling=True)

        for enabled_line in (
            "#SEED 123456789\n",
            "#SHUFFLE_TYPE 3\n",
            "#ENEMY_RANDO 1\n",
            "#BOSS_RANDO 1\n",
            "#ENEMY_SCALING 1\n",
            "#BOSS_SCALING 1\n",
            "#CHEATSHEET 1\n",
            "#EASY_CONGRE 1\n",
            "#EASY_TWINS 1\n",
            "#EASY_SKELLYS 1\n",
            "#REMAKE_RAT 1\n",
        ):
            self.assertIn(enabled_line, text)

        for disabled_line in (
            "#INV_REPLACE 0\n",
            "#INV_REMOVE 0\n",
            "#SUM_REPLACE 0\n",
            "#SUM_REMOVE 0\n",
            "#NPC_CLONING 0\n",
            "#RAINBOW 0\n",
            "#ENEMY_MIMIC 0\n",
            "#ENEMY_LIZARD 0\n",
            "#ROAMING_BOSS 0\n",
            "#ENEMY_LOCATION 0\n",
            "#RANDOMIZE_ADS 0\n",
            "#BELFRY_RUSH 0\n",
            "#MULTIBOSS 0\n",
            "#DUPE_SKELELORDS 0\n",
            "#DUPE_GARGOYLES 0\n",
            "#DUPE_SENTINELS 0\n",
            "#DUPE_GANKSQUAD 0\n",
            "#MULTIPLY_ENEMIES 0\n",
            "#MULTIPLY_BOSSES 0\n",
            "#DUPE_ADS 0\n",
            "#DUPE_ADS_CHARIOT 0\n",
            "#DUPE_ADS_ROYAL_RAT 0\n",
            "#DUPE_ADS_COVETOUS 0\n",
            "#DUPE_ADS_SKELELORDS 0\n",
            "#DUPE_ADS_FREJA 0\n",
            "#DUPE_ADS_IVORY 0\n",
        ):
            self.assertIn(disabled_line, text)

        self.assertIn("#ENEMY_MULTIPLIER 100\n", text)
        self.assertIn("#BOSS_MULTIPLIER 100\n", text)
        self.assertIn("#BANNED []\n", text)

    def test_v1_config_enables_all_supported_maps_with_default_zone_limit(self):
        text = render_ds2s_enemy_config(42, randomize_bosses=True, scaling=True)
        map_ids = (
            "M10020000", "M10040000", "M10100000", "M10140000", "M10150000",
            "M10160000", "M10170000", "M10180000", "M10190000", "M10230000",
            "M10250000", "M10270000", "M10290000", "M10300000", "M10310000",
            "M10320000", "M10330000", "M10340000", "M20100000", "M20110000",
            "M20210000", "M20240000", "M20260000", "M40030000", "M50350000",
            "M50360000", "M50370000", "M50380000",
        )
        for map_id in map_ids:
            self.assertIn(f"#{map_id} 99 1\n", text)

    def test_boss_randomization_can_be_disabled(self):
        text = render_ds2s_enemy_config(42, randomize_bosses=False, scaling=True)
        self.assertIn("#BOSS_RANDO 0\n", text)
        self.assertIn("#ENEMY_RANDO 1\n", text)

    def test_scaling_can_be_disabled_without_disabling_randomization(self):
        text = render_ds2s_enemy_config(42, randomize_bosses=True, scaling=False)
        self.assertIn("#ENEMY_SCALING 0\n", text)
        self.assertIn("#BOSS_SCALING 0\n", text)
        self.assertIn("#ENEMY_RANDO 1\n", text)
        self.assertIn("#BOSS_RANDO 1\n", text)

    def test_seed_renderer_rejects_values_outside_signed_64_bit_range(self):
        with self.assertRaises(ValueError):
            render_ds2s_enemy_config(1 << 63, randomize_bosses=True, scaling=True)

    def test_disabled_slot_data_contains_only_disabled_marker(self):
        data = build_enemy_randomizer_slot_data(
            enabled=False,
            seed_name="AP_123456",
            player=1,
            randomize_bosses=True,
            scaling=True,
        )
        self.assertEqual({"enemy_randomizer": 0}, data)

    def test_enabled_slot_data_contains_seed_flags_and_external_config(self):
        data = build_enemy_randomizer_slot_data(
            enabled=True,
            seed_name="AP_123456",
            player=1,
            randomize_bosses=False,
            scaling=True,
        )
        self.assertEqual(1, data["enemy_randomizer"])
        self.assertEqual(0, data["enemy_randomizer_bosses"])
        self.assertEqual(1, data["enemy_randomizer_scaling"])
        self.assertEqual(derive_enemy_randomizer_seed("AP_123456", 1), data["enemy_randomizer_seed"])
        self.assertIn(f"#SEED {data['enemy_randomizer_seed']}\n", data["enemy_randomizer_config"])
        self.assertIn("#BOSS_RANDO 0\n", data["enemy_randomizer_config"])

    def test_spoiler_records_v1_configuration(self):
        text = format_enemy_randomizer_spoiler(
            player_name="Alex",
            seed=987654321,
            randomize_bosses=True,
            scaling=True,
        )
        self.assertIn("Dark Souls II Enemy Randomizer V1 (Alex):", text)
        self.assertIn("Seed: 987654321", text)
        self.assertIn("Enemies: randomized", text)
        self.assertIn("Bosses: randomized", text)
        self.assertIn("Scaling: enabled", text)
        self.assertIn("Scholar of the First Sin only", text)
        self.assertIn("DS2SRandomizer cheatsheet", text)


if __name__ == "__main__":
    unittest.main()
