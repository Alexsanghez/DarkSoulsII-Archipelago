import random

from .Items import ItemCategory
from .WeaponUpgrades import format_randomized_weapon_upgrade_spoiler, roll_randomized_upgrade_pair


def _is_upgradeable_ds2_item(world, location) -> bool:
    item = location.item
    return (
        item is not None
        and item.player == world.player
        and getattr(item, "category", None) in [ItemCategory.WEAPON, ItemCategory.SHIELD]
        and isinstance(location.address, int)
    )


def _build_randomized_weapon_upgrade_levels(self) -> list[list[int]]:
    if self.options.weapon_upgrade_mode != "randomized":
        return []

    selection_rng = random.Random(
        f"{self.multiworld.seed_name}:{self.player}:ds2-randomized-weapon-upgrade-selection"
    )
    level_rng = random.Random(
        f"{self.multiworld.seed_name}:{self.player}:ds2-randomized-weapon-upgrade-levels"
    )
    result: list[list[int]] = []

    for location in sorted(
        self.multiworld.get_filled_locations(),
        key=lambda loc: (loc.player, loc.address or -1, loc.name),
    ):
        if not _is_upgradeable_ds2_item(self, location):
            continue

        levels = roll_randomized_upgrade_pair(
            selection_rng,
            level_rng,
            self.options.weapon_upgrade_percentage.value,
            self.options.weapon_upgrade_plus5_min_level.value,
            self.options.weapon_upgrade_plus5_max_level.value,
            self.options.weapon_upgrade_plus10_min_level.value,
            self.options.weapon_upgrade_plus10_max_level.value,
        )
        if levels is None:
            continue

        plus5_level, plus10_level = levels
        result.append([
            location.player,
            location.address,
            plus5_level,
            plus10_level,
        ])

    return result


def _write_randomized_spoiler(self, spoiler_handle, levels: list[list[int]]) -> None:
    locations_by_key = {
        (location.player, location.address): location
        for location in self.multiworld.get_filled_locations()
        if isinstance(location.address, int)
    }

    entries: list[tuple[str, str, str, int, int]] = []
    for source_player, location_id, plus5_level, plus10_level in levels:
        location = locations_by_key.get((source_player, location_id))
        if location is None or location.item is None:
            continue
        entries.append((
            self.multiworld.get_player_name(source_player),
            location.name,
            location.item.name,
            plus5_level,
            plus10_level,
        ))

    entries.sort(key=lambda entry: (entry[0], entry[1]))
    plus5_min = min(
        self.options.weapon_upgrade_plus5_min_level.value,
        self.options.weapon_upgrade_plus5_max_level.value,
    )
    plus5_max = max(
        self.options.weapon_upgrade_plus5_min_level.value,
        self.options.weapon_upgrade_plus5_max_level.value,
    )
    plus10_min = min(
        self.options.weapon_upgrade_plus10_min_level.value,
        self.options.weapon_upgrade_plus10_max_level.value,
    )
    plus10_max = max(
        self.options.weapon_upgrade_plus10_min_level.value,
        self.options.weapon_upgrade_plus10_max_level.value,
    )

    spoiler_handle.write(format_randomized_weapon_upgrade_spoiler(
        player_name=self.multiworld.get_player_name(self.player),
        percentage=self.options.weapon_upgrade_percentage.value,
        plus5_min=plus5_min,
        plus5_max=plus5_max,
        plus10_min=plus10_min,
        plus10_max=plus10_max,
        entries=entries,
    ))


def _write_spoiler(self, spoiler_handle) -> None:
    if self.options.weapon_upgrade_mode != "randomized":
        return

    levels = self._build_randomized_weapon_upgrade_levels()
    if levels:
        _write_randomized_spoiler(self, spoiler_handle, levels)


def _fill_slot_data(self) -> dict:
    data = self.options.as_dict(
        "death_link", "game_version", "no_weapon_req", "no_spell_req", "no_equip_load",
        "infinite_lifegems", "randomize_starting_loadout", "starting_weapon_requirement",
        "autoequip", "weapon_upgrade_mode"
    )
    data["weapon_randomized_levels"] = self._build_randomized_weapon_upgrade_levels()
    return data


def install_weapon_upgrade_integration(world_class) -> None:
    world_class._build_randomized_weapon_upgrade_levels = _build_randomized_weapon_upgrade_levels
    world_class.write_spoiler = _write_spoiler
    world_class.fill_slot_data = _fill_slot_data
