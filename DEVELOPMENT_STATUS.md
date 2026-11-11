# Azure Development Status

Last updated: 2026-11-11

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

## Current build investigation

- Windows CI compiles `app/Capri.cs` directly through `ci/build-windows.ps1`; this is the canonical Windows source, not generated output.
- Linux and macOS CI build `cross/Capri.Cross.csproj` separately.
- Baseline CI on 2026-11-11 at commit `a49a0a401d9b26202197285e629ea0007fbd750d`:
  - Windows failed with `CS1513: } expected` at `app/Capri.cs(47787,10)`.
  - Linux and macOS build/smoke jobs passed.
  - Windows package-marker failure was secondary because the build did not produce the installer.
- The later diagnostic run exposed the underlying Windows source issues:
  - A purchase-confirmation smoke-test `try` block lacked its closing brace before `finally` near line 39327.
  - Two stale `Cloud.Code` references remained in `app/Capri.cs` even though `Cloud.Code` had been removed with legacy access-code support (previously near lines 10506 and 13867).
  - An intermediate repair added a brace in the wrong location before the `StartSmokeTest` catch; that incorrect brace has been removed.
- Corrective source changes are committed to `azure-dev` in commit `677f73d482ed3d24145d6d2a5b72cc13076a95be`:
  - Closed the purchase-confirmation test block before its `finally`.
  - Removed the misplaced brace from `StartSmokeTest`.
  - Removed the two obsolete `remote.Code` branches; they only supported the removed legacy access-code system.
- Static verification after that commit: braces are balanced and no `brain.Remote.Code` / `remote.Code` references remain.
- **A fresh CI run against the corrected source is still required.** The most recent completed Windows run tested the intermediate source and failed; do not describe the corrected build as passing until the new Windows build and smoke test complete.

## Latest Windows CI and focused follow-up (2026-11-11)

- The corrected Windows source compiled successfully in CI, and the separate Windows silent install/uninstall job passed.
- The Windows runtime smoke test reached 889 PASS, 45 LIMIT, 4 FAIL, and 12 SKIP. The four failures were:
  - OpenRouter provider routing/settings assertion in `SmokeCloudBrains` (also failed in the earlier run before the recent access-code cleanup).
  - A stale `SelfKnow` label that still named the old `Things your request didn't mention` setting.
  - A SECURITY preset/privacy assertion in `SmokePrivacy` that still needs investigation.
  - SECURITY window layout overflow on the long fixed-confirmation description (also failed in the earlier run, on the payment row).
- Focused fixes committed on `azure-dev`: shortened the fixed extra-action confirmation description and updated the SelfKnow help topic to match the current fixed safeguard label and behavior.
- Those two focused fixes have not yet been validated by a completed Windows CI run. Do not call the Windows smoke suite passing until that run completes.
- The OpenRouter assertion predates the latest changes and is not yet diagnosed. Preserve provider-specific endpoints, keys, and settings; do not change routing without a reproducible root cause.

## Verified safety implementation observed so far

- `app/Computer.cs`: legacy `Computer.Bypass` is compatibility-only; getter always returns `false` and setter ignores writes.
- `app/Capri.cs`: legacy saved bypass values migrate to a safe Azure/Trusted permissions preset and the old flag is cleared.
- Security smoke tests assert that payments, unrequested actions, and credential entry remain protected, including under the Azure preset.
- `app/Computer.cs` prompts instruct the agent to stop on Windows/antivirus security warnings, not dismiss them or run the file.
- `app/Brain.cs`: legacy Capri access-code strings are rejected; legitimate user-selected provider kinds and local brains remain supported.
- The broader Capri-owned endpoint and actual Windows warning-override audit is not complete. Do not claim either audit is finished.

## Temporary patch mechanism

- The one-off workflow `.github/workflows/temporary-azure-source-patch.yml` and script `ci/patch_azure_source.py` have been removed after applying the focused source correction.
- Do not reintroduce automatic source-rewriting workflows or broad write-permission automation.

## Next tasks

1. Validate the corrected Windows source with a fresh CI run on the latest `azure-dev` head.
2. Inspect Windows build and smoke-test logs; fix only verified regressions.
3. Audit Capri-owned endpoint/access-code references and preserve legitimate user-selected providers and local AI.
4. Audit actual Windows security-warning handling paths, not just prompts; remove any automatic override if present.
5. Keep Gaming Co-Pilot Mode as a separate future Azure feature: cooperative advice plus user-approved control handoff. It is planned, not implemented.
6. Update this file after each meaningful code change and CI result so a new chat can resume accurately.
