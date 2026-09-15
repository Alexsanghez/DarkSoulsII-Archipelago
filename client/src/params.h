#pragma once

#include <cstdint>
#include <map>

#ifdef _M_IX86
typedef struct {
    int32_t param_id;
    int32_t reward_offset;
    int32_t unknown;
} ParamRow;
#elif defined(_M_X64)
typedef struct {
    uint8_t padding1[4];
    int32_t param_id;
    uint8_t padding2[4];
    int32_t reward_offset;
    uint8_t padding3[4];
    int32_t unknown;
} ParamRow;
#endif

struct StatBlock {
    int16_t str = 0;
    int16_t dex = 0;
    int16_t intl = 0;
    int16_t fth = 0;
};

enum ItemCategory {
    Weapon = 0,
    Shield = 1,
    HeadArmor = 2,
    ChestArmor = 3,
    HandsArmor = 4,
    LegsArmor = 5,
    Ammunition = 6,
    Ring = 7,
    Good = 8,
    Spell = 9,
    Gesture = 10
};

std::map<int32_t, StatBlock> get_weapon_requirements();
std::map<int32_t, int8_t> get_item_categories();
std::map<int32_t, int8_t> get_weapon_max_upgrades();
int8_t scale_weapon_upgrade(int32_t item_id, int8_t normalized_level);
int8_t select_cap_specific_normalized_upgrade(int32_t item_id, int8_t plus5_level, int8_t plus10_level);
