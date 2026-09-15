import hashlib


def derive_enemy_randomizer_seed(seed_name: str, player: int) -> int:
    material = f"{seed_name}:{int(player)}:ds2-enemy-randomizer-v1".encode("utf-8")
    digest = hashlib.blake2b(material, digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=False)


def _flag(value: bool) -> int:
    return 1 if value else 0


def render_ds2s_enemy_config(seed: int, randomize_bosses: bool, scaling: bool) -> str:
    if not 0 <= int(seed) <= (1 << 64) - 1:
        raise ValueError("enemy randomizer seed must fit in an unsigned 64-bit integer")

    lines = [
        "#VERSION 0",
        "#INV_REPLACE 0",
        "#INV_REMOVE 0",
        "#SUM_REPLACE 0",
        "#SUM_REMOVE 0",
        "#NPC_CLONING 0",
        "#SHUFFLE_TYPE 1",
        "#CHEATSHEET 1",
        "",
        "#ENEMY_RANDO 1",
        "#ENEMY_MIMIC 0",
        "#ENEMY_LIZARD 0",
        "#INVIS_ENEMY 0",
        "#ROAMING_BOSS 0",
        "#ROAMING_CHANCE 0",
        "#ROAMING_RESPAWN 0",
        f"#ENEMY_SCALING {_flag(scaling)}",
        "#HP_SCALE 70",
        "#DMG_SCALE 70",
        f"#BOSS_SCALING {_flag(scaling)}",
        "#BOSS_HP_SCALE 70",
        "#BOSS_DMG_SCALE 70",
        "",
        f"#BOSS_RANDO {_flag(randomize_bosses)}",
        "#BELFRY_RUSH 1",
        "#EASY_CONGRE 1",
        "#EASY_TWINS 1",
        "#EASY_SKELLYS 1",
        "#REMAKE_RAT 1",
        "#RAT_CLONES 5",
        "",
        "#MULTIBOSS 0",
        "#MB_SKE 0",
        "#MB_GAR 0",
        "#MB_RUI 0",
        "#MB_TWI 0",
        "#MB_THR 0",
        "#MB_GRA 0",
        "#MB_LUD 0",
        f"#SEED {int(seed)}",
    ]
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
        + "Enemies: randomized\n"
        + f"Bosses: {'randomized' if randomize_bosses else 'vanilla'}\n"
        + f"Scaling: {'enabled' if scaling else 'disabled'}\n"
        + "Safety: NPCs, invaders, summons, mimics, lizards, wandering bosses, and multiboss are disabled.\n"
        + "Placements: see the DS2SRandomizer cheatsheet generated when the external randomizer is applied.\n"
    )
