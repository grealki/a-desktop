# Azure Development Status

Last updated: 2026-11-11

## Repository and working rules

- Repository: https://github.com/grealki/a-desktop
- Active branch: `azure-dev` only.
- The upstream repository must never be modified.
- Do not merge into `main`, publish releases, or distribute builds.
- Inspect before changing; preserve unrelated functionality.
- Approved cleanup scope:
  1. Permanently disable unrestricted Blackwall permission bypass.
  2. Replace Capri-owned AI endpoints/access-code integration with Azure configuration while preserving legitimate user-selected providers and local AI.
  3. Remove automatic Windows security-warning override / “Run anyway” behavior.

## Current build investigation

- Windows build uses `ci/build-windows.ps1`, which compiles `app/Capri.cs` directly. This is the canonical Windows source file, not generated output.
- Linux and macOS CI build `cross/Capri.Cross.csproj` separately.
- Latest completed CI before the current fix (2026-11-11, commit `a49a0a401d9b26202197285e629ea0007fbd750d`):
  - Windows compilation failed with `CS1513: } expected` at `app/Capri.cs(47787,10)`.
  - Linux and macOS build/smoke jobs passed.
  - The Windows package-marker step failed secondarily because the failed build did not produce the installer.
- Root cause found in `StartSmokeTest`: the `else if (step == 1)` block was closed, but the surrounding `try` block was not closed before its `catch`.
- A single closing brace was inserted immediately before that `catch`. The source correction was committed to `azure-dev` as `27bb7ac601b51217eba5cc8d787d5fe252180384`.
- **Validation is pending.** The CI run created for the preceding temporary-script commit may still test the pre-fix source. A fresh CI run must validate the source-fix commit or a later commit containing it.

## Verified safety implementation observed so far

- `app/Computer.cs`: legacy `Computer.Bypass` is compatibility-only; getter always returns `false` and setter ignores writes.
- `app/Capri.cs`: legacy saved bypass values are migrated to a safe Azure/Trusted permissions preset and the old flag is cleared.
- Security smoke tests assert that payments, unrequested actions, and credential entry remain protected, including under the Azure preset.
- `app/Computer.cs` prompts instruct the agent to stop on Windows/antivirus security warnings, not dismiss them or run the file.
- `app/Brain.cs`: legacy Capri access-code strings are rejected; legitimate provider kinds and local brains remain supported.
- The broader endpoint and warning-override audit is not yet complete. Do not claim those audits are finished.

## Temporary patch mechanism

- The temporary workflow `.github/workflows/temporary-azure-source-patch.yml` had `contents: write` permission and pushed source edits automatically.
- Its original 64 KB patch script was stale and failed because its expected legacy source snippet no longer existed.
- It was used once with a narrowed, exact-match brace correction. Remove the temporary workflow and its script now that the source edit is committed; do not keep an automatic source-rewriting workflow.

## Next tasks

1. Validate the corrected Windows source with a fresh CI run on a commit containing `27bb7ac`.
2. Inspect Windows build and smoke-test logs; fix only verified regressions.
3. Audit all Capri-owned endpoint/access-code references and preserve user-selected providers/local AI.
4. Audit the actual Windows security-warning handling paths, not just prompts; remove any automatic override if present.
5. Keep the optional Gaming Co-Pilot Mode as a separate future Azure feature: cooperative advice plus user-approved control handoff. It is planned, not implemented.
6. Update this file after each meaningful code change and CI result so a new chat can resume accurately.
