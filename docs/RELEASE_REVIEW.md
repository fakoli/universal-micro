# Source preview review

**0.1.0-preview.1 — unpublished review candidate, 2026-11-14.** Canonical target: `fakoli/universal-micro`; license MIT. Publication is withheld for owner review.

## Included

The Windows stdlib router, one added Input layer, browser dispatcher/adapters, narrow public-source patches, immutable source/hash manifest, tests, CI configuration and contributor/operator documentation. No private fork, upstream client tree, runtime binary, credentials, device backup, chat/speech capture or deployment settings are part of the release file list.

## Validation status

Validation is in progress; the final reviewed commit, automated results, fresh archive check and remaining review findings will be recorded here before handoff. Do not interpret this placeholder as a completed release.

The original prototype passed owner-operated physical selectors/actions and native Codex fallback. This candidate retains its own stricter identity/startup behavior and retargets Pi to a public base; that original hardware result is not acceptance evidence for these changes.

## Remaining gates

See [OSS_CHECKLIST.md](../OSS_CHECKLIST.md). Fresh-machine and physical acceptance, actual reboot/sign-in, accessibility, hosted CI and the private vulnerability-reporting channel remain pending. Edge and unpackaged Codex are not live-validated. The browser title/focus checks are convenience safeguards, not a security boundary.

## Planned release notes

- Consistent Dictate, Send, Stop and New chat across three selectable harnesses.
- Native Codex layer retained as fallback; startup opt-in and unique-window reconnection.
- Public pinned Hermes/Pi patch series, with explicit Pi speech configuration and reversible source workflow.
- Windows source preview only. Pi's new public base remains experimental until manual acceptance; no installer, auto-updater or added platforms.

Rollback: disable startup from the owning installation, close/remove the candidate, return to the native Input layer and restore the prior client release if a deployment was separately performed. Preparing this candidate does not deploy it.
