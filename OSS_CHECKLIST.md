# Open-source readiness

Target: **fakoli/universal-micro**, **MIT**, source preview **0.1.0-preview.1**. This checklist records evidence and release gates; checked boxes do not imply the project has been published. See [release review](docs/RELEASE_REVIEW.md) for exact validation results.

## Prepared for source review

- [x] Owner/repository and MIT approved; public Fakoli commit identity, clean new local Git history and local intended remote configured.
- [x] Separate candidate preserves the running installation; no deployed client, registry entry or Input layer migration is performed by this work.
- [x] Project LICENSE and upstream MIT notices retained; no client application/runtime/firmware bundle.
- [x] Explicit public-file allowlist, source/archive checker and ignore rules exclude operator state and full upstream source trees.
- [x] Generic README, button map, compatibility limits, installation/removal/recovery and startup migration guide; no real-chat screenshots or deployment examples.
- [x] Store-package Codex identity, process lifetime/foreground revalidation, ambiguity refusal and background-error reporting; test registration uses isolated OS objects and never owns physical F-keys.
- [x] Startup management refuses another installation's Run entry; state is outside the source tree in per-user application data.
- [x] Public immutable source manifest with original/patched-file, license and ordered-patch SHA-256 records; no private fork dependency.
- [x] Narrow Pi dictation prerequisite against public 0.17.0; no vendored client or chosen speech provider/model.
- [x] Public-source apply/reverse/reapply, drift/repeat/tamper checks and browser/voice regression checks.
- [x] Pi client build and relevant neighboring tests; Hermes JavaScript syntax and pending-transcription cleanup checks.
- [x] Source installation/version metadata, contributor/support instructions, sanitized issue/PR templates and security/privacy documentation.
- [x] Windows Python matrix and public-adapter CI configured with immutable action pins, read-only repository permissions and no private credentials.
- [x] Final independent source review completed; important Hermes mode-transition defect fixed with failing-then-passing actual-source checks; one minor Pi banner issue documented. Fresh archive extraction and publication payload checks passed locally.

## Publication gates — deliberately pending

- [ ] Maintainer reviews the exact local branch/archive, support claims, provenance, remaining limitations and independent review results.
- [ ] Another person follows the public quickstart on a fresh Windows account/VM and completes [manual acceptance](docs/ACCEPTANCE.md), including the new public Pi base, keyboard/screen-reader UI checks, physical pad and native fallback.
- [ ] Actual Windows sign-in/reboot, install/migrate/remove and unchanged unrelated startup/Input state verified in that disposable environment.
- [ ] Owner authorizes publication. Create the public repository, confirm MIT detection/description/support links, enable and test private vulnerability reporting. No working reporting route is claimed before that setup.
- [ ] Run hosted CI after the approved push, inspect results and resolve failures. Workflow configuration and local checks are not hosted-CI evidence.
- [ ] Only after the gates pass, tag the source preview and attach archive/checksum/release notes from the reviewed Git tree. No binaries/installer are included.

## Later, on demonstrated demand

- [ ] Packaged/signed executable and installer, including runtime notices and frozen-executable startup handling.
- [ ] Additional harnesses/operating systems with a compatibility owner and integration evidence.
- [ ] Steer/fork, lighting/status, tray controls, firmware support and automatic updates.
