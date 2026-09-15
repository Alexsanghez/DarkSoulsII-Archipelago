#pragma once

#include <string>

enum class EnemyRandomizerPrepareResult {
    MissingInstallation,
    Unchanged,
    Updated,
    WriteFailed,
};

EnemyRandomizerPrepareResult prepare_enemy_randomizer_config(const std::string& config_text);
bool enemy_randomizer_runtime_files_available();
bool enemy_randomizer_ap_is_chain_loaded();
bool load_enemy_randomizer_runtime_support();
bool enemy_randomizer_is_available();
bool launch_enemy_randomizer();
