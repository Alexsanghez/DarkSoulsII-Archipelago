# Dark Souls II Enemy Randomizer V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Scholar of the First Sin-only Archipelago-controlled enemy randomizer V1 that deterministically configures normal enemies, bosses, scaling, and conservative boss-balance fixes.

**Architecture:** The APWorld owns the feature flags and derives a stable unsigned 64-bit enemy seed from the Archipelago seed/player slot. It renders the `er_config.txt` format consumed by cboyo's DS2 Item & Enemy Randomizer. The game client receives that configuration in slot data, writes it beside an installed `DS2SRandomizer.exe`, and provides a console command to launch the external randomizer before restarting DS2. This bridge is required because the public DS2SRandomizer repository explicitly contains only the main param-writing files, not the complete app/data distribution.

**Tech Stack:** Python 3.13 / Archipelago 0.6.8 APWorld, C++20 / MSVC v143, nlohmann::json, std::filesystem, Win32 process launch APIs.

**Spec:** User-approved V1 scope from the 2026-09-15 conversation.

## Global Constraints

- V1 supports Scholar of the First Sin only.
- Enemy randomization is off by default.
- When enabled, normal enemies are randomized.
- Boss randomization and location-based enemy/boss scaling default on but are independently configurable.
- NPCs, invaders, summons, mimics, lizards, wandering bosses, and multiboss are disabled in V1.
- The same Archipelago seed and player slot must produce the same 64-bit enemy seed.
- The external randomizer's cheatsheet remains the authoritative placement list; the AP spoiler records configuration and seed only.
- Existing weapon-randomization slot data and spoiler behavior must continue to work.

---

### Task 1: Pure enemy-randomizer model and tests

**Files:**
- Create: `world/dark_souls_2/EnemyRandomizer.py`
- Create: `world/dark_souls_2/test_enemy_randomizer.py`

**Interfaces:**
- Produces: `derive_enemy_randomizer_seed(seed_name: str, player: int) -> int`
- Produces: `render_ds2s_enemy_config(seed: int, randomize_bosses: bool, scaling: bool) -> str`
- Produces: `format_enemy_randomizer_spoiler(player_name: str, seed: int, randomize_bosses: bool, scaling: bool) -> str`

- [ ] Write tests proving seed determinism/player separation, V1-safe exclusions, boss toggle, scaling toggle, and spoiler formatting.
- [ ] Run tests and verify they fail because `EnemyRandomizer.py` does not exist.
- [ ] Implement the minimal pure helper module.
- [ ] Run the focused tests and verify they pass.

### Task 2: APWorld options and integration

**Files:**
- Modify: `world/dark_souls_2/Options.py`
- Create: `world/dark_souls_2/EnemyRandomizerIntegration.py`
- Modify: `world/dark_souls_2/__init__.py`

**Interfaces:**
- Adds YAML options: `enemy_randomizer`, `enemy_randomizer_bosses`, `enemy_randomizer_scaling`.
- Adds slot data: `enemy_randomizer`, `enemy_randomizer_seed`, `enemy_randomizer_bosses`, `enemy_randomizer_scaling`, `enemy_randomizer_config`.

- [ ] Add the three AP options, with enemy randomizer disabled and bosses/scaling enabled by default.
- [ ] Wrap `generate_early` and raise `OptionError` when enemy randomizer is enabled for vanilla DS2.
- [ ] Wrap existing `fill_slot_data` so weapon-randomizer data is preserved and enemy-randomizer data is appended.
- [ ] Wrap existing `write_spoiler` so the enemy section is appended without replacing weapon spoiler output.
- [ ] Install enemy integration after weapon integration in package `__init__.py`.

### Task 3: SotFS client bridge

**Files:**
- Create: `client/src/enemy_randomizer_bridge.h`
- Create: `client/src/enemy_randomizer_bridge.cpp`
- Modify: `client/src/archipelago.cpp`
- Modify: `client/src/dllmain.cpp`
- Modify: `client/DS2Archipelago.vcxproj`
- Modify: `client/DS2Archipelago.vcxproj.filters`

**Interfaces:**
- Produces: `prepare_enemy_randomizer_config(const std::string&) -> EnemyRandomizerPrepareResult`
- Produces: `launch_enemy_randomizer() -> bool`
- Produces: `enemy_randomizer_is_available() -> bool`

- [ ] Implement randomizer-directory discovery for `randomizer/DS2SRandomizer.exe` and root `DS2SRandomizer.exe`.
- [ ] Write `er_config.txt` only when contents changed; return `UNCHANGED`, `UPDATED`, or `MISSING_INSTALLATION`.
- [ ] Parse enemy slot data on connection and reject the feature on Win32/vanilla builds.
- [ ] Add `/enemy-randomizer` to launch the installed randomizer executable after the AP configuration has been prepared.
- [ ] Add clear console logging that changed configurations require applying the randomizer and restarting DS2 before play.
- [ ] Add new source/header files to the Visual Studio project.

### Task 4: Documentation and verification

**Files:**
- Modify: `README.md`

- [ ] Document SotFS-only V1 setup and the two-stage first-run flow: connect, run `/enemy-randomizer`, apply randomization, restart, reconnect.
- [ ] Document that DS2 Item & Enemy Randomizer must be installed separately and that its cheatsheet contains actual enemy placements.
- [ ] Re-run Python unit tests.
- [ ] Review the complete diff for preservation of existing weapon randomizer behavior.
- [ ] Build x64 Release in Visual Studio on Windows before calling the client portion verified.
