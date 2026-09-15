import hashlib


DS2S_RANDOMIZER_MAP_IDS = (
    "M10020000", "M10040000", "M10100000", "M10140000", "M10150000",
    "M10160000", "M10170000", "M10180000", "M10190000", "M10230000",
    "M10250000", "M10270000", "M10290000", "M10300000", "M10310000",
    "M10320000", "M10330000", "M10340000", "M20100000", "M20110000",
    "M20210000", "M20240000", "M20260000", "M40030000", "M50350000",
    "M50360000", "M50370000", "M50380000",
)


def derive_enemy_randomizer_seed(seed_name: str, player: int) -> int:
    material = f"{seed_name}:{int(player)}:ds2-enemy-randomizer-v1".encode("utf-8")
    digest = hashlib.blake2b(material, digest_size=8).digest()
    # The current DS2SRandomizer configuration tooling accepts a signed 64-bit decimal seed.
    # Keep the deterministic hash non-negative and inside that range.
    return int.from_bytes(digest, byteorder="big", signed=False) & ((1 << 63) - 1)


def _flag(value: bool) -> int:
    return 1 if value else 0


def render_ds2s_enemy_config(seed: int, randomize_bosses: bool, scaling: bool) -> str:
    seed = int(seed)
    if not 0 <= seed <= (1 << 63) - 1:
        raise ValueError("enemy randomizer seed must fit in a non-negative signed 64-bit integer")

    lines = [
        "#VERSION 0",
        "#INV_REPLACE 0",
        "#INV_REMOVE 0",
        "#SUM_REPLACE 0",
        "#SUM_REMOVE 0",
        "#NPC_CLONING 0",
        "#SHUFFLE_TYPE 3",
        "#CHEATSHEET 1",
        "#RAINBOW 0",
        "",
        "#ENEMY_RANDO 1",
        "#ENEMY_MIMIC 0",
        "#ENEMY_LIZARD 0",
        "#INVIS_ENEMY 0",
        "#ROAMING_BOSS 0",
        "#ROAMING_CHANCE 1",
        "#ROAMING_RESPAWN 0",
        "#ENEMY_LOCATION 0",
        "#RANDOMIZE_ADS 0",
        "#DUPE_GARGOYLES 0",
        f"#ENEMY_SCALING {_flag(scaling)}",
        "#HP_SCALE 70",
        "#DMG_SCALE 70",
        "#BOSS_DMG_SCALE 70",
        f"#BOSS_SCALING {_flag(scaling)}",
        "#BOSS_HP_SCALE 70",
        "",
        f"#BOSS_RANDO {_flag(randomize_bosses)}",
        "#BELFRY_RUSH 0",
        "#EASY_CONGRE 1",
        "#EASY_TWINS 1",
        "#EASY_SKELLYS 1",
        "#REMAKE_RAT 1",
        "#RAT_CLONES 5",
        "",
        "#MULTIBOSS 0",
        "#DUPE_SKELELORDS 0",
        "#DUPE_GARGOYLES 0",
        "#DUPE_SENTINELS 0",
        "#DUPE_GANKSQUAD 0",
        # Older public DS2SRandomizer builds used these names. Keeping them at zero is harmless
        # for newer builds and prevents accidental multiboss behavior on older compatible builds.
        "#MB_SKE 0",
        "#MB_GAR 0",
        "#MB_RUI 0",
        "#MB_TWI 0",
        "#MB_THR 0",
        "#MB_GRA 0",
        "#MB_LUD 0",
        "",
        "#ENEMY_MULTIPLIER 100",
        "#BOSS_MULTIPLIER 100",
        "#MULTIPLY_ENEMIES 0",
        "#MULTIPLY_BOSSES 0",
        "#DUPE_ADS 0",
        "#DUPE_ADS_CHARIOT 0",
        "#DUPE_ADS_ROYAL_RAT 0",
        "#DUPE_ADS_COVETOUS 0",
        "#DUPE_ADS_SKELELORDS 0",
        "#DUPE_ADS_FREJA 0",
        "#DUPE_ADS_IVORY 0",
        "",
        f"#SEED {seed}",
        "#BANNED []",
    ]

    lines.extend(f"#{map_id} 99 1" for map_id in DS2S_RANDOMIZER_MAP_IDS)
    return "\n".join(lines) + "\n"


def build_enemy_randomizer_slot_data(
    enabled: bool,
    seed_name: str,
    player: int,
    randomize_bosses: bool,
    scaling: bool,
) -> dict:
    if not enabled:
        return {"enemy_randomizer": 0}

    seed = derive_enemy_randomizer_seed(seed_name, player)
    return {
        "enemy_randomizer": 1,
        "enemy_randomizer_seed": seed,
        "enemy_randomizer_bosses": _flag(randomize_bosses),
        "enemy_randomizer_scaling": _flag(scaling),
        "enemy_randomizer_config": render_ds2s_enemy_config(seed, randomize_bosses, scaling),
    }


def format_enemy_randomizer_spoiler(
    player_name: str,
    seed: int,
    randomize_bosses: bool,
    scaling: bool,
) -> str:
    return (
        "\n\nDark Souls II Enemy Randomizer V1"
        + (f" ({player_name})" if player_name else "")
        + ":\n"
        + "Target: Scholar of the First Sin only\n"
        + f"Seed: {int(seed)}\n"
        + "Enemies: randomized (full-random shuffle)\n"
        + f"Bosses: {'randomized' if randomize_bosses else 'vanilla'}\n"
        + f"Scaling: {'enabled' if scaling else 'disabled'}\n"
        + "Safety: NPCs, invaders, summons, mimics, lizards, wandering bosses, enemy multiplication, and multiboss are disabled.\n"
        + "Placements: see the DS2SRandomizer cheatsheet generated when the external randomizer is applied.\n"
    )
