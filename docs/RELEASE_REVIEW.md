# Source preview review

## 0.2.0-preview.1 — configurable apps and Claude

**Experimental Windows source preview, 2026-11-15.** Adds an Apps & shortcuts editor, local app/window profiles, configurable F13–F24 selectors/actions and per-app native shortcuts. Claude desktop uses F16, Ctrl+D, Enter, Escape and Ctrl+N by default. Existing Codex/Hermes/Pi keys and the independent native Codex layer remain intact. Browser patches and their pinned revisions are unchanged from the prior preview.

| Check | Result |
| --- | --- |
| Python 3.12.15 and 3.14.8 | 18/18 tests pass on both; includes custom window/action routing, persistence, invalid profiles, no-clobber oversized saves, registration collision/save-failure rollback and existing Windows safety checks |
| Browser/controller checks | Web controller, public patched Hermes transcription/capture safety and public patched Pi speech/banner checks pass |
| Independent feature review | Accepted after fixes for oversized profile saves, serialization-error rollback and restoring the editor's modal grab; reviewer independently reran targeted tests and disposable save-failure probes |
| Installed source and persistence | Installed runtime matches reviewed source; profiles reload successfully; original startup entry and executable preferences preserved |
| Device preservation | Full-layout structural comparison found only the intended third-layer `KC_NONE` to `KC_F16` change; both native layers and all seven existing universal assignments are unchanged |
| Physical acceptance | Owner reports Claude selection, dictation, Send, Stop and New chat passed; native Codex Layer 1 fallback also passed |
| Publication payload | Explicit 38-file source allowlist; private profile/device/recovery files remain excluded |

The physical result applies to the owner's installed setup, not a fresh-machine qualification. Public Pi base, accessibility and fresh Windows acceptance remain follow-up as below. Windows restart/sign-in is owner-managed in a separate session and is outside this workstream's completion requirements. No restart result is claimed. Hosted checks for the published commit are available in [GitHub Actions](https://github.com/fakoli/universal-micro/actions/workflows/checks.yml).

Upgrade and recovery: keep the installation folder and startup entry, include `profiles.py` alongside `router.py`, preserve per-user settings, and add only F16 to the unused universal-layer button. Back up the old source/layout first. Returning to the native Input layer remains independent of this router. For source rollback, restore the previous router files after closing the router; the previous version ignores F16. See [profiles](PROFILES.md) and the [README](../README.md).

## Previous release: 0.1.0-preview.1

**0.1.0-preview.1 — experimental source preview, 2026-11-14.** Repository: [fakoli/universal-micro](https://github.com/fakoli/universal-micro); license MIT. The owner authorized publication with the compatibility limits below.

## Included

The Windows stdlib router, one added Input layer, browser dispatcher/adapters, narrow public-source patches, immutable source/hash manifest, tests, CI configuration and contributor/operator documentation. No private fork, upstream client tree, runtime binary, credentials, device backup, chat/speech capture or deployment settings are part of the release file list.

## Validation status

Local validation on Windows 11 x64:

| Check | Result |
| --- | --- |
| `python -m unittest discover` | 13/13 pass on Python 3.12, 3.13 and 3.14; includes real isolated Windows mutex/Tk message delivery, fake registry ownership and disposable Git/archive checks |
| `node test_web_controller.cjs` | Both adapters and focus/modal/IME/recording/raw-audio/duplicate/error guards pass |
| `node test_transcription.cjs` against public patched Hermes | Pending-fetch cleanup passes; actual upstream capture/stop functions refuse active raw audio after a mode change, pin dictation before permission waits and permit later dictation despite stale idle capture state |
| `node test_pi_voice.cjs` against public patched Pi | Configuration, streamed/declarative body caps, MIME type, sanitized failures, transcript and PCM WAV encoding pass; microphone/browser lifecycle is not exercised |
| Both immutable adapter bases | Check/apply/reverse/reapply pass; source/patch drift and repeat application are refused |
| Public Pi 0.17.0 | `npm ci --ignore-scripts`, production build and TypeScript complete successfully; 73/73 neighboring composer/shortcut tests pass |
| Hermes JavaScript | `node --check static/boot.js` passes |
| Publication guard | 35 allowlisted files; local tree and complete Git history checked for known private operator markers; no ignored client/source/operator files in archive |
| Fresh extracted source archive | Both Python 3.12/3.14 unit runs, browser checks, public-source patch reversal/check/application and both patched voice checks pass without `.git` or retained operator snapshots in the extracted source |
| Preservation check | Original router/launcher/preferences and device map byte hashes match the pre-work snapshot; existing startup value is unchanged |

Python 3.12.15/Tk 8.6 and Python 3.14.8/Tk 9.0 are the locally checked support endpoints. Node is 24.19.0. The Pi build emits an upstream dynamic-dependency warning for its session-export route; compilation and type checking still pass. Node's TypeScript-stripping API prints its experimental warning. No production server was launched for this preparation.

Hosted [CI passed](https://github.com/fakoli/universal-micro/actions/runs/43688763984) on Windows Python 3.12/3.14 and Ubuntu for the public-source adapter apply/reverse, voice checks, Pi build and 73 neighboring tests. Current runs are listed in [GitHub Actions](https://github.com/fakoli/universal-micro/actions/workflows/checks.yml). An extracted archive on the development host is **not** fresh-machine acceptance. A separate fresh public Hermes clone also passed the documented LF checkout, check/apply/transcription/reverse sequence.

## Independent review and fixes

One independent reviewer inspected all 35 public files, six local history trees, source/patch/license hashes, adapter-copy parity and the source archive. It reran the Python and three Node checks. No critical issue was found. One important Hermes defect was reproduced: changing a native raw recording's preference to dictation let Micro Dictate stop that recording through its auto-send path. A related preference change during pending microphone permission could turn a requested dictation into raw capture.

The candidate now checks the active capture mode and snapshots the requested mode before awaiting permission. Regression checks use the actual pinned `_startMicCapture`, `_stopMic`, `_toggleMicCapture` and `_sendRawAudio` bodies and the shipped adapter. Both failures were observed before their respective fixes, then the complete suite passed. There was no second review pass. With subsequent owner approval, the safety change was also applied to the existing modified Hermes client; its actual-source safety regression passed before activation.

**Pi review minor resolved:** Error expiry and a new recording attempt now clear the old banner. Older error timers are cancelled so they cannot clear a newer error early. The actual hook check reproduced the stale banner, then passed expiry, retry, timer ownership and successful dictation recovery. Both the public source candidate and the owner's existing modified Pi client were rebuilt successfully; the existing client's fix was activated with owner approval. The owner then confirmed physical selection, dictation, Send, Stop and New chat passed in both installed browser clients after the fixes. This does not establish physical acceptance of the separate public Pi 0.17.0 base.

Review boundaries and decisions:

1. Public-base physical pad/Input import, microphones, native Codex, accessibility and fresh-machine behavior remain compatibility follow-up. Windows restart/sign-in validation is owner-managed follow-up outside this workstream, not a completion blocker. Cost: restart behavior remains unverified until that separate session.
2. Private vulnerability reporting is enabled and confirmed by API readback; hosted CI is tracked in the publication checklist. A report was not filed to test the reporter's end-to-end authentication flow.
3. Preservation relies on the executor's original file/device-map byte hashes and registry comparison; the reviewer examined that evidence without repeating private-state collection. The owner's subsequent installed-hardware results are recorded below; the reviewer did not independently reproduce them.
4. Review covers shipped changes and relevant client paths, not a full security audit of upstream applications/dependencies. Cost: upstream vulnerabilities may remain outside these checks.

After activation of the Hermes safety and Pi error-recovery fixes, the owner repeated the physical checks on the current installed setup: Hermes, Pi and Codex selection, dictation, Send, Stop and New chat all passed. The native Layer 1 Codex fallback also passed, and the owner was instructed to leave the pad on that layer. These are owner-reported results for the installed modified clients and existing router. The source candidate retains stricter identity/startup behavior and a separate public Pi 0.17.0 base; those still require the documented clean-machine acceptance.

## Preview limitations and follow-up

See [OSS_CHECKLIST.md](../OSS_CHECKLIST.md). Fresh-machine and public-base physical acceptance and accessibility remain follow-up. The owner will validate Windows restart/sign-in separately; it is not required for completion of this workstream. Edge is not live-validated; unpackaged Codex is unsupported. The browser title/focus checks are convenience safeguards, not a security boundary.

## Planned release notes

- Consistent Dictate, Send, Stop and New chat across three selectable harnesses.
- Native Codex layer retained as fallback; startup opt-in and unique-window reconnection.
- Public pinned Hermes/Pi patch series, with explicit Pi speech configuration and reversible source workflow.
- Windows source preview only. Pi's new public base remains experimental until manual acceptance; no installer, auto-updater or added platforms.

Rollback: disable startup from the owning installation, close/remove the candidate, return to the native Input layer and restore the prior client release if a deployment was separately performed. Preparing this candidate does not deploy it.
