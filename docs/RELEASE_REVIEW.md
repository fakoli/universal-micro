# Source preview review

**0.1.0-preview.1 — unpublished review candidate, 2026-11-14.** Canonical target: `fakoli/universal-micro`; license MIT. Publication is withheld for owner review.

## Included

The Windows stdlib router, one added Input layer, browser dispatcher/adapters, narrow public-source patches, immutable source/hash manifest, tests, CI configuration and contributor/operator documentation. No private fork, upstream client tree, runtime binary, credentials, device backup, chat/speech capture or deployment settings are part of the release file list.

## Validation status

Local validation on Windows 11 x64:

| Check | Result |
| --- | --- |
| `python -m unittest discover` | 13/13 pass on Python 3.12, 3.13 and 3.14; includes real isolated Windows mutex/Tk message delivery, fake registry ownership and disposable Git/archive checks |
| `node test_web_controller.cjs` | Both adapters and focus/modal/IME/recording/raw-audio/duplicate/error guards pass |
| `node test_transcription.cjs` against public patched Hermes | Busy state spans pending fetch and clears after success/error |
| `node test_pi_voice.cjs` against public patched Pi | Configuration, streamed/declarative body caps, MIME type, sanitized failures, transcript and PCM WAV encoding pass; microphone/browser lifecycle is not exercised |
| Both immutable adapter bases | Check/apply/reverse/reapply pass; source/patch drift and repeat application are refused |
| Public Pi 0.17.0 | `npm ci --ignore-scripts`, production build and TypeScript complete successfully; 73/73 neighboring composer/shortcut tests pass |
| Hermes JavaScript | `node --check static/boot.js` passes |
| Publication guard | 35 allowlisted files; local tree and complete Git history checked for known private operator markers; no ignored client/source/operator files in archive |
| Fresh extracted source archive | Both Python 3.12/3.14 unit runs, browser checks, public-source patch reversal/check/application and both patched voice checks pass without `.git` or retained operator snapshots in the extracted source |
| Preservation check | Original router/launcher/preferences and device map byte hashes match the pre-work snapshot; existing startup value is unchanged |

Python 3.12.15/Tk 8.6 and Python 3.14.8/Tk 9.0 are the locally checked support endpoints. Node is 24.19.0. The Pi build emits an upstream dynamic-dependency warning for its session-export route; compilation and type checking still pass. Node's TypeScript-stripping API prints its experimental warning. No production server was launched for this preparation.

CI YAML and pinned official action references were checked, but hosted CI has **not** run: no project repository has been created/pushed. An extracted archive on the development host is **not** fresh-machine acceptance. Final independent source-review findings will be recorded before handoff.

The original prototype passed owner-operated physical selectors/actions and native Codex fallback. This candidate retains its own stricter identity/startup behavior and retargets Pi to a public base; that original hardware result is not acceptance evidence for these changes.

## Remaining gates

See [OSS_CHECKLIST.md](../OSS_CHECKLIST.md). Fresh-machine and physical acceptance, actual reboot/sign-in, accessibility, hosted CI and the private vulnerability-reporting channel remain pending. Edge and unpackaged Codex are not live-validated. The browser title/focus checks are convenience safeguards, not a security boundary.

## Planned release notes

- Consistent Dictate, Send, Stop and New chat across three selectable harnesses.
- Native Codex layer retained as fallback; startup opt-in and unique-window reconnection.
- Public pinned Hermes/Pi patch series, with explicit Pi speech configuration and reversible source workflow.
- Windows source preview only. Pi's new public base remains experimental until manual acceptance; no installer, auto-updater or added platforms.

Rollback: disable startup from the owning installation, close/remove the candidate, return to the native Input layer and restore the prior client release if a deployment was separately performed. Preparing this candidate does not deploy it.
