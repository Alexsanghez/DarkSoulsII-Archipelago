import unittest

from .EnemyRandomizer import (
    build_enemy_randomizer_slot_data,
    derive_enemy_randomizer_seed,
    format_enemy_randomizer_spoiler,
    render_ds2s_enemy_config,
)


class EnemyRandomizerTests(unittest.TestCase):
    def test_enemy_seed_is_deterministic_and_player_specific(self):
        first = derive_enemy_randomizer_seed("AP_123456", 1)
        second = derive_enemy_randomizer_seed("AP_123456", 1)
        other_player = derive_enemy_randomizer_seed("AP_123456", 2)

        self.assertEqual(first, second)
        self.assertNotEqual(first, other_player)
        self.assertGreaterEqual(first, 0)
        self.assertLessEqual(first, (1 << 64) - 1)

    def test_v1_config_randomizes_enemies_and_disables_out_of_scope_features(self):
        text = render_ds2s_enemy_config(123456789, randomize_bosses=True, scaling=True)

        self.assertIn("#SEED 123456789\n", text)
        self.assertIn("#ENEMY_RANDO 1\n", text)
        self.assertIn("#BOSS_RANDO 1\n", text)
        self.assertIn("#ENEMY_SCALING 1\n", text)
        self.assertIn("#BOSS_SCALING 1\n", text)
        self.assertIn("#CHEATSHEET 1\n", text)

        for disabled_line in (
            "#INV_REPLACE 0\n",
            "#INV_REMOVE 0\n",
            "#SUM_REPLACE 0\n",
            "#SUM_REMOVE 0\n",
            "#NPC_CLONING 0\n",
            "#ENEMY_MIMIC 0\n",
            "#ENEMY_LIZARD 0\n",
            "#ROAMING_BOSS 0\n",
            "#MULTIBOSS 0\n",
        ):
            self.assertIn(disabled_line, text)

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
