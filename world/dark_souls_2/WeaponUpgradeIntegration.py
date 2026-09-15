import random

from .Items import ItemCategory
from .WeaponUpgrades import (
    format_progression_weapon_upgrade_spoiler,
    format_randomized_weapon_upgrade_spoiler,
    roll_normalized_upgrade,
    roll_randomized_upgrade_pair,
)


def _is_upgradeable_ds2_item(world, location) -> bool:
    item = location.item
    return (
        item is not None
        and item.player == world.player
        and getattr(item, "category", None) in [ItemCategory.WEAPON, ItemCategory.SHIELD]
        and isinstance(location.address, int)
    )


def _build_progression_weapon_upgrade_levels(self) -> list[list[int]]:
    if self.options.weapon_upgrade_mode != "progression":
        return []

    spheres = list(self.multiworld.get_spheres())
    rng = random.Random(f"{self.multiworld.seed_name}:{self.player}:ds2-weapon-upgrades")
    mapped_locations: set[tuple[int, int]] = set()
    result: list[list[int]] = []
    denominator = max(1, len(spheres) - 1)

    for sphere_index, sphere in enumerate(spheres):
        progress = sphere_index / denominator
        for location in sorted(sphere, key=lambda loc: (loc.player, loc.address or -1, loc.name)):
            if not _is_upgradeable_ds2_item(self, location):
                continue

            level = roll_normalized_upgrade(
                rng,
                self.options.weapon_upgrade_mode.value,
                self.options.weapon_upgrade_min_level.value,
                self.options.weapon_upgrade_max_level.value,
                self.options.weapon_upgrade_variance.value,
                progress,
            )
            result.append([location.player, location.address, level])
            mapped_locations.add((location.player, location.address))

    # Excluded/minimal-access locations may not appear in a progression sphere.
    for location in sorted(
        self.multiworld.get_filled_locations(),
        key=lambda loc: (loc.player, loc.address or -1, loc.name),
    ):
        key = (location.player, location.address) if isinstance(location.address, int) else None
        if key is None or key in mapped_locations or not _is_upgradeable_ds2_item(self, location):
            continue

        level = roll_normalized_upgrade(
            rng,
            self.options.weapon_upgrade_mode.value,
            self.options.weapon_upgrade_min_level.value,
            self.options.weapon_upgrade_max_level.value,
            self.options.weapon_upgrade_variance.value,
            1.0,
        )
        result.append([location.player, location.address, level])

    return result


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


def _write_progression_spoiler(self, spoiler_handle, levels: list[list[int]]) -> None:
    spheres = list(self.multiworld.get_spheres())
    denominator = max(1, len(spheres) - 1)
    sphere_by_location: dict[tuple[int, int], int] = {}
    for sphere_index, sphere in enumerate(spheres):
        for location in sphere:
            if isinstance(location.address, int):
                sphere_by_location[(location.player, location.address)] = sphere_index

    locations_by_key = {
        (location.player, location.address): location
        for location in self.multiworld.get_filled_locations()
        if isinstance(location.address, int)
    }

    entries: list[tuple[int | None, int, str, str, str, int]] = []
    for source_player, location_id, level in levels:
        key = (source_player, location_id)
        location = locations_by_key.get(key)
        if location is None or location.item is None:
            continue

        sphere_index = sphere_by_location.get(key)
        progress_percent = 100 if sphere_index is None else round((sphere_index / denominator) * 100)
        entries.append((
            sphere_index,
            progress_percent,
            self.multiworld.get_player_name(source_player),
            location.name,
            location.item.name,
            level,
        ))

    entries.sort(key=lambda entry: (
        entry[0] if entry[0] is not None else 1_000_000,
        entry[2],
        entry[3],
    ))

    minimum = min(self.options.weapon_upgrade_min_level.value, self.options.weapon_upgrade_max_level.value)
    maximum = max(self.options.weapon_upgrade_min_level.value, self.options.weapon_upgrade_max_level.value)
    spoiler_handle.write(format_progression_weapon_upgrade_spoiler(
        player_name=self.multiworld.get_player_name(self.player),
        min_level=minimum,
        max_level=maximum,
        variance=self.options.weapon_upgrade_variance.value,
        entries=entries,
    ))


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
    if self.options.weapon_upgrade_mode == "off":
        return

    if self.options.weapon_upgrade_mode == "randomized":
        _write_randomized_spoiler(self, spoiler_handle, self._build_randomized_weapon_upgrade_levels())
        return

    levels = self._build_weapon_upgrade_levels()
    if levels:
        _write_progression_spoiler(self, spoiler_handle, levels)


def _fill_slot_data(self) -> dict:
    data = self.options.as_dict(
        "death_link", "game_version", "no_weapon_req", "no_spell_req", "no_equip_load",
        "infinite_lifegems", "randomize_starting_loadout", "starting_weapon_requirement",
        "autoequip", "weapon_upgrade_mode"
    )
    data["weapon_upgrade_levels"] = self._build_weapon_upgrade_levels()
    data["weapon_randomized_levels"] = self._build_randomized_weapon_upgrade_levels()
    return data


def install_weapon_upgrade_integration(world_class) -> None:
    world_class._build_weapon_upgrade_levels = _build_progression_weapon_upgrade_levels
    world_class._build_randomized_weapon_upgrade_levels = _build_randomized_weapon_upgrade_levels
    world_class.write_spoiler = _write_spoiler
    world_class.fill_slot_data = _fill_slot_data
