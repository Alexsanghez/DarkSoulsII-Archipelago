from enum import IntEnum
from random import Random


class WeaponUpgradeMode(IntEnum):
    OFF = 0
    RANDOM = 1
    PROGRESSION = 2


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def roll_normalized_upgrade(
    rng: Random,
    mode: int | WeaponUpgradeMode,
    min_level: int,
    max_level: int,
    variance: int,
    progress: float,
) -> int:
    """Return a deterministic seed-driven reinforcement tier on the normal 0..10 scale.

    The client later scales this normalized level to the weapon's real reinforcement cap,
    so a +5 weapon receives half the normalized tier while a normal +10 weapon receives
    the tier directly.
    """
    try:
        mode = WeaponUpgradeMode(mode)
    except ValueError:
        mode = WeaponUpgradeMode.OFF

    if mode == WeaponUpgradeMode.OFF:
        return 0

    lower = _clamp(int(min_level), 0, 10)
    upper = _clamp(int(max_level), 0, 10)
    if lower > upper:
        lower, upper = upper, lower

    if mode == WeaponUpgradeMode.RANDOM:
        return rng.randint(lower, upper)

    clamped_progress = max(0.0, min(1.0, float(progress)))
    target = round(lower + (upper - lower) * clamped_progress)
    spread = _clamp(int(variance), 0, 10)
    return _clamp(target + rng.randint(-spread, spread), lower, upper)


def format_weapon_upgrade_spoiler(
    player_name: str,
    mode: str,
    min_level: int,
    max_level: int,
    variance: int,
    entries: list[tuple[int | None, int, str, str, str, int]],
) -> str:
    lines = [
        "",
        "",
        f"Dark Souls II Weapon Reinforcement Levels ({player_name}):",
        f"Mode: {mode} | Normalized range: +{min_level}..+{max_level} | Variance: +/-{variance}",
        "Note: levels are normalized to the +0..+10 scale; +5 weapons are scaled by the client.",
    ]

    for sphere_index, progress_percent, source_player, location_name, item_name, level in entries:
        sphere_label = f"Sphere {sphere_index}" if sphere_index is not None else "Fallback"
        lines.append(
            f"{sphere_label} ({progress_percent}%): [{source_player}] {location_name} -> "
            f"{item_name} | normalized +{level}/10"
        )

    return "\n".join(lines) + "\n"
