#include "enemy_randomizer_bridge.h"

#include <algorithm>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <optional>
#include <string>

#ifdef _WIN32
#include <windows.h>
#include <shellapi.h>
#pragma comment(lib, "Shell32.lib")
#endif

namespace {
namespace fs = std::filesystem;

struct EnemyRandomizerInstallation {
    fs::path directory;
    fs::path executable;
    fs::path config;
};

std::optional<fs::path> game_directory()
{
    std::error_code ec;
    fs::path root = fs::current_path(ec);
    if (ec) return std::nullopt;
    return root;
}

std::optional<EnemyRandomizerInstallation> find_enemy_randomizer_installation()
{
    const auto root = game_directory();
    if (!root) return std::nullopt;

    const fs::path candidates[] = { *root / "randomizer", *root };
    for (const fs::path& directory : candidates) {
        const fs::path executable = directory / "DS2SRandomizer.exe";
        std::error_code ec;
        if (fs::is_regular_file(executable, ec) && !ec) {
            return EnemyRandomizerInstallation{
                directory,
                executable,
                directory / "er_config.txt",
            };
        }
    }
    return std::nullopt;
}

std::string read_file(const fs::path& path)
{
    std::ifstream file(path, std::ios::binary);
    if (!file) return {};
    return std::string(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
}
}

bool enemy_randomizer_runtime_files_available()
{
    const auto root = game_directory();
    if (!root || !find_enemy_randomizer_installation()) return false;

    std::error_code ec;
    const bool has_modengine = fs::is_regular_file(*root / "modengine.ini", ec) && !ec;
    ec.clear();
    const bool has_heap_fix = fs::is_regular_file(*root / "ds2s_heap_x.dll", ec) && !ec;
    return has_modengine && has_heap_fix;
}

bool enemy_randomizer_ap_is_chain_loaded()
{
#ifdef _WIN32
    static int module_anchor = 0;
    HMODULE self_module = nullptr;
    if (!GetModuleHandleExW(
        GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
        reinterpret_cast<LPCWSTR>(&module_anchor),
        &self_module)) {
        return false;
    }

    wchar_t module_path[MAX_PATH] = {};
    if (GetModuleFileNameW(self_module, module_path, MAX_PATH) == 0) return false;

    std::wstring filename = fs::path(module_path).filename().wstring();
    std::transform(filename.begin(), filename.end(), filename.begin(), [](wchar_t ch) {
        return static_cast<wchar_t>(std::towlower(ch));
    });
    return filename != L"dinput8.dll";
#else
    return true;
#endif
}

bool load_enemy_randomizer_runtime_support()
{
    if (!enemy_randomizer_runtime_files_available()) return false;

#ifdef _WIN32
    if (GetModuleHandleW(L"ds2s_heap_x.dll") != nullptr) return true;

    const auto root = game_directory();
    if (!root) return false;
    return LoadLibraryW((*root / "ds2s_heap_x.dll").c_str()) != nullptr;
#else
    return true;
#endif
}

EnemyRandomizerPrepareResult prepare_enemy_randomizer_config(const std::string& config_text)
{
    if (!enemy_randomizer_runtime_files_available()) {
        return EnemyRandomizerPrepareResult::MissingInstallation;
    }

    const auto installation = find_enemy_randomizer_installation();
    if (!installation) return EnemyRandomizerPrepareResult::MissingInstallation;

    std::error_code ec;
    if (fs::is_regular_file(installation->config, ec) && !ec) {
        if (read_file(installation->config) == config_text) {
            return EnemyRandomizerPrepareResult::Unchanged;
        }
    }

    std::ofstream file(installation->config, std::ios::binary | std::ios::trunc);
    if (!file) return EnemyRandomizerPrepareResult::WriteFailed;
    file.write(config_text.data(), static_cast<std::streamsize>(config_text.size()));
    if (!file) return EnemyRandomizerPrepareResult::WriteFailed;
    return EnemyRandomizerPrepareResult::Updated;
}

bool enemy_randomizer_is_available()
{
    return enemy_randomizer_runtime_files_available();
}

bool launch_enemy_randomizer()
{
    if (!enemy_randomizer_runtime_files_available()) return false;

    const auto installation = find_enemy_randomizer_installation();
    if (!installation) return false;

#ifdef _WIN32
    const HINSTANCE result = ShellExecuteW(
        nullptr,
        L"open",
        installation->executable.c_str(),
        nullptr,
        installation->directory.c_str(),
        SW_SHOWNORMAL
    );
    return reinterpret_cast<INT_PTR>(result) > 32;
#else
    return false;
#endif
}
