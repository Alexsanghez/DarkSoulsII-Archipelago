from Options import OptionError

from .EnemyRandomizer import (
    build_enemy_randomizer_slot_data,
    derive_enemy_randomizer_seed,
    format_enemy_randomizer_spoiler,
)


def _enemy_randomizer_enabled(world) -> bool:
    return bool(world.options.enemy_randomizer)


def _build_enemy_randomizer_slot_data(self) -> dict:
    return build_enemy_randomizer_slot_data(
        enabled=_enemy_randomizer_enabled(self),
        seed_name=self.multiworld.seed_name,
        player=self.player,
        randomize_bosses=bool(self.options.enemy_randomizer_bosses),
        scaling=bool(self.options.enemy_randomizer_scaling),
    )


def install_enemy_randomizer_integration(world_class) -> None:
    original_generate_early = world_class.generate_early
    original_fill_slot_data = world_class.fill_slot_data
    original_write_spoiler = getattr(world_class, "write_spoiler", None)

    def generate_early(self) -> None:
        original_generate_early(self)
        if _enemy_randomizer_enabled(self) and self.options.game_version != "sotfs":
            raise OptionError(
                "Dark Souls II Enemy Randomizer V1 supports Scholar of the First Sin only. "
                "Set game_version to sotfs or disable enemy_randomizer."
            )

    def fill_slot_data(self) -> dict:
        data = original_fill_slot_data(self)
        data.update(_build_enemy_randomizer_slot_data(self))
        return data

    def write_spoiler(self, spoiler_handle) -> None:
        if original_write_spoiler is not None:
            original_write_spoiler(self, spoiler_handle)
        if not _enemy_randomizer_enabled(self):
            return

        seed = derive_enemy_randomizer_seed(self.multiworld.seed_name, self.player)
        spoiler_handle.write(format_enemy_randomizer_spoiler(
            player_name=self.multiworld.get_player_name(self.player),
            seed=seed,
            randomize_bosses=bool(self.options.enemy_randomizer_bosses),
            scaling=bool(self.options.enemy_randomizer_scaling),
        ))

    world_class._build_enemy_randomizer_slot_data = _build_enemy_randomizer_slot_data
    world_class.generate_early = generate_early
    world_class.fill_slot_data = fill_slot_data
    world_class.write_spoiler = write_spoiler
