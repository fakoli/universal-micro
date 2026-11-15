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
| `node test_transcription.cjs` against public patched Hermes | Pending-fetch cleanup passes; actual upstream capture/stop functions refuse active raw audio after a mode change, pin dictation before permission waits and permit later dictation despite stale idle capture state |
| `node test_pi_voice.cjs` against public patched Pi | Configuration, streamed/declarative body caps, MIME type, sanitized failures, transcript and PCM WAV encoding pass; microphone/browser lifecycle is not exercised |
| Both immutable adapter bases | Check/apply/reverse/reapply pass; source/patch drift and repeat application are refused |
| Public Pi 0.17.0 | `npm ci --ignore-scripts`, production build and TypeScript complete successfully; 73/73 neighboring composer/shortcut tests pass |
| Hermes JavaScript | `node --check static/boot.js` passes |
| Publication guard | 35 allowlisted files; local tree and complete Git history checked for known private operator markers; no ignored client/source/operator files in archive |
| Fresh extracted source archive | Both Python 3.12/3.14 unit runs, browser checks, public-source patch reversal/check/application and both patched voice checks pass without `.git` or retained operator snapshots in the extracted source |
| Preservation check | Original router/launcher/preferences and device map byte hashes match the pre-work snapshot; existing startup value is unchanged |

Python 3.12.15/Tk 8.6 and Python 3.14.8/Tk 9.0 are the locally checked support endpoints. Node is 24.19.0. The Pi build emits an upstream dynamic-dependency warning for its session-export route; compilation and type checking still pass. Node's TypeScript-stripping API prints its experimental warning. No production server was launched for this preparation.

CI YAML and pinned official action references were checked, but hosted CI has **not** run: no project repository has been created/pushed. An extracted archive on the development host is **not** fresh-machine acceptance. A separate fresh public Hermes clone also passed the documented LF checkout, check/apply/transcription/reverse sequence.

## Independent review and fixes

One independent reviewer inspected all 35 public files, six local history trees, source/patch/license hashes, adapter-copy parity and the source archive. It reran the Python and three Node checks. No critical issue was found. One important Hermes defect was reproduced: changing a native raw recording's preference to dictation let Micro Dictate stop that recording through its auto-send path. A related preference change during pending microphone permission could turn a requested dictation into raw capture.

The candidate now checks the active capture mode and snapshots the requested mode before awaiting permission. Regression checks use the actual pinned `_startMicCapture`, `_stopMic`, `_toggleMicCapture` and `_sendRawAudio` bodies and the shipped adapter. Both failures were observed before their respective fixes, then the complete suite passed. There was no second review pass. With subsequent owner approval, the safety change was also applied to the existing modified Hermes client; its actual-source safety regression passed before activation.

**Pi review minor resolved:** Error expiry and a new recording attempt now clear the old banner. Older error timers are cancelled so they cannot clear a newer error early. The actual hook check reproduced the stale banner, then passed expiry, retry, timer ownership and successful dictation recovery. Both the public source candidate and the owner's existing modified Pi client were rebuilt successfully; the existing client's fix was activated with owner approval. The owner then confirmed physical selection, dictation, Send, Stop and New chat passed in both installed browser clients after the fixes. This does not establish physical acceptance of the separate public Pi 0.17.0 base.

Review boundaries and decisions:

1. Public-base physical pad/Input import, microphones, native Codex, accessibility and fresh-machine behavior remain manual publication gates. Windows restart/sign-in validation is now owner-managed follow-up outside this workstream, not a completion blocker. Cost: restart behavior remains unverified until that separate session.
2. Hosted CI and private vulnerability reporting await approved repository setup. Cost: hosted execution and the private reporting channel are not yet demonstrated; publishing must wait.
3. Preservation relies on the executor's original file/device-map byte hashes and registry comparison; the reviewer examined that evidence without repeating private-state collection. Cost: it does not prove a new physical end-to-end run.
4. Review covers shipped changes and relevant client paths, not a full security audit of upstream applications/dependencies. Cost: upstream vulnerabilities may remain outside these checks.

After activation of the Hermes safety and Pi error-recovery fixes, the owner repeated the physical checks on the current installed setup: Hermes, Pi and Codex selection, dictation, Send, Stop and New chat all passed. The native Layer 1 Codex fallback also passed, and the owner was instructed to leave the pad on that layer. These are owner-reported results for the installed modified clients and existing router. The source candidate retains stricter identity/startup behavior and a separate public Pi 0.17.0 base; those still require the documented clean-machine acceptance.

## Remaining gates

See [OSS_CHECKLIST.md](../OSS_CHECKLIST.md). Fresh-machine and public-base physical acceptance, accessibility, hosted CI and the private vulnerability-reporting channel remain pending for publication. The owner will validate Windows restart/sign-in separately; it is not required for completion of this workstream. Edge and unpackaged Codex are not live-validated. The browser title/focus checks are convenience safeguards, not a security boundary.

## Planned release notes

- Consistent Dictate, Send, Stop and New chat across three selectable harnesses.
- Native Codex layer retained as fallback; startup opt-in and unique-window reconnection.
- Public pinned Hermes/Pi patch series, with explicit Pi speech configuration and reversible source workflow.
- Windows source preview only. Pi's new public base remains experimental until manual acceptance; no installer, auto-updater or added platforms.

Rollback: disable startup from the owning installation, close/remove the candidate, return to the native Input layer and restore the prior client release if a deployment was separately performed. Preparing this candidate does not deploy it.
