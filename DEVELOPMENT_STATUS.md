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
- Current `azure-dev` source has no `Cloud.Code`, `remote.Code`, `CodeKind` or active legacy access-code references in `app/Capri.cs`.
- The safe `Security` API lives in `app/Hands.cs`. Current callers in `app/Capri.cs` use its preset, load, toggle and gate APIs. Payments, unrequested actions and credential entry remain fixed restrictions.
- `Computer.Bypass` is compatibility-only: its getter always returns false and its setter ignores writes. The saved `Preferences.Bypass` field is migration-only and is cleared when old settings are migrated.

## Latest Windows CI and smoke status

- Branch head checked: `35dedd7b110b21614ee08e5511b803f5d05c5ef1` (2026-11-12, “Update cloud smoke expectations for Azure system prompt”).
- CI run [43250811736, attempt 3](https://github.com/grealki/a-desktop/actions/runs/43250811736) completed successfully on that head:
  - `windows`: build, Azure memory checks and package-marker test passed.
  - `windows-setup`: build, silent install and silent uninstall passed.
  - The compiler emitted existing `CS0649` warnings for fields populated by deserialization; there were no compile errors.
- Full smoke run [43250811762, attempt 2](https://github.com/grealki/a-desktop/actions/runs/43250811762) is still running the configured 30-minute runtime soak. Do not call the full smoke suite passed until this run completes and its logs are inspected.
- The preceding full smoke run [43243672132](https://github.com/grealki/a-desktop/actions/runs/43243672132) reached 1020 PASS / 48 LIMIT / 1 FAIL / 12 SKIP. Its only reported failure was a stale assertion expecting “You are Capri” in a cloud request after the active Azure prompt had changed. Commit `35dedd7` updates the two affected cloud-request expectations to “You are Azure”; the new full smoke run is the validation for that correction.
- This branch's current CI workflow is Windows-only, matching the development focus. Do not spend effort on macOS or Linux unless the user changes that instruction.

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

1. Check full smoke run `43250811762` after its runtime soak completes; inspect all diagnostics and fix only reproducible regressions.
2. Keep legitimate user-selected cloud providers and local AI intact. Do not change provider routing without a reproducible root cause.
3. Keep mod-directory endpoints and unrelated services intact unless the user separately approves a change.
4. Keep development, testing and commits on Windows and `azure-dev` only.
5. Keep Gaming Co-Pilot Mode as a separate future Azure feature: cooperative advice plus user-approved control handoff. It is planned, not implemented.
