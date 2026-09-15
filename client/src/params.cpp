#include "params.h"

#include "memory.h"
#include "offsets.h"

#include "spdlog/spdlog.h"

#include <algorithm>
#include <vector>

std::map<int32_t, StatBlock> get_weapon_requirements()
{
    uintptr_t param_ptr = resolve_pointer(get_base_address(), pointer_offsets::base_a, param_offsets::weapon_param);
    ParamRow* row_ptr = reinterpret_cast<ParamRow*>(param_ptr + 0x44 - sizeof(uintptr_t)); // 0x3C for x64 and 0x40 for x86
    std::map<int32_t, StatBlock> result;

    for (int i = 0; i < 10000; i++) {
        int param_id = row_ptr[i].param_id;

        if (param_id == 12020000) break; // reached the end

        uintptr_t reward_ptr = param_ptr + row_ptr[i].reward_offset;

        StatBlock req;
        req.str = read_value<int16_t>(reward_ptr + 0x18);
        req.dex = read_value<int16_t>(reward_ptr + 0x1A);
        req.intl = read_value<int16_t>(reward_ptr + 0x1C);
        req.fth = read_value<int16_t>(reward_ptr + 0x1E);

        result[param_id] = req;
    }

    return result;
}

std::map<int32_t, int8_t> get_item_categories()
{
    uintptr_t param_ptr = resolve_pointer(get_base_address(), pointer_offsets::base_a, param_offsets::item_param);
    ParamRow* row_ptr = reinterpret_cast<ParamRow*>(param_ptr + 0x44 - sizeof(uintptr_t)); // 0x3C for x64 and 0x40 for x86
    std::map<int32_t, int8_t> categories;

    for (int i = 0; i < 10000; ++i) {
        int param_id = row_ptr[i].param_id;
        if (i > 0 && param_id == 0) break;

        uintptr_t reward_ptr = param_ptr + row_ptr[i].reward_offset;

        categories[param_id] = read_value<int8_t>(reward_ptr + 0x4F);
    }

    return categories;
}

std::map<int32_t, int8_t> get_weapon_max_upgrades()
{
    uintptr_t base_address = get_base_address();
    uintptr_t weapon_param_ptr = resolve_pointer(base_address, pointer_offsets::base_a, param_offsets::weapon_param);

#ifdef _M_IX86
    const std::vector<uintptr_t> weapon_reinforce_param = { 0x18, 0x238, 0x94, 0x0 };
#elif defined(_M_X64)
    const std::vector<uintptr_t> weapon_reinforce_param = { 0x18, 0x470, 0xD8, 0x0 };
#endif

    uintptr_t reinforce_param_ptr = resolve_pointer(base_address, pointer_offsets::base_a, weapon_reinforce_param);
    ParamRow* reinforce_rows = reinterpret_cast<ParamRow*>(reinforce_param_ptr + 0x44 - sizeof(uintptr_t));

    std::map<int32_t, int8_t> reinforce_caps;
    for (int i = 0; i < 1000; ++i) {
        int reinforce_id = reinforce_rows[i].param_id;
        if (i > 0 && reinforce_id == 0) break;

        uintptr_t reinforce_data = reinforce_param_ptr + reinforce_rows[i].reward_offset;
        int max_upgrade = read_value<int32_t>(reinforce_data + 0x48);
        reinforce_caps[reinforce_id] = static_cast<int8_t>(std::clamp(max_upgrade, 0, 10));
    }

    ParamRow* weapon_rows = reinterpret_cast<ParamRow*>(weapon_param_ptr + 0x44 - sizeof(uintptr_t));
    std::map<int32_t, int8_t> result;

    for (int i = 0; i < 10000; ++i) {
        int weapon_id = weapon_rows[i].param_id;
        if (weapon_id == 12020000) break;

        uintptr_t weapon_data = weapon_param_ptr + weapon_rows[i].reward_offset;
        int reinforce_id = read_value<int32_t>(weapon_data + 0x8);

        auto cap = reinforce_caps.find(reinforce_id);
        if (cap != reinforce_caps.end()) {
            result[weapon_id] = cap->second;
        }
    }

    return result;
}

int8_t scale_weapon_upgrade(int32_t item_id, int8_t normalized_level)
{
    static std::map<int32_t, int8_t> weapon_caps = get_weapon_max_upgrades();

    auto cap = weapon_caps.find(item_id);
    if (cap == weapon_caps.end() || cap->second <= 0) return 0;

    int normalized = std::clamp(static_cast<int>(normalized_level), 0, 10);
    int max_upgrade = std::clamp(static_cast<int>(cap->second), 0, 10);

    // Rounded proportional mapping: +10 scale -> each weapon's actual reinforcement cap.
    return static_cast<int8_t>((normalized * max_upgrade + 5) / 10);
}

int8_t select_cap_specific_weapon_upgrade(int32_t item_id, int8_t plus5_level, int8_t plus10_level)
{
    static std::map<int32_t, int8_t> weapon_caps = get_weapon_max_upgrades();

    auto cap = weapon_caps.find(item_id);
    if (cap == weapon_caps.end() || cap->second <= 0) return 0;

    int max_upgrade = std::clamp(static_cast<int>(cap->second), 0, 10);
    int candidate = max_upgrade <= 5
        ? static_cast<int>(plus5_level)
        : static_cast<int>(plus10_level);

    return static_cast<int8_t>(std::clamp(candidate, 0, max_upgrade));
}
