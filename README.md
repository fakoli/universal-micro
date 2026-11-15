# Universal Micro

One Work Louder Codex Micro layer for **Dictate, Send, Stop and New chat** across native Codex, Hermes WebUI and Pi Web. The top buttons select and focus the harness. Your existing native Codex layer remains the fallback.

**Experimental Windows source preview — 0.1.0-preview.1.** See [releases](https://github.com/fakoli/universal-micro/releases), [validation and follow-up](OSS_CHECKLIST.md), and the supported revisions below. Browser support requires those exact patched revisions. Stock clients are not claimed compatible.

## What runs where

- Windows router: Python standard library, Tk and Windows APIs; no listening port, browser extension, network calls or key logging.
- Input: a separate layer emits seven F-keys. Existing layers and firmware are retained.
- Browser adapters: shortcuts invoke each client's composer controls. Hermes uses its existing dictation. Public Pi needs the included dictation prerequisite and an operator-configured speech service.

Speech is recorded and transcribed by the harness, outside the router. Dictation inserts a draft; **Send is a separate action**. No speech provider or credentials are bundled.

## Compatibility

| Component | Preview boundary |
| --- | --- |
| OS | Windows 11 x64; no macOS/Linux router |
| Python | 3.12–3.14 with Tk; local results in [release review](docs/RELEASE_REVIEW.md) |
| Hardware/configurator | Codex Micro, Input 1.1.0; wired USB recommended; export your existing layout first |
| Codex | Store-packaged Codex, verified package family `OpenAI.Codex_2p2nqsd0c76g0`; unpackaged builds are refused |
| Browser | Desktop Chrome; Edge process/title support is present but live acceptance remains unverified |
| Hermes | Public `fakoli/hermes-webui` at `4772f16a95b5b7ad641780b6bd8a6a38f2109fb3` plus controller patch |
| Pi | Public `agegr/pi-web` 0.17.0 at `174bff967807cdb59abb0204198d3d7cc19c862d` plus both ordered patches; experimental pending hardware acceptance |
| Contributor tools | Git and Node 24; Pi build uses its own pinned package lock |

The modified-client setup passed owner-operated hardware acceptance. The new public Pi base has automated/build checks; it still needs the manual pass. Windows restart/sign-in validation is the owner's separate follow-up, outside this workstream's completion requirements, and is not claimed verified. A fresh-machine install also remains unverified.

## Install from source

1. Install Python with Tk, Input, Codex and your configured browser clients. Check `python -m tkinter` opens a test window; close it afterward.
2. Extract the reviewed source archive into a stable, short, user-writable location such as `C:\Tools\UniversalMicro`. Startup points to this exact location and interpreter. Moving either requires disabling startup first and enabling it from the new location.
3. Prepare the browser clients using [the pinned integration instructions](docs/INTEGRATIONS.md). Configure speech before testing dictation. Keep one dedicated browser window for each harness, with that app as the active tab.
4. In Input, **export/back up the current full layout**. Add an unused layer and import `input/Universal-Micro-layer.json` into that layer only. It is a single-layer export. Preserve your native layers; if Input offers to replace the full layout, cancel. Confirm the original layers still appear unchanged.
5. From the extracted folder run `python router.py`. No administrator rights are needed. Optional `Start Router.vbs` uses `pythonw.exe` on PATH; if it cannot find it, use the console command or repair your Python PATH.
6. Open the harness windows. The router discovers a single matching window automatically. When multiple windows match, choose one in its row and click **Bind**. Press the harness's selector to focus it, then use the action keys.

Use your Micro touch sensor to select Universal Micro (typically Layer 3 when two native layers exist). The layer number depends on your device; do not replace an existing layer to force that number.

| Physical position | Key | Action |
| --- | --- | --- |
| Top row, left / right | F13 / F14 | Codex / Hermes |
| Second row, far left | F15 | Pi |
| Third row, first / second | F21 / F22 | Stop / New chat |
| Bottom row, first / second | F19 / F20 | Dictate / Send |

Other keys, encoders and joystick positions in this added layer are unassigned. Press Dictate to start and again to finish; wait for the draft before Send. Stop cancels the agent's run; finish dictation with Dictate. In Hermes select **dictation**, since raw-audio mode can send automatically and is refused by this adapter. In Pi choose a project before New chat.

## Startup and reconnect

Enable **Start at Windows sign-in** in the router. This creates only its per-user `UniversalMicroRouter` Run value, with `--background`; the router opens minimized at sign-in. Windows may delay Run entries. Reopening the launcher restores the existing instance.

Preferences live in `%LOCALAPPDATA%\UniversalMicro\bindings.json`. They save browser/process preferences, not window IDs or chat contents. Missing windows reconnect when a unique matching window appears. After a window or process changes, selection clears: press its harness key again before an action. Ambiguous windows require a choice; closing extra matching windows restores automatic discovery.

An existing startup value pointing to another installation is preserved and cannot be replaced here. Keep using the existing installation until migration is reviewed. To migrate later, disable startup and close the old router first, then launch this one and opt in. Both installations use the same instance lock and F-keys and cannot run together.

## Recovery and removal

Return the Micro to its original native Codex layer with the touch sensor at any time. This path works independently of the router. Close the router to release the seven global keys.

To remove an installation, disable its startup checkbox **from that installation**, close it, and delete its source folder. Optionally delete its `bindings.json` when no other Universal Micro installation uses it. Remove only the added Universal Micro layer in Input; retain your full-layout backup and native layers. Removal does not require changing firmware, other startup programs or browser service configuration. Reverse the client patches separately as documented.

## Troubleshooting and development

See [troubleshooting](docs/TROUBLESHOOTING.md), [manual compatibility checks](docs/ACCEPTANCE.md), [contribution checks](CONTRIBUTING.md), [security/privacy limits](SECURITY.md) and [third-party notices](THIRD_PARTY_NOTICES.md). MIT licensed; no warranty or guaranteed response time. Sanitized bug reports belong in [project issues](https://github.com/fakoli/universal-micro/issues).
