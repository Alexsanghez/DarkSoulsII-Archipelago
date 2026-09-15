#include "../src/enemy_randomizer_bridge.h"

#include <cassert>
#include <filesystem>
#include <fstream>
#include <string>

namespace fs = std::filesystem;

static std::string read_all(const fs::path& path)
{
    std::ifstream file(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
}

int main()
{
    const fs::path original = fs::current_path();
    const fs::path root = fs::temp_directory_path() / "ds2ap_enemy_bridge_test";
    fs::remove_all(root);
    fs::create_directories(root);
    fs::current_path(root);

    assert(prepare_enemy_randomizer_config("#SEED 1\n") == EnemyRandomizerPrepareResult::MissingInstallation);

    fs::create_directories(root / "randomizer");
    std::ofstream(root / "randomizer" / "DS2SRandomizer.exe").put('\0');

    assert(prepare_enemy_randomizer_config("#SEED 2\n") == EnemyRandomizerPrepareResult::Updated);
    assert(read_all(root / "randomizer" / "er_config.txt") == "#SEED 2\n");
    assert(prepare_enemy_randomizer_config("#SEED 2\n") == EnemyRandomizerPrepareResult::Unchanged);

    fs::remove_all(root / "randomizer");
    std::ofstream(root / "DS2SRandomizer.exe").put('\0');
    assert(prepare_enemy_randomizer_config("#SEED 3\n") == EnemyRandomizerPrepareResult::Updated);
    assert(read_all(root / "er_config.txt") == "#SEED 3\n");

    fs::current_path(original);
    fs::remove_all(root);
    return 0;
}
