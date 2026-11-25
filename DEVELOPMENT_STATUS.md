# Azure Development Status

Last updated: 2026-11-25

## Repository and working rules

- Repository: https://github.com/grealki/a-desktop
- Active branch: `azure-dev` only.
- Never modify the upstream repository.
- Never merge into `main`, publish a release, or distribute a build.
- Windows is the only active development and test target unless the user changes that instruction.
- Inspect before changing; preserve unrelated functionality.
- Approved cleanup scope:
  1. Permanently disable unrestricted Blackwall permission bypass.
  2. Replace Capri-owned desktop AI endpoints/access-code integration with Azure configuration while preserving legitimate user-selected providers and local AI.
  3. Remove automatic Windows security-warning override / “Run anyway” behavior.
- Keep the separate mod-directory service and unrelated services intact.

## Windows source and security API

- Current `azure-dev` head: `3c4fd545985713a02dcc08d493a411a8a1222d95` (2026-11-24).
- `app/Capri.cs` is canonical Windows source, not generated output. `ci/build-windows.ps1` explicitly includes both `app/Capri.cs` and `app/Companion.Part2.cs` in the source list passed directly to `csc.exe`.
- The safe `Security` API lives in `app/Hands.cs`. `Pays`, `Unasked` and `Secrets` are fixed restrictions: `Locked` returns true for them, `On` returns false, `Set` ignores writes, and `Mask`/`Load` clear those bits. `Gate` holds actions and asks when an ordinary-action toggle is off.
- `Computer.Bypass` is compatibility-only: its getter always returns false and its setter ignores writes. The saved `Preferences.Bypass` field exists only to migrate old settings; `Companion.Migrate` clears it. Security smoke checks deliberately attempt legacy writes and verify they cannot relax restrictions.
- The latest code commit, `3c4fd545985713a02dcc08d493a411a8a1222d95`, changes only `app/Companion.Part2.cs`. Its smoke fixture temporarily enables Full-memory behavior for voice/screen-memory steps and restores the previous in-memory value before completing; it does not change the user's saved memory mode.

## Latest Windows CI and smoke status

- CI run [45347479776](https://github.com/grealki/a-desktop/actions/runs/45347479776) completed successfully on the current head:
  - `windows`: compilation, Azure memory-mode checks, legacy access-code/AI-route regression test and package-marker test passed.
  - `windows-setup`: build, silent install and silent uninstall passed.
  - Compiler output: 154 warnings (151 `CS0649`, 3 `CS0109`), zero compiler errors.
- Full smoke run [45347479770](https://github.com/grealki/a-desktop/actions/runs/45347479770) completed successfully:
  - **1185 PASS / 54 LIMIT / 0 FAIL / 0 SKIP.**
  - The previous smoke failure on the voice/screen-memory step was corrected by the smoke-only Full-memory fixture in the current code commit.
  - `LIMIT` means a live-device or interactive check was not performed in the runner, not a failed assertion. Outstanding examples include real microphone/voice recognition, installed local speech packs, live provider credentials and model availability, physical audio devices, multiple monitors, real games/browsers and physical mouse/tray interaction.
  - The full smoke runner did not perform a real install/uninstall; the separate CI setup job's silent install/uninstall checks passed.
- The latest branch head and latest CI/smoke runs were rechecked on 2026-11-25. No newer commits or runs were present.

## Approved safety cleanup audit

- **Blackwall:** no active unrestricted bypass was found in the inspected Windows source. `Computer.Bypass` cannot be enabled; the old preference flag is cleared during migration; the Security API strips the restricted permission bits. Remaining references are compatibility/migration code and regression tests, not a selectable bypass mode.
- **Desktop AI providers:** the old Capri access-code provider is not recognized. The smoke regression test verifies a legacy `CAPRI-...` string is not treated as a provider and that a user-supplied Anthropic key still uses Anthropic directly. The standard provider URL in `app/Brain.cs` is a direct user-selected provider endpoint, not the retired Capri proxy. Local AI and the other user-selected provider paths were not removed.
- **Worker routes:** `worker/test-legacy-code-routes.mjs` verifies GET and POST requests to the retired `/codes` and `/brain` routes return 404 and do not expose Capri-code headers. The worker's separate `/help` support route and `/mods` directory service remain untouched; no unrelated endpoint removal was made.
- **Windows warnings:** the inspected Windows app/build sources contain no SmartScreen dismissal, “Run anyway” automation, Mark-of-the-Web/`Zone.Identifier` removal, `Unblock-File`, or Defender real-time-protection override. The computer agent is instructed to stop on Windows or antivirus warnings; `app/ErrorChecks.cs` rejects missing-server guidance that says “Run anyway”; `README.md`, `SECURITY.md`, `site/help/knowledge.md`, `site/help/index.html` and `site/setup/index.html` tell users not to bypass SmartScreen or restore quarantined files.
- A macOS-only `xattr -dr com.apple.quarantine` instruction remains in the macOS help material. It was not changed because the active project scope is Windows-only.
- The separate mod-directory endpoints and services remain unchanged.

## Next tasks

1. Do a real-PC Windows validation of microphone input, wake-word recognition, local speech packs, the chosen cloud provider, local AI, physical audio devices and any multi-monitor/game workflows the user uses.
2. Continue fixing only reproducible regressions; keep provider routing and unrelated services intact.
3. Keep development, testing and commits on `azure-dev` only. Do not modify upstream, merge into `main`, publish releases or distribute builds.
4. Keep Gaming Co-Pilot Mode as a separate future feature unless the user asks to start it.
