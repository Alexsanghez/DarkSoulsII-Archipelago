from enum import IntEnum
from random import Random


class WeaponUpgradeMode(IntEnum):
    OFF = 0
    RANDOMIZED = 1


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def _normalized_bounds(min_level: int, max_level: int, cap: int) -> tuple[int, int]:
    lower = _clamp(int(min_level), 0, cap)
    upper = _clamp(int(max_level), 0, cap)
    if lower > upper:
        lower, upper = upper, lower
    return lower, upper


def roll_randomized_upgrade_pair(
    selection_rng: Random,
    level_rng: Random,
    percentage: int,
    plus5_min: int,
    plus5_max: int,
    plus10_min: int,
    plus10_max: int,
) -> tuple[int, int] | None:
    """Select an equipment location and pre-roll candidates for +5 and +10 reinforcement caps.

    Selection and level RNGs are intentionally separate so changing level ranges does not change
    which locations are selected by the configured percentage.
    """
    chance = _clamp(int(percentage), 0, 100)
    if selection_rng.randrange(100) >= chance:
        return None

    plus5_lower, plus5_upper = _normalized_bounds(plus5_min, plus5_max, 5)
    plus10_lower, plus10_upper = _normalized_bounds(plus10_min, plus10_max, 10)
    return (
        level_rng.randint(plus5_lower, plus5_upper),
        level_rng.randint(plus10_lower, plus10_upper),
    )


def format_randomized_weapon_upgrade_spoiler(
    player_name: str,
    percentage: int,
    plus5_min: int,
    plus5_max: int,
    plus10_min: int,
    plus10_max: int,
    entries: list[tuple[str, str, str, int, int]],
) -> str:
    lines = [
        "",
        "",
        f"Dark Souls II Weapon Reinforcement Levels ({player_name}):",
        f"Mode: randomized | Chance: {percentage}%",
        f"+5 range: +{plus5_min}..+{plus5_max} | +10 range: +{plus10_min}..+{plus10_max}",
        "Note: each selected location stores both candidates; the client uses the item's real reinforcement cap.",
    ]

    for source_player, location_name, item_name, plus5_level, plus10_level in entries:
        lines.append(
            f"[{source_player}] {location_name} -> {item_name} | "
            f"+5 candidate: +{plus5_level} | +10 candidate: +{plus10_level}"
        )

    return "\n".join(lines) + "\n"
