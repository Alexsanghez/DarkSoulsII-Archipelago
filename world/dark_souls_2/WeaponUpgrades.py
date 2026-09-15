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
