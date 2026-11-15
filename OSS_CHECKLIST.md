# Open-source readiness

Target: **fakoli/universal-micro**, **MIT**, source preview **0.1.0-preview.1**. This checklist records evidence and release gates; checked boxes do not imply the project has been published. See [release review](docs/RELEASE_REVIEW.md) for exact validation results.

## Prepared for source review

- [x] Owner/repository and MIT approved; public Fakoli commit identity, clean new local Git history and local intended remote configured.
- [x] Separate source repository preserves the installed router and native Input layers; subsequent client fixes were activated with owner approval.
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
- [x] Final independent source review completed; Hermes mode-transition defect and Pi banner recovery issue fixed with failing-then-passing actual-source checks. Fresh archive extraction and publication payload checks passed locally. Owner-approved fixes were also activated in the existing modified clients; public-source physical acceptance remains a compatibility follow-up.

## Source-preview publication

- [x] Owner authorized public publication of the reviewed MIT source preview with its documented limitations.
- [x] Public `fakoli/universal-micro` repository created with issues enabled; private vulnerability reporting enabled and confirmed by API readback.
- [ ] Push the reviewed source and verify MIT detection and public documentation links.
- [ ] Run hosted CI, inspect results and resolve failures. Local checks are not hosted-CI evidence.
- [ ] Tag the source preview and attach the allowlisted source archive/checksum and release notes from its Git tree. No binaries/installer are included.

## Preview validation follow-up

The experimental preview keeps these gaps explicit; they are not claims of completed validation or blockers for the owner-approved source preview.

- [ ] Another person follows the public quickstart on a fresh Windows account/VM and completes [manual compatibility checks](docs/ACCEPTANCE.md), including the public Pi base, keyboard/screen-reader UI checks, physical pad and native fallback.
- [ ] Install/migrate/remove and unchanged unrelated startup/Input state verified in that disposable environment.

## Owner follow-up outside this workstream

The owner will restart Windows and validate sign-in/reconnection in a separate session. This remains unverified; it is not a completion requirement or blocking gate for this workstream. The current implementation and installed-setup physical checks are complete. The owner subsequently authorized source-preview publication.

## Later, on demonstrated demand

- [ ] Packaged/signed executable and installer, including runtime notices and frozen-executable startup handling.
- [ ] Additional harnesses/operating systems with a compatibility owner and integration evidence.
- [ ] Steer/fork, lighting/status, tray controls, firmware support and automatic updates.
