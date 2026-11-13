# Azure Development Status

Last updated: 2026-11-13

## Repository and working rules

- Repository: https://github.com/grealki/a-desktop
- Active branch: `azure-dev` only.
- Never modify the upstream repository.
- Never merge into `main`, publish a release, or distribute a build.
- Inspect before changing; preserve unrelated functionality.
- Approved cleanup scope:
  1. Permanently disable unrestricted Blackwall permission bypass.
  2. Replace Capri-owned AI endpoints/access-code integration with Azure configuration while preserving legitimate user-selected providers and local AI.
  3. Remove automatic Windows security-warning override / “Run anyway” behavior.

## Windows source and compile status

- `app/Capri.cs` is canonical Windows source, not generated output. `ci/build-windows.ps1` lists it directly alongside `app/Companion.Part2.cs` and the other source files passed to `csc.exe`.
- The earlier Windows `CS1513: } expected` failure and the two stale `remote.Code` references were fixed in commit `677f73d482ed3d24145d6d2a5b72cc13076a95be`. That commit also closed the purchase-confirmation smoke-test block before its `finally` and removed the misplaced brace near the `StartSmokeTest` catch.
- Current source has no `Cloud.Code`, `remote.Code`, `CodeKind` or active legacy access-code references in `app/Capri.cs`.
- The safe `Security` API lives in `app/Hands.cs`. Current callers in `app/Capri.cs` use its preset, load, toggle and gate APIs. Payments, unrequested actions and credential entry remain fixed restrictions.
- `Computer.Bypass` is compatibility-only: its getter always returns false and its setter ignores writes. The saved `Preferences.Bypass` field is migration-only and is cleared when old settings are migrated.

## Latest Windows CI and smoke status

- Source revision under test: `b61de00f6ad99e28c6f588974a9c70a0aef0e6a8` on `azure-dev`.
- CI run [43380825822](https://github.com/grealki/a-desktop/actions/runs/43380825822) completed successfully on that revision:
  - `windows`: build, Azure memory checks and package-marker test passed.
  - `windows-setup`: build, silent install and silent uninstall passed.
  - The compiler emitted existing `CS0649` warnings for fields populated by deserialization; there were no compile errors.
- Full smoke run [43380825779](https://github.com/grealki/a-desktop/actions/runs/43380825779) is running on the same source revision. Its configured 30-minute runtime soak must complete before the full smoke suite can be called passed.
- The preceding full smoke run [43250811762](https://github.com/grealki/a-desktop/actions/runs/43250811762) reached 1032 PASS / 50 LIMIT / 1 FAIL / 12 SKIP. Its only failure was the Azure Memory button cycling test.
- Root cause: the old `Capri.ToggleRemembering` method still flipped the legacy `Preferences.Remembers` boolean and `Brain.Keeping` compatibility override. The visible Settings button already used `Brain.CycleMemoryMode`, but the smoke-test helper reached the stale method. Commit `b61de00` changes that legacy entry point to call `Brain.CycleMemoryMode` and leaves the saved boolean migration-only. The new full smoke run validates this correction.
- The earlier stale “You are Capri” cloud-request expectations were updated to Azure in commit `35dedd7`.
- The current CI workflow is Windows-only, matching the development focus. Do not spend effort on macOS or Linux unless the user changes that instruction.

## Approved safety cleanup audit (2026-11-13)

- **Blackwall:** no active unrestricted bypass was found in the inspected desktop source. Remaining mentions are migration comments, legacy-settings tests and help text explaining that Blackwall is no longer selectable. Restricted permissions are masked by `Security`; the legacy bypass flag cannot enable them.
- **AI providers:** `Cloud.KindOf` recognizes supported user-selected providers, while local Ollama/custom local servers and the user-installed Claude Code/Codex plan integrations remain available. No Capri-owned desktop AI endpoint or active access-code provider integration was found. The legacy `CAPRI-...` shape remains only in a negative smoke test and in secret-redaction logic; it is not accepted as a provider.
- **Worker routes:** `worker/test-legacy-code-routes.mjs` asserts that GET and POST requests to the old `/codes` and `/brain` routes return 404 without Capri-code headers. The old migration file is retained as migration history. The separate `/mods` directory service is intentionally untouched.
- **Windows warnings:** the inspected desktop C# sources contain no SmartScreen dismissal, “Run anyway” automation, Mark-of-the-Web / `Zone.Identifier` removal, `Unblock-File`, or Defender real-time-protection override. `app/Computer.cs` tells the computer agent to stop on Windows or antivirus warnings; `README.md`, `SECURITY.md` and the website help docs explicitly say not to choose “Run anyway” or disable SmartScreen.
- `app/Capri.cs` uses `WinVerifyTrust` to verify update signatures and rejects an unverifiable signature; disabling its verification UI does not bypass the trust result. `app/Setup.cs` has a separate `runas` path only to close the app from its own install folder during setup; declining UAC is reported and does not bypass Windows protection.
- This was a targeted audit of the desktop app, build scripts, worker legacy-route checks and relevant user-facing documentation. It was not a blanket review or removal of unrelated website, Discord-bot or mod-directory services.

## Temporary patch mechanism

- The one-off workflow `.github/workflows/temporary-azure-source-patch.yml` and script `ci/patch_azure_source.py` were removed after the focused source correction.
- Do not reintroduce automatic source-rewriting workflows or broad write-permission automation.

## Next tasks

1. Check full smoke run `43380825779` after its runtime soak completes; inspect all diagnostics and fix only reproducible regressions.
2. Keep legitimate user-selected cloud providers and local AI intact. Do not change provider routing without a reproducible root cause.
3. Keep mod-directory endpoints and unrelated services intact unless the user separately approves a change.
4. Keep development, testing and commits on Windows and `azure-dev` only.
5. Keep Gaming Co-Pilot Mode as a separate future Azure feature: cooperative advice plus user-approved control handoff. It is planned, not implemented.
